"""
ai_service/routers/advisory.py — Agronomic Decision & Advisory Engine.
Generates safe, ICAR/KVK-aligned crop protection and treatment recommendations.
Supports ultra-fast Groq/Gemini generation with in-process translation to Hindi/Gujarati.
"""

from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, Optional
from fastapi import APIRouter
from pydantic import BaseModel

from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

CONF_GATE = 0.70
FIELDS = ["immediate_action", "treatment", "prevention", "monitoring"]

DISCLAIMERS = {
    "en": "DISCLAIMER: Confirm the diagnosis and any chemical use with your local KVK or agriculture officer, and follow the product label.",
    "hi": "अस्वीकरण: कोई भी रसायन या दवा इस्तेमाल करने से पहले अपने स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि अधिकारी से निदान की पुष्टि करें और उत्पाद के लेबल का पालन करें।",
    "gu": "અસ્વીકરણ: કોઈ પણ રસાયણ કે દવાનો ઉપયોગ કરતા પહેલાં તમારા સ્થાનિક કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) અથવા ખેતીવાડી અધિકારી પાસેથી નિદાનની પુષ્ટિ કરો અને ઉત્પાદનના લેબલનું પાલન કરો.",
}

# Load Advisory Knowledge Base
ADVISORY_KB: dict[str, Any] = {}
if settings.KB_PATH.exists():
    try:
        with open(settings.KB_PATH, "r", encoding="utf-8") as f:
            ADVISORY_KB = json.load(f)
        logger.info("Loaded %d knowledge entries from %s", len(ADVISORY_KB), settings.KB_PATH.name)
    except Exception as exc:
        logger.error("Failed to load advisory knowledge base: %s", exc)
else:
    logger.warning("Advisory knowledge base not found at %s", settings.KB_PATH)


def _as_list(val: Any) -> list:
    if isinstance(val, list):
        return val
    if isinstance(val, str) and val.strip():
        return [val]
    return []


def _fallback_fields(kb_entry: dict[str, Any]) -> dict[str, str]:
    """Generates deterministic, verified agronomy fields directly from the knowledge base."""
    chem = _as_list(kb_entry.get("chemical_options"))
    org = _as_list(kb_entry.get("organic_options"))
    cult = _as_list(kb_entry.get("cultural_practices"))

    treat_parts = []
    if org:
        first_org = org[0]
        treat_parts.append(first_org.get("action") if isinstance(first_org, dict) else str(first_org))
    if chem:
        first_chem = chem[0]
        c_text = f"{first_chem.get('product', '')} ({first_chem.get('dose', '')})" if isinstance(first_chem, dict) else str(first_chem)
        treat_parts.append(f"Chemical: {c_text}")

    treatment_text = "; ".join(treat_parts) if treat_parts else "Follow registered crop protection guidelines under KVK supervision."
    prevention_text = "; ".join(str(c) for c in cult[:2]) if cult else "Ensure proper field sanitation and healthy soil drainage."

    return {
        "immediate_action": kb_entry.get("immediate_action") or f"Inspect the field for spreading symptoms and isolate affected plants.",
        "treatment": kb_entry.get("treatment") or treatment_text,
        "prevention": kb_entry.get("prevention") or prevention_text,
        "monitoring": kb_entry.get("monitoring") or "Check foliage every 24-48 hours for progression.",
    }


def _call_groq_llm(system_prompt: str, user_prompt: str) -> Optional[dict]:
    """Invokes the free high-speed Groq API if GROQ_API_KEY is configured."""
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return None

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=350,
        )
        content = completion.choices[0].message.content
        if content:
            return json.loads(content)
    except Exception as exc:
        logger.warning("Groq LLM call failed or unavailable: %s", exc)
    return None


class AdvisoryRequest(BaseModel):
    crop: str
    disease: str
    confidence: float
    severity_pct: float = 0.0
    severity_bucket: str = "Unknown"
    temperature: str = "N/A"
    humidity: str = "N/A"
    weather_condition: str = "N/A"
    plot_acres: float | None = None
    language: str = "en"


@router.get("/health")
def advisory_health():
    return {
        "status": "healthy",
        "service": "advisory_engine",
        "kb_entries": len(ADVISORY_KB),
        "groq_enabled": bool(settings.GROQ_API_KEY),
        "supported_languages": ["en", "hi", "gu"],
    }


