from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
import os
import hashlib
import base64
import logging
from pathlib import Path
from app.api.deps import get_current_user
from app.core.config import settings
from app.core.paths import ensure_storage_directories
from app.core.storage import get_storage

logger = logging.getLogger("smart-farming.tts")

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


def sync_existing_audio_to_storage() -> dict[str, int]:
    """Uploads any existing local audio files in AUDIO_CACHE_DIR to the active storage backend (e.g. AWS S3)."""
    storage = get_storage()
    synced = 0
    skipped = 0
    if not AUDIO_CACHE_DIR.exists():
        return {"synced": 0, "skipped": 0}

    for file_path in AUDIO_CACHE_DIR.glob("*.mp3"):
        if file_path.is_file():
            storage_key = f"audio/{file_path.name}"
            try:
                if not storage.exists(storage_key):
                    data = file_path.read_bytes()
                    storage.save(data, storage_key, content_type="audio/mpeg")
                    synced += 1
                    logger.info("Uploaded local audio %s to storage backend (%s)", file_path.name, storage_key)
                else:
                    skipped += 1
            except Exception as exc:
                logger.warning("Failed to sync %s to storage backend: %s", file_path.name, exc)
    return {"synced": synced, "skipped": skipped}


@router.post("/tts")
async def generate_tts(payload: TTSRequest, user_id: str = Depends(get_current_user)):
    AUDIO_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    storage = get_storage()

    voice_cfg = _resolve_tts_voice(payload.language)
    lang_code = voice_cfg["languageCode"]

    # 1. Determine key and cache paths (partitioned by voice language + text)
    text_hash = hashlib.sha256(f"{lang_code}:{payload.text}".encode("utf-8")).hexdigest()
    cache_file = AUDIO_CACHE_DIR / f"{text_hash}.mp3"
    storage_key = f"audio/{text_hash}.mp3"

    audio_bytes: bytes | None = None

    # Step 1A: Check local disk cache
    if cache_file.exists():
        try:
            audio_bytes = cache_file.read_bytes()
        except Exception as exc:
            logger.warning("Failed to read local audio cache %s: %s", cache_file, exc)
            audio_bytes = None

    # Step 1B: If not found on local disk, check storage backend (e.g. AWS S3)
    if not audio_bytes:
        try:
            if storage.exists(storage_key):
                audio_bytes = storage.get(storage_key)
                # Populate local disk cache for fast future retrieval
                try:
                    cache_file.write_bytes(audio_bytes)
                except Exception as exc:
                    logger.warning("Failed to populate local audio cache %s: %s", cache_file, exc)
        except Exception as exc:
            logger.warning("Error checking storage backend for audio key %s: %s", storage_key, exc)

    # If cached audio was found:
    if audio_bytes:
        # Ensure S3 / object storage also has this file in case it was only saved locally previously
        try:
            if not storage.exists(storage_key):
                storage.save(audio_bytes, storage_key, content_type="audio/mpeg")
                logger.info("Synced previously cached audio %s to storage backend", storage_key)
        except Exception as exc:
            logger.warning("Failed to sync cached audio to storage backend %s: %s", storage_key, exc)

        b64_encoded = base64.b64encode(audio_bytes).decode("utf-8")
        return {"audioContent": b64_encoded, "cached": True}

    # 2. Generate via Google TTS if not cached in local or object storage
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
            audio_bytes = base64.b64decode(b64_audio)

            # 1. Save to local disk cache
            try:
                cache_file.write_bytes(audio_bytes)
            except Exception as exc:
                logger.warning("Failed to write local audio cache file %s: %s", cache_file, exc)

            # 2. Save to configured storage backend (AWS S3)
            try:
                storage.save(audio_bytes, storage_key, content_type="audio/mpeg")
                logger.info("Successfully uploaded new audio file to storage backend: %s", storage_key)
            except Exception as exc:
                logger.error("Failed to upload audio file to storage backend %s: %s", storage_key, exc)

        return {"audioContent": b64_audio, "cached": False}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"TTS synthesis failed: {exc}")
