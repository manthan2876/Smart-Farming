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

AUDIO_CACHE_DIR = settings.AUDIO_ROOT
ensure_storage_directories()

@router.post("/tts")
async def generate_tts(payload: TTSRequest, user_id: str = Depends(get_current_user)):
    AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Check cache
    text_hash = hashlib.sha256(payload.text.encode('utf-8')).hexdigest()
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
        "voice": {"languageCode": "en-US", "name": "en-US-Standard-A"},
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
