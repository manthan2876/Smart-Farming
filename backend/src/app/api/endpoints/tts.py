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

SUPPORTED_LANGUAGES: dict[str, str] = {
    "hi": "Hindi",
    "gu": "Gujarati",
    "en": "Indian English",
}


def _resolve_tts_language(language: str | None) -> str:
    if not language:
        return "en"
    clean = language.strip().lower()
    if clean.startswith("hi"):
        return "hi"
    if clean.startswith("gu"):
        return "gu"
    return "en"


def sync_existing_audio_to_storage() -> dict[str, int]:
    """Uploads any existing local audio files in AUDIO_CACHE_DIR to the active storage backend (e.g. AWS S3)."""
    storage = get_storage()
    synced = 0
    skipped = 0
    if not AUDIO_CACHE_DIR.exists():
        return {"synced": 0, "skipped": 0}

    for file_path in AUDIO_CACHE_DIR.glob("*.*"):
        if file_path.is_file() and file_path.suffix in {".wav", ".mp3"}:
            storage_key = f"audio/{file_path.name}"
            content_type = "audio/wav" if file_path.suffix == ".wav" else "audio/mpeg"
            try:
                if not storage.exists(storage_key):
                    data = file_path.read_bytes()
                    storage.save(data, storage_key, content_type=content_type)
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

    cleaned_text = (payload.text or "").strip()
    import re
    if not cleaned_text or not re.search(r"[\w\u0900-\u097F\u0A80-\u0AFF]", cleaned_text):
        raise HTTPException(
            status_code=400,
            detail="Text must contain speakable words to generate audio."
        )

    lang = _resolve_tts_language(payload.language)

    # 1. Determine key and cache paths (partitioned by language + text)
    text_hash = hashlib.sha256(f"{lang}:{cleaned_text}".encode("utf-8")).hexdigest()
    cache_file = AUDIO_CACHE_DIR / f"{text_hash}.wav"
    storage_key = f"audio/{text_hash}.wav"

    audio_bytes: bytes | None = None

    # Step 1A: Check local disk cache (wav first, then legacy mp3)
    for candidate in [cache_file, AUDIO_CACHE_DIR / f"{text_hash}.mp3"]:
        if candidate.exists():
            try:
                audio_bytes = candidate.read_bytes()
                break
            except Exception as exc:
                logger.warning("Failed to read local audio cache %s: %s", candidate, exc)

    # Step 1B: If not found on local disk, check storage backend (e.g. AWS S3)
    if not audio_bytes:
        for candidate_key in [storage_key, f"audio/{text_hash}.mp3"]:
            try:
                if storage.exists(candidate_key):
                    audio_bytes = storage.get(candidate_key)
                    # Populate local disk cache for fast future retrieval
                    try:
                        cache_file.write_bytes(audio_bytes)
                    except Exception as exc:
                        logger.warning("Failed to populate local audio cache %s: %s", cache_file, exc)
                    break
            except Exception as exc:
                logger.warning("Error checking storage backend for audio key %s: %s", candidate_key, exc)

    # If cached audio was found:
    if audio_bytes:
        try:
            if not storage.exists(storage_key):
                storage.save(audio_bytes, storage_key, content_type="audio/wav")
                logger.info("Synced previously cached audio %s to storage backend", storage_key)
        except Exception as exc:
            logger.warning("Failed to sync cached audio to storage backend %s: %s", storage_key, exc)

        b64_encoded = base64.b64encode(audio_bytes).decode("utf-8")
        return {"audioContent": b64_encoded, "format": "wav", "cached": True}

    # 2. Generate via AI4Bharat Indic-TTS service
    tts_url = (settings.TTS_SERVER_URL or os.getenv("TTS_SERVER_URL") or "").rstrip("/")
    if not tts_url:
        raise HTTPException(
            status_code=503,
            detail="TTS service is not configured. Set TTS_SERVER_URL to the Indic-TTS service or Cloudflare Gateway."
        )

    headers = {"Content-Type": "application/json"}
    if settings.GATEWAY_API_KEY:
        headers["Authorization"] = f"Bearer {settings.GATEWAY_API_KEY}"

    data = {
        "text": cleaned_text,
        "language": lang,
        "speaker": "female",
    }

    try:
        timeout = httpx.Timeout(settings.TTS_SERVER_TIMEOUT)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # First try /tts/synthesize (returns JSON with base64 audioContent)
            synthesize_url = f"{tts_url}/tts/synthesize" if not tts_url.endswith("/tts") else f"{tts_url}/synthesize"
            resp = await client.post(synthesize_url, json=data, headers=headers)

            if resp.status_code == 200:
                result = resp.json()
                b64_audio = result.get("audioContent")
                if not b64_audio:
                    raise RuntimeError("TTS service returned empty audio content")
                audio_bytes = base64.b64decode(b64_audio)
            elif resp.status_code == 404:
                resp_text = resp.text
                if "Unknown service route" in resp_text:
                    raise HTTPException(
                        status_code=502,
                        detail=(
                            "Cloudflare Worker Gateway has not been deployed with the /tts route yet. "
                            "Please deploy the updated worker by running 'npx wrangler deploy' in the cloudflare_gateway folder."
                        ),
                    )
                # Fallback to direct raw audio endpoint POST /tts
                direct_url = f"{tts_url}/tts" if not tts_url.endswith("/tts") else tts_url
                resp_direct = await client.post(direct_url, json=data, headers=headers)
                if resp_direct.status_code == 200:
                    audio_bytes = resp_direct.content
                    b64_audio = base64.b64encode(audio_bytes).decode("utf-8")
                else:
                    raise HTTPException(
                        status_code=502,
                        detail=f"Indic-TTS upstream error ({resp_direct.status_code}): {resp_direct.text}",
                    )
            elif resp.status_code == 503 and "TTS_URL" in resp.text:
                raise HTTPException(
                    status_code=503,
                    detail=(
                        "Indic-TTS service is currently offline. Please run Notebook 3 "
                        "(03_indic_tts_cloudflare.ipynb) on Colab to start the model and populate TTS_URL."
                    ),
                )
            else:
                raise HTTPException(
                    status_code=502,
                    detail=f"Indic-TTS upstream error ({resp.status_code}): {resp.text}",
                )

        if audio_bytes:
            # 1. Save to local disk cache
            try:
                cache_file.write_bytes(audio_bytes)
            except Exception as exc:
                logger.warning("Failed to write local audio cache file %s: %s", cache_file, exc)

            # 2. Save to configured storage backend (AWS S3)
            try:
                storage.save(audio_bytes, storage_key, content_type="audio/wav")
                logger.info("Successfully uploaded new audio file to storage backend: %s", storage_key)
            except Exception as exc:
                logger.error("Failed to upload audio file to storage backend %s: %s", storage_key, exc)

        return {"audioContent": b64_audio, "format": "wav", "cached": False}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Indic-TTS synthesis failed: {exc}")