@router.post("/advise")
def advise(req: AdvisoryRequest):
    lang = (req.language or "en").lower().strip()
    if lang not in ("en", "hi", "gu"):
        lang = "en"

    crop = req.crop.strip()
    disease = req.disease.strip()
    conf = req.confidence / 100.0 if req.confidence > 1.0 else req.confidence
    is_healthy = disease.lower() == "healthy"

    # Stage 1: Safety Gate — low confidence diagnosis must escalate to an extension officer
    if conf < CONF_GATE and not is_healthy:
        data = {
            "immediate_action": f"The automatic diagnosis for {crop} is unconfirmed ({conf * 100:.0f}% confidence). Please show the plant to your local KVK or agricultural extension officer before spraying anything.",
            "treatment": "No chemical treatment is recommended until an agronomist confirms the diagnosis.",
            "prevention": "Ensure good field drainage and avoid overhead irrigation while monitoring.",
            "monitoring": "Watch whether the symptoms spread over the next 48 hours.",
            "sources": ["Local KVK / Agriculture Extension Office"],
            "safety_disclaimer": DISCLAIMERS.get(lang, DISCLAIMERS["en"]),
            "language": "en",
        }
        return _package_response(data, lang)

    # Stage 2: Knowledge Base Lookup
    kb_key = f"{crop}|{disease}"
    kb = ADVISORY_KB.get(kb_key)
    if not isinstance(kb, dict) or not kb:
        data = {
            "immediate_action": f"No verified guidance is stored for {crop} - {disease}. Please consult your local KVK or agriculture officer.",
            "treatment": "No chemical treatment is recommended without expert confirmation.",
            "prevention": "Maintain field sanitation and clean tools.",
            "monitoring": "Check the plants regularly for spreading symptoms.",
            "sources": ["Local KVK / Extension Guidelines"],
            "safety_disclaimer": DISCLAIMERS.get(lang, DISCLAIMERS["en"]),
            "language": "en",
        }
        return _package_response(data, lang)

    # Stage 3: LLM Synthesis with Grounded Verification
    fb = _fallback_fields(kb)
    data = dict(fb)

    system_prompt = (
        "You are an agricultural advisory assistant for Indian farmers. "
        "Use ONLY the verified facts provided. Never name a chemical, product or dose that is not in the facts. "
        "Write short, simple sentences a farmer can follow, and keep every value under 35 words. "
        "Reply with a JSON object containing keys: immediate_action, treatment, prevention, monitoring."
    )
    user_prompt = f"""Verified facts:
- Crop: {crop}
- Diagnosis: {disease}
- Immediate action guideline: {fb['immediate_action']}
- Treatment guideline: {fb['treatment']}
- Prevention guideline: {fb['prevention']}
- Monitoring guideline: {fb['monitoring']}

Field situation:
- Severity: {req.severity_bucket} ({req.severity_pct}% leaf affected)
- Weather: {req.temperature} C, {req.weather_condition}, {req.humidity}% humidity
- Plot area: {req.plot_acres or 'standard field'} acres
"""

    llm_result = _call_groq_llm(system_prompt, user_prompt)
    if llm_result and isinstance(llm_result, dict):
        for k in FIELDS:
            if llm_result.get(k) and isinstance(llm_result[k], str):
                data[k] = llm_result[k].strip()

    # Sources extraction
    srcs = []
    for item in _as_list(kb.get("chemical_options")) + _as_list(kb.get("organic_options")):
        if isinstance(item, dict) and item.get("source"):
            srcs.append(str(item["source"]))
    for s in _as_list(kb.get("sources")) + _as_list(kb.get("source_refs")):
        srcs.append(str(s))
    data["sources"] = list(dict.fromkeys(srcs)) or ["ICAR Integrated Pest Management Guidelines"]
    data["safety_disclaimer"] = DISCLAIMERS.get(lang, DISCLAIMERS["en"])
    data["language"] = "en"

    return _package_response(data, lang)


def _package_response(data: dict, lang: str) -> dict:
    """Translates the response in-process if a regional language is requested."""
    if lang == "en":
        return data

    try:
        from routers.translation import translate_texts

        texts_to_translate = [data[k] for k in FIELDS]
        translated = translate_texts(texts_to_translate, lang)

        out = dict(data)
        out["english"] = {k: data[k] for k in FIELDS}
        for k, tr in zip(FIELDS, translated):
            out[k] = tr
        out["language"] = lang
        return out
    except Exception as exc:
        logger.warning("In-process translation of advisory failed: %s", exc)
        return data

