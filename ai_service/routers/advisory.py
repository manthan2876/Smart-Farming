"""
ai_service/routers/advisory.py — Agronomic Decision & Advisory Engine.
Generates safe, ICAR/KVK-aligned crop protection and treatment recommendations.
Features instant deterministic ICAR/KVK facts with built-in Hindi & Gujarati translations,
and optional cloud Groq synthesis with Zero-Latency execution on CPU.
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
from typing import Any, Optional

try:
    import torch
except ImportError:
    torch = None
try:
    from fastapi import APIRouter
except ImportError:
    class APIRouter:  # type: ignore
        def get(self, *args, **kwargs):
            return lambda fn: fn
        def post(self, *args, **kwargs):
            return lambda fn: fn

try:
    from pydantic import BaseModel
except ImportError:
    class BaseModel:  # type: ignore
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

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

LOW_CONF_DATA = {
    "en": {
        "immediate_action": "The automatic diagnosis for {crop} is unconfirmed ({conf:.0f}% confidence). Please show the plant to your local KVK or agricultural extension officer before spraying anything.",
        "treatment": "No chemical treatment is recommended until an agronomist confirms the diagnosis.",
        "prevention": "Ensure good field drainage and avoid overhead irrigation while monitoring.",
        "monitoring": "Watch whether the symptoms spread over the next 48 hours.",
    },
    "hi": {
        "immediate_action": "{crop} के लिए स्वचालित निदान की पुष्टि नहीं हुई है ({conf:.0f}% सटीकता)। कृपया कोई भी दवा छिड़कने से पहले अपने स्थानीय केवीके (KVK) या कृषि अधिकारी को पौधा दिखाएं।",
        "treatment": "विशेषज्ञ द्वारा निदान की पुष्टि होने तक किसी भी रासायनिक उपचार की अनुशंसा नहीं की जाती है।",
        "prevention": "खेत में उचित जल निकासी बनाए रखें और निगरानी के दौरान पौधों पर ऊपर से पानी छिड़कने से बचें।",
        "monitoring": "अगले 48 घंटों में लक्षणों के फैलाव पर लगातार नजर रखें।",
    },
    "gu": {
        "immediate_action": "{crop} માટે આપોઆપ નિદાનની પુષ્ટિ થયેલ નથી ({conf:.0f}% ચોક્કસતા). કૃપા કરીને કોઈ પણ દવાનો છંટકાવ કરતા પહેલાં તમારા સ્થાનિક કેવીકે (KVK) અથવા ખેતીવાડી અધિકારીને પાન બતાવો.",
        "treatment": "નિષ્ણાત દ્વારા નિદાનની પુષ્ટિ ન થાય ત્યાં સુધી કોઈ રાસાયણિક છંટકાવની ભલામણ કરવામાં આવતી નથી.",
        "prevention": "ખેતરમાં સારો નિતાર જાળવો અને નિરીક્ષણ દરમિયાન પાન પર વધારે પાણી છાંટવાનું ટાળો.",
        "monitoring": "આગામી 48 કલાકમાં લક્ષણો વધે છે કે નહીં તેના પર નિયમિત નજર રાખો.",
    },
}

UNVERIFIED_DATA = {
    "en": {
        "immediate_action": "No verified guidance is stored for {crop} - {disease}. Please consult your local KVK or agriculture officer.",
        "treatment": "No chemical treatment is recommended without expert confirmation.",
        "prevention": "Maintain field sanitation and clean tools.",
        "monitoring": "Check the plants regularly for spreading symptoms.",
    },
    "hi": {
        "immediate_action": "{crop} - {disease} के लिए कोई सत्यापित मार्गदर्शन संग्रहीत नहीं है। कृपया अपने स्थानीय केवीके या कृषि अधिकारी से परामर्श लें।",
        "treatment": "विशेषज्ञ पुष्टि के बिना किसी रासायनिक उपचार की अनुशंसा नहीं की जाती है।",
        "prevention": "खेत की स्वच्छता बनाए रखें और औजारों को साफ रखें।",
        "monitoring": "लक्षणों के फैलाव के लिए पौधों की नियमित जांच करें।",
    },
    "gu": {
        "immediate_action": "{crop} - {disease} માટે કોઈ ચકાસાયેલ માર્ગદર્શન ઉપલબ્ધ નથી. કૃપા કરીને તમારા સ્થાનિક કેવીકે અથવા ખેતીવાડી અધિકારીનો સંપર્ક કરો.",
        "treatment": "નિષ્ણાતની પુષ્ટિ વગર કોઈપણ રાસાયણિક ઉપચારની ભલામણ કરવામાં આવતી નથી.",
        "prevention": "ખેતરની સ્વચ્છતા જાળવો અને ઓજારો સાફ રાખો.",
        "monitoring": "લક્ષણો વધે છે કે નહીં તે માટે છોડનું નિયમિત નિરીક્ષણ કરો.",
    },
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


def _normalize_crop(crop: str) -> str:
    c = crop.strip()
    c_lower = c.lower().replace("_", " ")
    if c_lower in ("pepper bell", "pepper_bell", "capsicum", "bell pepper"):
        return "Pepper Bell"
    if c_lower in ("cotton", "kapas"):
        return "Cotton"
    if c_lower in ("groundnut", "peanut", "mungfali"):
        return "Groundnut"
    if c_lower in ("potato", "aloo", "batata"):
        return "Potato"
    if c_lower in ("tomato", "tamatar"):
        return "Tomato"
    return c.title()


def _normalize_disease(crop: str, disease: str) -> str:
    d = disease.strip()
    c_norm = _normalize_crop(crop)
    c_lower = c_norm.lower()
    if d.lower().startswith(c_lower + " "):
        d = d[len(c_norm):].strip()
    elif d.lower().startswith(c_lower.replace(" ", "_") + " "):
        d = d[len(c_norm.replace(" ", "_")):].strip()

    d_lower = d.lower()
    aliases = {
        "mold leaf": "Leaf Mold",
        "leaf mold": "Leaf Mold",
        "septoria": "Septoria Leaf Spot",
        "septoria leaf spot": "Septoria Leaf Spot",
        "mosaic virus": "Tomato Mosaic Virus" if c_norm == "Tomato" else "Mosaic Virus",
        "tomato mosaic virus": "Tomato Mosaic Virus",
        "yellow curl virus": "Tomato Yellow Leaf Curl Virus" if c_norm == "Tomato" else "Yellow Curl Virus",
        "yellow leaf curl virus": "Tomato Yellow Leaf Curl Virus" if c_norm == "Tomato" else "Yellow Curl Virus",
        "tomato yellow leaf curl virus": "Tomato Yellow Leaf Curl Virus",
        "spider mites": "Spider Mites",
        "spider mite": "Spider Mites",
        "althernaria leaf spot": "Alternaria Leaf Spot",
        "alternaria leaf spot": "Alternaria Leaf Spot",
        "tikka": "Late Leaf Spot",
        "late leaf spot": "Late Leaf Spot",
        "early leaf spot": "Early Leaf Spot",
        "leaf spot": "Early Leaf Spot",
        "cercospora leaf spot": "Cercospora Leaf Spot",
        "target spot": "Target Spot",
        "verticillium wilt": "Verticillium Wilt",
        "fusarium wilt": "Fusarium Wilt",
        "bacterial blight": "Bacterial Blight",
        "bacterial spot": "Bacterial Spot",
        "bacteria": "Bacteria",
        "fungi": "Fungi",
        "nematode": "Nematode",
        "pest": "Pest",
        "virus": "Virus",
        "curl virus": "Curl Virus",
        "leaf curl": "Leaf Curl",
        "powdery mildew": "Powdery Mildew",
        "edema": "Edema",
        "rosette": "Rosette",
        "rust": "Rust",
        "nutrition deficiency": "Nutrition Deficiency",
        "leaf reddening": "Leaf Reddening",
        "healthy": "Healthy",
        "healthy leaf": "Healthy",
    }
    if d_lower in aliases:
        return aliases[d_lower]
    return d.title()


def _find_kb_entry(crop: str, disease: str) -> tuple[Optional[str], Optional[dict[str, Any]]]:
    """Finds the best matching verified knowledge base entry with alias support."""
    c_norm = _normalize_crop(crop)
    d_norm = _normalize_disease(c_norm, disease)

    # 1. Exact candidate keys
    candidates = [
        f"{c_norm}|{d_norm}",
        f"{c_norm.replace(' ', '_')}|{d_norm}",
    ]
    for cand in candidates:
        if cand in ADVISORY_KB:
            return cand, ADVISORY_KB[cand]

    # 2. Case-insensitive lookup
    target_key = f"{c_norm}|{d_norm}".lower()
    for k, v in ADVISORY_KB.items():
        if k.lower() == target_key:
            return k, v

    # 3. Fuzzy search within crop keys
    crop_keys = [
        k for k in ADVISORY_KB
        if k.startswith(c_norm + "|") or k.startswith(c_norm.replace(" ", "_") + "|")
    ]
    d_clean = d_norm.lower()
    for k in crop_keys:
        k_dis = k.split("|")[1].lower()
        if d_clean in k_dis or k_dis in d_clean:
            return k, ADVISORY_KB[k]

    return None, None


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

    immediate = kb_entry.get("immediate_action") or "Inspect the field for spreading symptoms and isolate affected plants."
    treatment = kb_entry.get("treatment") or treatment_text
    prevention = kb_entry.get("prevention") or prevention_text
    monitoring = kb_entry.get("monitoring") or "Check foliage every 24-48 hours for progression."

    chem_rec = kb_entry.get("chemical_recommendation")
    if chem_rec and "none" not in chem_rec.lower() and "requires local diagnosis" not in chem_rec.lower():
        treatment = f"{treatment} [Recommended: {chem_rec}]"

    return {
        "immediate_action": immediate,
        "treatment": treatment,
        "prevention": prevention,
        "monitoring": monitoring,
    }


_qwen_model = None
_qwen_tokenizer = None
_qwen_lock = threading.Lock()


def _get_local_qwen():
    """Lazy-load the local Qwen2.5-1.5B-Instruct model in memory (Only if explicitly enabled on GPU)."""
    global _qwen_model, _qwen_tokenizer
    if _qwen_model is not None and _qwen_tokenizer is not None:
        return _qwen_model, _qwen_tokenizer

    with _qwen_lock:
        if _qwen_model is not None:
            return _qwen_model, _qwen_tokenizer

        model_id = settings.LOCAL_LLM_MODEL
        logger.info("Loading in-memory local LLM (%s) on %s...", model_id, settings.DEVICE)
        from transformers import AutoModelForCausalLM, AutoTokenizer

        _qwen_tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        torch_dtype = torch.bfloat16 if hasattr(torch, "bfloat16") else torch.float32
        _qwen_model = AutoModelForCausalLM.from_pretrained(
            model_id,
            trust_remote_code=True,
            torch_dtype=torch_dtype,
            low_cpu_mem_usage=True,
        ).to(settings.DEVICE).eval()
        logger.info("Local advisory LLM (%s) loaded successfully.", model_id)
        return _qwen_model, _qwen_tokenizer


def _call_local_llm(system_prompt: str, user_prompt: str) -> Optional[dict]:
    """Runs inference on the local Qwen2.5 model (guarded against CPU freezes)."""
    try:
        model, tokenizer = _get_local_qwen()
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )
        model_inputs = tokenizer([text], return_tensors="pt").to(settings.DEVICE)

        with torch.inference_mode():
            generated_ids = model.generate(
                **model_inputs,
                max_new_tokens=220,
                temperature=0.2,
                top_p=0.9,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
            )
            generated_ids = [
                output_ids[len(input_ids):] for input_ids, output_ids in zip(model_inputs.input_ids, generated_ids)
            ]
            response_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0].strip()

        clean = re.sub(r"```(?:json)?", "", response_text).strip()
        match = re.search(r"\{[\s\S]*\}", clean)
        if match:
            return json.loads(match.group(0))
        return json.loads(clean)
    except Exception as exc:
        logger.warning("Local Qwen LLM inference encountered an issue: %s. Relying on verified KB facts.", exc)
        return None


def _call_groq_llm(system_prompt: str, user_prompt: str) -> Optional[dict]:
    """Invokes fast Groq API if configured."""
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
        "engine": "verified_icar_kb" if not settings.USE_LOCAL_LLM else "local_qwen2.5",
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
        tpl = LOW_CONF_DATA.get(lang, LOW_CONF_DATA["en"])
        data = {
            "immediate_action": tpl["immediate_action"].format(crop=crop, conf=conf * 100),
            "treatment": tpl["treatment"],
            "prevention": tpl["prevention"],
            "monitoring": tpl["monitoring"],
            "sources": ["Local KVK / Agriculture Extension Office"],
            "safety_disclaimer": DISCLAIMERS.get(lang, DISCLAIMERS["en"]),
            "language": lang,
        }
        if lang != "en":
            en_tpl = LOW_CONF_DATA["en"]
            data["english"] = {
                "immediate_action": en_tpl["immediate_action"].format(crop=crop, conf=conf * 100),
                "treatment": en_tpl["treatment"],
                "prevention": en_tpl["prevention"],
                "monitoring": en_tpl["monitoring"],
            }
        return data

    # Stage 2: Knowledge Base Lookup with Smart Aliasing & Normalization
    matched_key, kb = _find_kb_entry(crop, disease)
    if not isinstance(kb, dict) or not kb:
        logger.info("No verified KB entry found for %s | %s", crop, disease)
        tpl = UNVERIFIED_DATA.get(lang, UNVERIFIED_DATA["en"])
        data = {
            "immediate_action": tpl["immediate_action"].format(crop=crop, disease=disease),
            "treatment": tpl["treatment"],
            "prevention": tpl["prevention"],
            "monitoring": tpl["monitoring"],
            "sources": ["Local KVK / Extension Guidelines"],
            "safety_disclaimer": DISCLAIMERS.get(lang, DISCLAIMERS["en"]),
            "language": lang,
        }
        if lang != "en":
            en_tpl = UNVERIFIED_DATA["en"]
            data["english"] = {
                "immediate_action": en_tpl["immediate_action"].format(crop=crop, disease=disease),
                "treatment": en_tpl["treatment"],
                "prevention": en_tpl["prevention"],
                "monitoring": en_tpl["monitoring"],
            }
        return data

    # Stage 3: Grounded Advisory Synthesis
    fb = _fallback_fields(kb)
    data = dict(fb)

    # Optional fast LLM synthesis via Groq or GPU local LLM
    llm_result = None
    if settings.GROQ_API_KEY:
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
    elif settings.USE_LOCAL_LLM and settings.DEVICE != "cpu":
        system_prompt = (
            "You are an agricultural advisory assistant for Indian farmers. "
            "Use ONLY the verified facts provided. Never name a chemical, product or dose that is not in the facts. "
            "Write short, simple sentences a farmer can follow, and keep every value under 35 words. "
            "Reply with a JSON object containing keys: immediate_action, treatment, prevention, monitoring."
        )
        user_prompt = f"Verified facts:\n- Crop: {crop}\n- Diagnosis: {disease}\n- Immediate: {fb['immediate_action']}\n- Treatment: {fb['treatment']}\n"
        llm_result = _call_local_llm(system_prompt, user_prompt)

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

    return _package_response(data, lang, kb)


def _package_response(data: dict, lang: str, kb_entry: Optional[dict[str, Any]] = None) -> dict:
    """Translates response with zero-latency precomputed translations and robust fallback."""
    if lang == "en":
        return data

    out = dict(data)
    out["english"] = {k: data[k] for k in FIELDS}
    out["language"] = lang
    out["safety_disclaimer"] = DISCLAIMERS.get(lang, DISCLAIMERS["en"])

    chem_rec = kb_entry.get("chemical_recommendation") if isinstance(kb_entry, dict) else None
    has_chem = bool(chem_rec and "none" not in chem_rec.lower() and "requires local diagnosis" not in chem_rec.lower())

    # 1. Zero-latency instant verified translation from Knowledge Base
    if kb_entry and isinstance(kb_entry, dict):
        trans = kb_entry.get("translations", {}).get(lang)
        if trans and isinstance(trans, dict):
            for k in FIELDS:
                if trans.get(k):
                    out[k] = trans[k]
            if has_chem and out.get("treatment") and "[Recommended:" not in out["treatment"] and "ભલામણ કરેલ:" not in out["treatment"] and "अनुशंसित:" not in out["treatment"]:
                from routers.translation import translate_chemical_recommendation
                rec_label = "ભલામણ કરેલ" if lang == "gu" else "अनुशंसित"
                translated_chem = translate_chemical_recommendation(chem_rec, lang)
                out["treatment"] = f"{out['treatment']} [{rec_label}: {translated_chem}]"
            return out

    # 2. Dynamic in-process translation via IndicTrans2 if needed
    try:
        from routers.translation import translate_texts, translate_treatment_recommendation

        texts_to_translate = [data[k] for k in FIELDS]
        translated = translate_texts(texts_to_translate, lang)

        for k, tr in zip(FIELDS, translated):
            if "[Recommended:" in tr:
                tr = translate_treatment_recommendation(tr, lang)
            out[k] = tr
        return out
    except Exception as exc:
        logger.warning("In-process translation of advisory failed (%s), returning verified English.", exc)
        return out
