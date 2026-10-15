from __future__ import annotations

import logging
import re
from typing import Any
import httpx

from app.core.config import settings

logger = logging.getLogger("smart-farming.translation")

SENTENCE_SPLIT_PATTERN = re.compile(r'(?<=[.?!।])\s+')


def split_into_sentences(text: str) -> list[str]:
    """Split multi-sentence agricultural paragraphs into individual sentences.

    Splits on English (. ? !) and Indic (।) sentence terminals,
    preserving sentence granularity for sequence-to-sequence translation models.
    """
    if not text or not text.strip():
        return []
    sentences = [s.strip() for s in SENTENCE_SPLIT_PATTERN.split(text.strip()) if s.strip()]
    return sentences or [text.strip()]


def join_sentences(sentences: list[str]) -> str:
    """Reassemble translated sentences into a coherent paragraph."""
    return " ".join(s for s in sentences if s).strip()

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




async def translate_batch_indictrans(texts: list[str], target_lang: str) -> list[str]:
    """Translate multiple texts via dedicated IndicTrans2 FastAPI server (e.g., Colab / HF Space).

    Splits paragraphs into sentence-level chunks, translates in batch, and reassembles them.
    Bypasses ngrok free-tier warning screen using ngrok-skip-browser-warning.
    """
    if not texts:
        return []

    target_code = normalize_language_code(target_lang)
    if target_code == "en":
        return texts
    if target_code not in ("hi", "gu"):
        # IndicTrans2 is configured for Indic languages (Hindi, Gujarati)
        return texts

    server_url = (getattr(settings, "TRANSLATION_SERVER_URL", "") or "").strip()
    if not server_url:
        raise RuntimeError("TRANSLATION_SERVER_URL is not configured")

    flat_sentences: list[str] = []
    text_slices: list[slice] = []
    for text in texts:
        if not text or not text.strip():
            text_slices.append(slice(len(flat_sentences), len(flat_sentences)))
            continue
        sents = split_into_sentences(text)
        start = len(flat_sentences)
        flat_sentences.extend(sents)
        text_slices.append(slice(start, len(flat_sentences)))

    if not flat_sentences:
        return texts

    timeout = float(getattr(settings, "TRANSLATION_SERVER_TIMEOUT", 15.0) or 15.0)
    endpoint = f"{server_url.rstrip('/')}/translate"
    headers = {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "69420",
        "User-Agent": "SmartFarmingBackend/2.0",
    }
    gateway_key = getattr(settings, "GATEWAY_API_KEY", None)
    if gateway_key:
        headers["Authorization"] = f"Bearer {gateway_key}"

    payload = {
        "texts": flat_sentences,
        "target": target_code,
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(endpoint, json=payload, headers=headers)

    if resp.status_code != 200:
        logger.error("IndicTrans2 API error: %d %s", resp.status_code, resp.text)
        raise RuntimeError(f"IndicTrans2 API failed with code {resp.status_code}: {resp.text}")

    data = resp.json()
    translated_sentences = data.get("translations", [])
    if len(translated_sentences) != len(flat_sentences):
        raise RuntimeError(
            f"IndicTrans2 returned {len(translated_sentences)} items for {len(flat_sentences)} inputs"
        )

    results: list[str] = []
    for idx, sl in enumerate(text_slices):
        if sl.start == sl.stop:
            results.append(texts[idx])
        else:
            results.append(join_sentences(translated_sentences[sl]))

    return results


def translate_batch_indictrans_sync(texts: list[str], target_lang: str) -> list[str]:
    """Synchronous version of IndicTrans2 batch translation for background worker threads."""
    if not texts:
        return []

    target_code = normalize_language_code(target_lang)
    if target_code == "en":
        return texts
    if target_code not in ("hi", "gu"):
        return texts

    server_url = (getattr(settings, "TRANSLATION_SERVER_URL", "") or "").strip()
    if not server_url:
        raise RuntimeError("TRANSLATION_SERVER_URL is not configured")

    flat_sentences: list[str] = []
    text_slices: list[slice] = []
    for text in texts:
        if not text or not text.strip():
            text_slices.append(slice(len(flat_sentences), len(flat_sentences)))
            continue
        sents = split_into_sentences(text)
        start = len(flat_sentences)
        flat_sentences.extend(sents)
        text_slices.append(slice(start, len(flat_sentences)))

    if not flat_sentences:
        return texts

    timeout = float(getattr(settings, "TRANSLATION_SERVER_TIMEOUT", 15.0) or 15.0)
    endpoint = f"{server_url.rstrip('/')}/translate"
    headers = {
        "Content-Type": "application/json",
        "ngrok-skip-browser-warning": "69420",
        "User-Agent": "SmartFarmingBackend/2.0",
    }
    gateway_key = getattr(settings, "GATEWAY_API_KEY", None)
    if gateway_key:
        headers["Authorization"] = f"Bearer {gateway_key}"

    payload = {
        "texts": flat_sentences,
        "target": target_code,
    }

    with httpx.Client(timeout=timeout) as client:
        resp = client.post(endpoint, json=payload, headers=headers)

    if resp.status_code != 200:
        logger.error("IndicTrans2 sync API error: %d %s", resp.status_code, resp.text)
        raise RuntimeError(f"IndicTrans2 sync API failed with code {resp.status_code}: {resp.text}")

    data = resp.json()
    translated_sentences = data.get("translations", [])
    if len(translated_sentences) != len(flat_sentences):
        raise RuntimeError(
            f"IndicTrans2 returned {len(translated_sentences)} items for {len(flat_sentences)} inputs"
        )

    results: list[str] = []
    for idx, sl in enumerate(text_slices):
        if sl.start == sl.stop:
            results.append(texts[idx])
        else:
            results.append(join_sentences(translated_sentences[sl]))

    return results


async def _fallback_translate_batch(texts: list[str], target_code: str) -> list[str]:
    """Free reliable fallback translator using Google Translate public endpoint when GPU server is offline."""
    out = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    async with httpx.AsyncClient(timeout=10.0, headers=headers) as client:
        for t in texts:
            if not t or not t.strip() or not any(c.isalpha() for c in t):
                out.append(t)
                continue
            try:
                resp = await client.get(
                    "https://translate.googleapis.com/translate_a/single",
                    params={"client": "gtx", "sl": "auto", "tl": target_code, "dt": "t", "q": t},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    segments = "".join(s[0] for s in data[0] if s and s[0])
                    out.append(segments if segments else t)
                else:
                    out.append(t)
            except Exception as exc:
                logger.warning("Fallback translate request failed for '%s': %s", t[:30], exc)
                out.append(t)
    return out


def _fallback_translate_batch_sync(texts: list[str], target_code: str) -> list[str]:
    """Synchronous fallback translator using Google Translate public endpoint when GPU server is offline."""
    out = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    with httpx.Client(timeout=10.0, headers=headers) as client:
        for t in texts:
            if not t or not t.strip() or not any(c.isalpha() for c in t):
                out.append(t)
                continue
            try:
                resp = client.get(
                    "https://translate.googleapis.com/translate_a/single",
                    params={"client": "gtx", "sl": "auto", "tl": target_code, "dt": "t", "q": t},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    segments = "".join(s[0] for s in data[0] if s and s[0])
                    out.append(segments if segments else t)
                else:
                    out.append(t)
            except Exception as exc:
                logger.warning("Fallback sync translate request failed for '%s': %s", t[:30], exc)
                out.append(t)
    return out


async def translate_batch(texts: list[str], target_lang: str) -> list[str]:
    """Translate a list of texts into target_lang, using Upstash Redis REST caching with IndicTrans2 server."""
    target_code = normalize_language_code(target_lang)
    if not texts:
        return texts
    if target_code == "en":
        # If texts are already in English/ASCII (no Indic chars), return as-is
        if not any(any(ord(c) >= 0x0900 for c in t) for t in texts if t):
            return texts

    import asyncio
    import hashlib
    from app.core.redis_rest import redis_rest

    results: list[str | None] = [None] * len(texts)
    missing_indices: list[int] = []
    missing_texts: list[str] = []

    # Prepare keys for single batch lookup
    items_to_lookup: list[tuple[int, str, str]] = []
    for idx, text in enumerate(texts):
        if not text or not text.strip():
            results[idx] = text
        else:
            h = hashlib.sha256(text.strip().encode("utf-8")).hexdigest()
            items_to_lookup.append((idx, f"sf:trans:{target_code}:{h}", text))

    if items_to_lookup:
        keys = [item[1] for item in items_to_lookup]
        cached_values = await redis_rest.mget(keys)
        for (idx, _, text), cached in zip(items_to_lookup, cached_values):
            if cached and (target_code not in ("hi", "gu") or not any(c.isalpha() for c in text) or any(ord(c) >= 0x0900 for c in cached)):
                results[idx] = cached
            else:
                missing_indices.append(idx)
                missing_texts.append(text)

    if missing_texts:
        translated_missing: list[str] | None = None

        # Primary: IndicTrans2 (Colab / GPU server via Cloudflare Gateway)
        server_url = (getattr(settings, "TRANSLATION_SERVER_URL", "") or "").strip()
        if server_url and target_code in ("hi", "gu"):
            try:
                translated_missing = await translate_batch_indictrans(missing_texts, target_code)
            except Exception as exc:
                logger.warning("IndicTrans2 translation failed (%s); trying fallback translator.", exc)

        # Fallback: Google Translate public endpoint if IndicTrans2 is unavailable or did not produce expected text
        if (
            translated_missing is None
            or (target_code in ("hi", "gu") and not any(any(ord(c) >= 0x0900 for c in t) for t in translated_missing if t))
        ):
            try:
                fallback_res = await _fallback_translate_batch(missing_texts, target_code)
                if fallback_res and (target_code not in ("hi", "gu") or any(any(ord(c) >= 0x0900 for c in t) for t in fallback_res if t)):
                    translated_missing = fallback_res
            except Exception as exc:
                logger.warning("Fallback translation failed: %s", exc)

        if translated_missing is None:
            translated_missing = list(missing_texts)

        cache_tasks = []
        for idx, trans_text, orig_text in zip(missing_indices, translated_missing, missing_texts):
            results[idx] = trans_text
            if trans_text and trans_text != orig_text:
                h = hashlib.sha256(orig_text.strip().encode("utf-8")).hexdigest()
                cache_tasks.append(redis_rest.set(f"sf:trans:{target_code}:{h}", trans_text, ex=86400 * 60))

        if cache_tasks:
            await asyncio.gather(*cache_tasks, return_exceptions=True)

    return [r if r is not None else "" for r in results]


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


def translate_batch_sync(texts: list[str], target_lang: str) -> list[str]:
    """Synchronous batch translation via IndicTrans2 server.

    1. Tries IndicTrans2 server if configured and target is Hindi/Gujarati.
    2. Falls back to original source texts if server is unavailable.
    """
    if not texts:
        return []
    target_code = normalize_language_code(target_lang)
    if target_code == "en":
        if not any(any(ord(c) >= 0x0900 for c in t) for t in texts if t):
            return texts

    # Primary: IndicTrans2 (Colab / GPU server)
    server_url = (getattr(settings, "TRANSLATION_SERVER_URL", "") or "").strip()
    if server_url and target_code in ("hi", "gu"):
        try:
            res = translate_batch_indictrans_sync(texts, target_code)
            if any(any(ord(c) >= 0x0900 for c in t) for t in res if t):
                return res
        except Exception as exc:
            logger.warning("IndicTrans2 sync translation failed (%s); trying fallback translator", exc)

    # Fallback: Google Translate public endpoint
    try:
        fallback_res = _fallback_translate_batch_sync(texts, target_code)
        if fallback_res and (target_code not in ("hi", "gu") or any(any(ord(c) >= 0x0900 for c in t) for t in fallback_res if t)):
            return fallback_res
    except Exception as exc:
        logger.warning("Fallback sync translation failed: %s", exc)

    return texts


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
        translated_list = translate_batch_sync(texts_to_translate, target_code)
    except Exception as exc:
        logger.warning("Sync translation failed: %s", exc)
        return recommendation

    translated_dict = dict(recommendation)
    translated_dict["language"] = target_code
    for k, trans in zip(indices, translated_list):
        if trans:
            translated_dict[k] = trans

    return translated_dict

