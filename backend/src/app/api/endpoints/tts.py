from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
import os
import hashlib
import base64
from pathlib import Path
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.paths import ensure_storage_directories

router = APIRouter(tags=["tts"])

class TTSRequest(BaseModel):
    text: str
    language: str | None = "English"

AUDIO_CACHE_DIR = settings.AUDIO_ROOT
ensure_storage_directories()

_TTS_VOICES: dict[str, dict[str, str]] = {
    "hi": {"languageCode": "hi-IN", "name": "hi-IN-Standard-A"},
    "gu": {"languageCode": "gu-IN", "name": "gu-IN-Standard-A"},
    "en": {"languageCode": "en-IN", "name": "en-IN-Standard-A"},
}


def _resolve_tts_voice(language: str | None) -> dict[str, str]:
    if not language:
        return _TTS_VOICES["en"]
    clean = language.strip().lower()
    if clean.startswith("hi"):
        return _TTS_VOICES["hi"]
    if clean.startswith("gu"):
        return _TTS_VOICES["gu"]
    return _TTS_VOICES["en"]


@router.post("/tts")
async def generate_tts(payload: TTSRequest, user_id: str = Depends(get_current_user)):
    AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    voice_cfg = _resolve_tts_voice(payload.language)
    lang_code = voice_cfg["languageCode"]

    # 1. Check cache (partitioned by voice language + text)
    text_hash = hashlib.sha256(f"{lang_code}:{payload.text}".encode("utf-8")).hexdigest()
    cache_file = AUDIO_CACHE_DIR / f"{text_hash}.mp3"
    
    if cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                audio_bytes = f.read()
                b64_encoded = base64.b64encode(audio_bytes).decode('utf-8')
                return {"audioContent": b64_encoded, "cached": True}
        except Exception:
            pass

    # 2. Generate if not cached
    api_key = settings.GOOGLE_TTS_API_KEY or os.getenv("GOOGLE_TTS_API_KEY")
    if not api_key:
        raise HTTPException(status_code=503, detail="TTS API key not configured on server")
        
    url = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={api_key}"
    
    data = {
        "input": {"text": payload.text},
        "voice": voice_cfg,
        "audioConfig": {"audioEncoding": "MP3"}
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(url, json=data)
            
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=f"TTS Provider Error: {resp.text}")
            
        result = resp.json()
        b64_audio = result.get("audioContent")
        
        if b64_audio:
            # Save to cache
            audio_bytes = base64.b64decode(b64_audio)
            with open(cache_file, "wb") as f:
                f.write(audio_bytes)
                
        return {"audioContent": b64_audio, "cached": False}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"TTS synthesis failed: {exc}")
