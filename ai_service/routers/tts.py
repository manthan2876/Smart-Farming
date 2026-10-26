"""
ai_service/routers/tts.py — Text-to-Speech (TTS) API router.
Supports high-definition Indian regional voices (Gujarati, Hindi, English)
using Microsoft Neural Speech (edge-tts) with AI4Bharat Indic-TTS local fallback.
"""

from __future__ import annotations

import base64
import io
import logging
import os
import re
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

VOICE_MAP = {
    "gu": {
        "female": "gu-IN-DhwaniNeural",
        "male": "gu-IN-NiranjanNeural",
    },
    "hi": {
        "female": "hi-IN-SwaraNeural",
        "male": "hi-IN-MadhurNeural",
    },
    "en": {
        "female": "en-IN-NeerjaNeural",
        "male": "en-IN-PrabhatNeural",
    },
}

DEFAULT_VOICE = {
    "gu": "gu-IN-DhwaniNeural",
    "hi": "hi-IN-SwaraNeural",
    "en": "en-IN-NeerjaNeural",
}


def _clean_text_for_speech(text: str) -> str:
    """Prepares text for natural speech synthesis."""
    if not text:
        return ""
    # Strip markdown markers, bullets, and excessive spaces
    t = re.sub(r"[\*\_#`]", "", text)
    t = re.sub(r"\[.*?\]\(.*?\)", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


async def _synthesize_edge_tts(text: str, voice_name: str) -> bytes:
    """Synthesizes high-fidelity speech via edge-tts."""
    import edge_tts

    communicate = edge_tts.Communicate(text, voice_name)
    audio_buffer = bytearray()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.extend(chunk["data"])
    return bytes(audio_buffer)


class TTSRequest(BaseModel):
    text: str
    language: str = "gu"
    speaker: Optional[str] = "female"


@router.get("/health")
def tts_health():
    return {
        "status": "healthy",
        "service": "neural_indic_tts",
        "engine": "edge-tts (Microsoft Neural) + Indic-TTS fallback",
        "supported_languages": list(VOICE_MAP.keys()),
    }


@router.post("/synthesize")
@router.post("/tts/synthesize")
async def synthesize_speech(req: TTSRequest):
    cleaned = _clean_text_for_speech(req.text)
    if not cleaned:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text for speech synthesis cannot be empty.",
        )

    lang = req.language.lower().strip()
    if lang not in VOICE_MAP:
        lang = "en"

    speaker = (req.speaker or "female").lower().strip()
    voice = VOICE_MAP[lang].get(speaker, DEFAULT_VOICE[lang])

    # 1. Primary: High-fidelity Neural Speech
    try:
        audio_bytes = await _synthesize_edge_tts(cleaned, voice)
        if audio_bytes and len(audio_bytes) > 100:
            b64_audio = base64.b64encode(audio_bytes).decode("ascii")
            return {
                "audioContent": b64_audio,
                "format": "mp3",
                "voice": voice,
                "language": lang,
            }
    except Exception as exc:
        logger.warning("Primary neural synthesis failed: %s. Attempting fallback...", exc)

    # 2. Fallback: Local Indic-TTS (if checkpoints are installed)
    try:
        from TTS.utils.synthesizer import Synthesizer
        safe_lang = os.path.basename(lang)
        if safe_lang.isalnum():
            base_cp = os.path.abspath("/content/checkpoints")
            cp_dir = os.path.abspath(os.path.join(base_cp, safe_lang))
            if cp_dir.startswith(base_cp + os.sep) and os.path.isdir(cp_dir):
                acoustic = os.path.join(cp_dir, "fastpitch", "best_model.pth")
                config = os.path.join(cp_dir, "fastpitch", "config_local.json")
                if os.path.isfile(acoustic) and os.path.isfile(config):
                    syn = Synthesizer(acoustic, config, None, None, use_cuda=settings.DEVICE == "cuda")
                    wav = syn.tts(cleaned)
                    buf = io.BytesIO()
                    import soundfile as sf
                    sf.write(buf, wav, syn.output_sample_rate, format="WAV")
                    b64_wav = base64.b64encode(buf.getvalue()).decode("ascii")
                    return {
                        "audioContent": b64_wav,
                        "format": "wav",
                        "voice": "indic_tts_local",
                        "language": lang,
                    }
    except Exception as fb_exc:
        logger.warning("Indic-TTS local fallback failed: %s", fb_exc)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Speech synthesis failed across both neural and local fallback engines.",
    )

