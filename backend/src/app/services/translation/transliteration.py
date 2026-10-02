from __future__ import annotations

import logging
from functools import lru_cache
import httpx
from app.core.config import settings

logger = logging.getLogger("smart-farming.transliteration")


def has_indic_chars(text: str) -> bool:
    """Return True if string contains Devanagari or Gujarati Unicode characters."""
    return any(ord(c) >= 0x0900 for c in text)


@lru_cache(maxsize=2048)
def transliterate_name(text: str, target_lang: str) -> str:
    """Transliterate proper nouns (person names, farm names, plot names) into Gujarati or Hindi.

    Forces source='en' so Google Cloud Translation does not treat Latin-script Indian names as untranslatable.
    Validates that the returned text contains true Indic script characters.
    Falls back to original English if all APIs fail.
    """
    clean_text = (text or "").strip()
    if not clean_text or target_lang in ("en", "english"):
        return clean_text

    target_code = "gu" if target_lang.lower().startswith("gu") else "hi"
    lang_label = "Gujarati" if target_code == "gu" else "Hindi"

    # If the text already contains characters in the target Indic script, return as is
    if target_code == "gu" and any("\u0A80" <= c <= "\u0AFF" for c in clean_text):
        return clean_text
    if target_code == "hi" and any("\u0900" <= c <= "\u097F" for c in clean_text):
        return clean_text

    # 1. Try Google Cloud Translation API v2 with explicit source="en"
    api_key = settings.GOOGLE_TRANSLATION_API_KEY or settings.GOOGLE_TTS_API_KEY
    if api_key:
        try:
            url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
            payload = {
                "q": [clean_text],
                "source": "en",
                "target": target_code,
                "format": "text",
            }
            resp = httpx.post(url, json=payload, timeout=6.0)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                translations = data.get("translations", [])
                if translations:
                    res = translations[0].get("translatedText", "").strip()
                    if res and has_indic_chars(res):
                        return res
        except Exception as exc:
            logger.warning("Google Translate transliteration failed for '%s': %s", clean_text, exc)

    # 2. Fallback to Gemini REST API if GEMINI_API_KEY is configured
    if settings.GEMINI_API_KEY:
        try:
            for model_name in ["gemini-3.8-flash", "gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
                prompt = (
                    f"Transliterate the Indian person name, farm name, or place name '{clean_text}' into {lang_label} script phonetically. "
                    f"Do NOT translate the meaning, only transliterate the pronunciation into {lang_label} script. "
                    f"Output ONLY the transliterated word without quotes or punctuation."
                )
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                resp = httpx.post(url, json=payload, timeout=5.0)
                if resp.status_code == 200:
                    cand = resp.json().get("candidates", [{}])[0]
                    parts = cand.get("content", {}).get("parts", [{}])
                    transliterated = parts[0].get("text", "").strip() if parts else ""
                    if transliterated and has_indic_chars(transliterated):
                        return transliterated
        except Exception as exc:
            logger.debug("Gemini transliteration attempt failed (%s)", exc)

    # 3. Fallback to original English
    return clean_text

