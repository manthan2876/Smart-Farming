"""
ai_service/routers/translation.py — IndicTrans2 Translation API router.
Provides high-performance English to Indic translation (Hindi, Gujarati).
Can be called via HTTP or directly in-process by the Advisory router.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from pathlib import Path
from typing import Optional

import torch
from fastapi import APIRouter
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

MODEL_NAME = "ai4bharat/indictrans2-en-indic-dist-200M"
LANG_CODES = {
    "hi": "hin_Deva",
    "gu": "guj_Gujr",
}

CACHE_FILE = settings.CACHE_DIR / "indictrans_cache.json"

_model = None
_tokenizer = None
_processor = None
_lock = threading.Lock()
_cache: dict[str, str] = {}


def _init_cache():
    global _cache
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _cache = json.load(f)
            logger.info("Loaded %d cached translations.", len(_cache))
        except Exception as e:
            logger.warning("Could not read translation cache: %s", e)


def _save_cache():
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_cache, f, ensure_ascii=False)
    except Exception as e:
        logger.warning("Could not persist translation cache: %s", e)


_init_cache()


def _get_indictrans_components():
    """Lazy-load the IndicTrans2 model and tokenizer upon first call."""
    global _model, _tokenizer, _processor
    if _model is not None and _tokenizer is not None and _processor is not None:
        return _model, _tokenizer, _processor

    with _lock:
        if _model is not None:
            return _model, _tokenizer, _processor

        logger.info("Loading IndicTrans2 (%s) on %s...", MODEL_NAME, settings.DEVICE)
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            from IndicTransToolkit.processor import IndicProcessor

            _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
            _model = AutoModelForSeq2SeqLM.from_pretrained(
                MODEL_NAME,
                trust_remote_code=True,
                torch_dtype=torch.float32 if settings.DEVICE == "cpu" else torch.float16,
            ).to(settings.DEVICE).eval()
            _processor = IndicProcessor(inference=True)
            logger.info("IndicTrans2 loaded successfully.")
        except Exception as exc:
            logger.error("Failed to load IndicTrans2: %s", exc)
            raise RuntimeError(f"IndicTrans2 initialization error: {exc}")

        return _model, _tokenizer, _processor


def _run_batch(texts: list[str], target_lang_code: str) -> list[str]:
    """Runs a batch through IndicTrans2."""
    model, tokenizer, processor = _get_indictrans_components()
    num_beams = 4 if settings.DEVICE == "cuda" else 2

    batch = processor.preprocess_batch(texts, src_lang="eng_Latn", tgt_lang=target_lang_code)
    inputs = tokenizer(
        batch,
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors="pt"
    ).to(settings.DEVICE)

    with torch.inference_mode():
        generated_tokens = model.generate(
            **inputs,
            num_beams=num_beams,
            max_length=256,
            use_cache=False
        )

    decoded = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
    return processor.postprocess_batch(decoded, lang=target_lang_code)


def translate_texts(texts: list[str], target_lang: str) -> list[str]:
    """
    Direct function callable internally by other routers (e.g. advisory).
    """
    lang = target_lang.lower().strip()
    if lang == "en" or not texts:
        return texts

    tgt_code = LANG_CODES.get(lang)
    if not tgt_code:
        logger.warning("Unsupported target language: %s, returning original texts.", target_lang)
        return texts

    def _cache_key(t: str) -> str:
        return f"{lang}:{t.strip()}"

    with _lock:
        todo = [t for t in dict.fromkeys(texts) if t.strip() and _cache_key(t) not in _cache]
        chunk_size = 16 if settings.DEVICE == "cuda" else 8

        if todo:
            try:
                for i in range(0, len(todo), chunk_size):
                    chunk = todo[i : i + chunk_size]
                    translated_chunk = _run_batch(chunk, tgt_code)
                    for src, dst in zip(chunk, translated_chunk):
                        _cache[_cache_key(src)] = dst
                _save_cache()
            except Exception as e:
                logger.error("Translation inference failed: %s", e)
                # Fallback to returning original strings on inference failure
                return texts

        return [_cache.get(_cache_key(t), t) for t in texts]


class TranslationRequest(BaseModel):
    texts: list[str]
    target: str


@router.get("/health")
def translation_health():
    return {
        "status": "healthy",
        "service": "indictrans2",
        "device": settings.DEVICE,
        "cached_translations": len(_cache),
        "supported_languages": list(LANG_CODES.keys()),
    }


@router.post("/translate")
def translate_api(req: TranslationRequest):
    translations = translate_texts(req.texts, req.target)
    return {"translations": translations}

