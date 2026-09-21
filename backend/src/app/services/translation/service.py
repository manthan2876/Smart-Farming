from __future__ import annotations

import logging
import os
from typing import Any
import httpx

from app.core.config import settings

logger = logging.getLogger("smart-farming.translation")

# Map supported language names or codes to standard ISO-639-1 codes
_LANG_CODE_MAP = {
    "english": "en",
    "en": "en",
    "en-us": "en",
    "en-in": "en",
    "hindi": "hi",
    "hi": "hi",
    "hi-in": "hi",
    "gujarati": "gu",
    "gu": "gu",
    "gu-in": "gu",
    "marathi": "mr",
    "mr": "mr",
    "telugu": "te",
    "te": "te",
    "tamil": "ta",
    "ta": "ta",
}


def normalize_language_code(language: str | None) -> str:
    """Normalize any language string to its 2-letter ISO code (default: 'en')."""
    if not language:
        return "en"
    clean = language.strip().lower()
    return _LANG_CODE_MAP.get(clean, "en")


def _get_google_api_key() -> str:
    return (
        settings.GOOGLE_TRANSLATION_API_KEY
        or os.getenv("GOOGLE_TRANSLATION_API_KEY")
        or settings.GOOGLE_TTS_API_KEY
        or os.getenv("GOOGLE_TTS_API_KEY")
        or ""
    )


async def translate_batch_google(texts: list[str], target_lang: str) -> list[str]:
    """Translate multiple text strings in a single batch call via Google Cloud Translation API v2."""
    if not texts:
        return []
    
    target_code = normalize_language_code(target_lang)
    if target_code == "en":
        return texts

    api_key = _get_google_api_key()
    if not api_key:
        raise RuntimeError("GOOGLE_TRANSLATION_API_KEY is not configured")

    url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
    payload = {
        "q": texts,
        "target": target_code,
        "format": "text",
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(url, json=payload)

    if resp.status_code != 200:
        logger.error("Google Translation API error: %d %s", resp.status_code, resp.text)
        raise RuntimeError(f"Google Translation API failed with code {resp.status_code}: {resp.text}")

    data = resp.json().get("data", {})
    translations = data.get("translations", [])
    return [t.get("translatedText", "") for t in translations]


async def translate_batch_hf_fallback(texts: list[str], target_lang: str) -> list[str]:
    """Fallback translation using Hugging Face Qwen LLM if Google API is unavailable."""
    hf_token = os.getenv("HF_TOKEN")
    if not hf_token:
        return texts

    target_code = normalize_language_code(target_lang)
    lang_name = "Hindi" if target_code == "hi" else ("Gujarati" if target_code == "gu" else target_lang)

    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(api_key=hf_token, provider="nscale")
        results: list[str] = []
        for text in texts:
            if not text.strip():
                results.append("")
                continue
            resp = client.chat.completions.create(
                model="Qwen/Qwen3-4B-Instruct-2507",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            f"You are an agricultural advisory translator. "
                            f"Translate the following agricultural recommendation into {lang_name} accurately. "
                            f"Return ONLY the translated text without commentary."
                        ),
                    },
                    {"role": "user", "content": text},
                ],
                max_tokens=350,
            )
            trans = resp.choices[0].message.content.strip()
            results.append(trans if trans else text)
        return results
    except Exception as exc:
        logger.warning("HF translation fallback failed: %s", exc)
        return texts


async def translate_batch(texts: list[str], target_lang: str) -> list[str]:
    """Translate a list of texts into target_lang, using Google Cloud Translation API with HF fallback."""
    target_code = normalize_language_code(target_lang)
    if target_code == "en":
        return texts

    try:
        return await translate_batch_google(texts, target_code)
    except Exception as exc:
        logger.warning("Google translation failed (%s), falling back to HF translation...", exc)
        return await translate_batch_hf_fallback(texts, target_code)


async def translate_text(text: str, target_lang: str) -> str:
    """Translate a single text string."""
    results = await translate_batch([text], target_lang)
    return results[0] if results else text


async def translate_recommendation(recommendation: dict[str, Any], target_lang: str) -> dict[str, Any]:
    """
    Translate all recommendation paragraphs into the target language.

    Preserves original English structure and returns translated text for:
    - immediate_action
    - treatment
    - prevention
    - monitoring
    - general recommendation text / fallback
    """
    target_code = normalize_language_code(target_lang)
    if target_code == "en":
        return recommendation

    keys = ["immediate_action", "treatment", "prevention", "monitoring", "recommendation"]
    indices: list[str] = []
    texts_to_translate: list[str] = []

    for k in keys:
        val = recommendation.get(k)
        if val and isinstance(val, str) and val.strip():
            indices.append(k)
            texts_to_translate.append(val.strip())

    if not texts_to_translate:
        return recommendation

    translated_list = await translate_batch(texts_to_translate, target_code)

    translated_dict = dict(recommendation)
    translated_dict["language"] = target_code
    for k, trans in zip(indices, translated_list):
        if trans:
            translated_dict[k] = trans

    return translated_dict


def translate_batch_google_sync(texts: list[str], target_lang: str) -> list[str]:
    """Synchronous version of batch Google translation for ARQ worker threads."""
    if not texts:
        return []
    target_code = normalize_language_code(target_lang)
    if target_code == "en":
        return texts

    api_key = _get_google_api_key()
    if not api_key:
        raise RuntimeError("GOOGLE_TRANSLATION_API_KEY is not configured")

    url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
    payload = {
        "q": texts,
        "target": target_code,
        "format": "text",
    }

    with httpx.Client(timeout=10.0) as client:
        resp = client.post(url, json=payload)

    if resp.status_code != 200:
        logger.error("Google Translation API error: %d %s", resp.status_code, resp.text)
        raise RuntimeError(f"Google Translation API failed with code {resp.status_code}: {resp.text}")

    data = resp.json().get("data", {})
    translations = data.get("translations", [])
    return [t.get("translatedText", "") for t in translations]


def translate_recommendation_sync(recommendation: dict[str, Any], target_lang: str) -> dict[str, Any]:
    """Synchronous recommendation translation for background worker jobs."""
    target_code = normalize_language_code(target_lang)
    if target_code == "en":
        return recommendation

    keys = ["immediate_action", "treatment", "prevention", "monitoring", "recommendation"]
    indices: list[str] = []
    texts_to_translate: list[str] = []

    for k in keys:
        val = recommendation.get(k)
        if val and isinstance(val, str) and val.strip():
            indices.append(k)
            texts_to_translate.append(val.strip())

    if not texts_to_translate:
        return recommendation

    try:
        translated_list = translate_batch_google_sync(texts_to_translate, target_code)
    except Exception as exc:
        logger.warning("Sync Google translation failed: %s", exc)
        return recommendation

    translated_dict = dict(recommendation)
    translated_dict["language"] = target_code
    for k, trans in zip(indices, translated_list):
        if trans:
            translated_dict[k] = trans

    return translated_dict

