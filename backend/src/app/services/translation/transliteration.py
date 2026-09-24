from __future__ import annotations

import logging
from functools import lru_cache
import httpx
from app.core.config import settings

logger = logging.getLogger("smart-farming.transliteration")


@lru_cache(maxsize=2048)
def transliterate_name(text: str, target_lang: str) -> str:
    """Transliterate proper nouns (person names, farm names, plot names) into Gujarati or Hindi phonetically.

    Attempts Gemini LLM first with an explicit phonetic transliteration prompt.
    Falls back to Google Cloud Translation API v2 if Gemini is unavailable or rate-limited.
    Falls back to original English if all APIs fail.
    """
    clean_text = (text or "").strip()
    if not clean_text or target_lang in ("en", "english"):
        return clean_text

    target_code = "gu" if target_lang.lower().startswith("gu") else "hi"
    lang_label = "Gujarati" if target_code == "gu" else "Hindi"

    # 1. Try Gemini REST API if GEMINI_API_KEY is configured
    if settings.GEMINI_API_KEY:
        try:
            for model_name in ["gemini-2.5-flash", "gemini-3.6-flash"]:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={settings.GEMINI_API_KEY}"
                prompt = (
                    f"Transliterate the Indian name, farm name, or place name '{clean_text}' into {lang_label} script phonetically. "
                    f"Do NOT translate the meaning, only transliterate the pronunciation. "
                    f"Output ONLY the transliterated word without quotes or punctuation."
                )
                payload = {"contents": [{"parts": [{"text": prompt}]}]}
                resp = httpx.post(url, json=payload, timeout=6.0)
                if resp.status_code == 200:
                    cand = resp.json().get("candidates", [{}])[0]
                    parts = cand.get("content", {}).get("parts", [{}])
                    transliterated = parts[0].get("text", "").strip() if parts else ""
                    if transliterated:
                        return transliterated
        except Exception as exc:
            logger.debug("Gemini transliteration attempt failed (%s), trying Google Translate fallback...", exc)

    # 2. Fallback to Google Cloud Translation API v2
    api_key = settings.GOOGLE_TRANSLATION_API_KEY or settings.GOOGLE_TTS_API_KEY
    if api_key:
        try:
            url = f"https://translation.googleapis.com/language/translate/v2?key={api_key}"
            resp = httpx.post(url, json={"q": [clean_text], "target": target_code}, timeout=6.0)
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                translations = data.get("translations", [])
                if translations:
                    return translations[0].get("translatedText", clean_text).strip()
        except Exception as exc:
            logger.warning("Google Translate fallback failed for transliteration '%s': %s", clean_text, exc)

    # 3. Fallback to original English
    return clean_text
