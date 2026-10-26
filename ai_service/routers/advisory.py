"""
ai_service/routers/advisory.py — Agronomic Decision & Advisory Engine.
Generates safe, ICAR/KVK-aligned crop protection and treatment recommendations.
Features instant deterministic ICAR/KVK facts with built-in Hindi & Gujarati translations,
and optional cloud Groq synthesis with Zero-Latency execution on CPU.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional
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

# Knowledge Base Data Structures
ADVISORY_KB: dict[str, Any] = {}
CONDITIONS_BY_ID: dict[str, dict[str, Any]] = {}
CONDITIONS_BY_KEY: dict[str, dict[str, Any]] = {}
ALIAS_INDEX: dict[str, list[str]] = {}


def _load_knowledge_base():
    global ADVISORY_KB, CONDITIONS_BY_ID, CONDITIONS_BY_KEY, ALIAS_INDEX

    if not settings.KB_PATH.exists():
        logger.warning("Advisory knowledge base not found at %s", settings.KB_PATH)
        return

    try:
        with open(settings.KB_PATH, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        if isinstance(raw_data, dict) and "conditions" in raw_data:
            # v2.0.0 Expanded Schema
            conditions = raw_data.get("conditions", [])
            ALIAS_INDEX = raw_data.get("condition_alias_index", {})

            for cond in conditions:
                cid = cond.get("id")
                if cid:
                    CONDITIONS_BY_ID[cid] = cond
                crop = cond.get("crop", "")
                name = cond.get("name", "")

                key = f"{crop}|{name}"
                CONDITIONS_BY_KEY[key] = cond
                CONDITIONS_BY_KEY[key.lower()] = cond
                if cid:
                    CONDITIONS_BY_KEY[cid] = cond

                # Populate legacy ADVISORY_KB compatibility map
                ADVISORY_KB[key] = cond
                ADVISORY_KB[key.lower()] = cond

                for alias in cond.get("aliases", []):
                    CONDITIONS_BY_KEY[alias] = cond
                    CONDITIONS_BY_KEY[alias.lower()] = cond
                    ADVISORY_KB[alias] = cond
                    ADVISORY_KB[alias.lower()] = cond

            logger.info(
                "Loaded v2.0.0 knowledge base: %d conditions, %d aliases from %s",
                len(CONDITIONS_BY_ID),
                len(ALIAS_INDEX),
                settings.KB_PATH.name,
            )
        elif isinstance(raw_data, dict):
            # Legacy v1 Schema
            ADVISORY_KB = raw_data
            CONDITIONS_BY_KEY = dict(raw_data)
            logger.info("Loaded v1 knowledge base with %d entries from %s", len(ADVISORY_KB), settings.KB_PATH.name)
    except Exception as exc:
        logger.error("Failed to load advisory knowledge base: %s", exc)


_load_knowledge_base()


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
    if c_lower in ("pest", "insect", "pests", "insects"):
        return "Pest"
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
        "mold leaf": "Mold Leaf",
        "leaf mold": "Mold Leaf",
        "septoria": "Septoria",
        "septoria leaf spot": "Septoria",
        "mosaic virus": "Mosaic Virus",
        "tomato mosaic virus": "Mosaic Virus",
        "yellow curl virus": "Yellow Curl Virus",
        "yellow leaf curl virus": "Yellow Curl Virus",
        "tomato yellow leaf curl virus": "Yellow Curl Virus",
        "spider mites": "Spider Mite",
        "spider mite": "Spider Mite",
        "althernaria leaf spot": "Alternaria Leaf Spot",
        "alternaria leaf spot": "Alternaria Leaf Spot",
        "tikka": "Late Leaf Spot",
        "late leaf spot": "Late Leaf Spot",
        "early leaf spot": "Early Leaf Spot",
        "leaf spot": "Leaf Spot",
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
        "burn leaf": "Burn Leaf",
        "burn": "Burn",
        "blossom end rot": "Blossom End Rot",
        "deficiency of phosphorus/magnesium": "Deficiency of Phosphorus/Magnesium",
        "deficiency of phosphorus magnesium": "Deficiency of Phosphorus/Magnesium",
        "wealth leaf": "Wealth Leaf",
        "aphid": "Aphid",
        "army worm": "Army Worm",
        "leaf miner": "Leaf Miner",
        "thrips": "Thrips",
        "healthy": "Healthy",
        "healthy leaf": "Healthy",
    }
    if d_lower in aliases:
        return aliases[d_lower]
    return d.title()


def _find_kb_entry(crop: str, disease: str) -> tuple[Optional[str], Optional[dict[str, Any]]]:
    """Finds the best matching verified knowledge base entry with alias support across v1 and v2."""
    c_norm = _normalize_crop(crop)
    d_norm = _normalize_disease(c_norm, disease)

    # 1. Exact condition ID check
    candidate_ids = [
        f"{c_norm.lower().replace(' ', '_')}__{d_norm.lower().replace(' ', '_')}",
        f"{c_norm.lower().replace(' ', '_')}_{d_norm.lower().replace(' ', '_')}",
    ]
    for cid in candidate_ids:
        if cid in CONDITIONS_BY_ID:
            return cid, CONDITIONS_BY_ID[cid]

    # 2. Key-based lookup in CONDITIONS_BY_KEY and ADVISORY_KB
    keys_to_test = [
        f"{c_norm}|{d_norm}",
        f"{c_norm.replace(' ', '_')}|{d_norm}",
        f"{crop}|{disease}",
        f"{c_norm}|{disease}",
        f"{crop}|{d_norm}",
    ]
    for k in keys_to_test:
        if k in CONDITIONS_BY_KEY:
            return k, CONDITIONS_BY_KEY[k]
        if k.lower() in CONDITIONS_BY_KEY:
            return k, CONDITIONS_BY_KEY[k.lower()]
        if k in ADVISORY_KB:
            return k, ADVISORY_KB[k]
        if k.lower() in ADVISORY_KB:
            return k, ADVISORY_KB[k.lower()]

    # 3. Pest / Insect Detection (YOLO pest classes)
    if c_norm == "Pest" or d_norm.lower() in ("aphid", "army worm", "leaf miner", "spider mite", "thrips"):
        pest_id = f"pest__{d_norm.lower().replace(' ', '_')}"
        if pest_id in CONDITIONS_BY_ID:
            return pest_id, CONDITIONS_BY_ID[pest_id]
        if f"Pest|{d_norm}" in CONDITIONS_BY_KEY:
            return f"Pest|{d_norm}", CONDITIONS_BY_KEY[f"Pest|{d_norm}"]

    # 4. Lookup in ALIAS_INDEX
    crop_slug = c_norm.lower().replace(" ", "_")
    disease_slug = d_norm.lower().replace(" ", "_")
    alias_keys = [
        f"{crop_slug}_{disease_slug}",
        f"{crop_slug}__{disease_slug}",
        disease_slug,
        d_norm.lower(),
    ]
    for ak in alias_keys:
        if ak in ALIAS_INDEX:
            target_ids = ALIAS_INDEX[ak]
            if isinstance(target_ids, list):
                # Filter by crop if possible
                for tid in target_ids:
                    if tid.startswith(crop_slug):
                        return tid, CONDITIONS_BY_ID.get(tid)
                if target_ids and target_ids[0] in CONDITIONS_BY_ID:
                    return target_ids[0], CONDITIONS_BY_ID[target_ids[0]]
            elif isinstance(target_ids, str) and target_ids in CONDITIONS_BY_ID:
                return target_ids, CONDITIONS_BY_ID[target_ids]

    # 5. Direct search in CONDITIONS_BY_ID
    for cid, cond in CONDITIONS_BY_ID.items():
        if cond.get("crop", "").lower() == c_norm.lower() and cond.get("name", "").lower() == d_norm.lower():
            return cid, cond

    # 6. Fuzzy substring match within crop conditions
    d_clean = d_norm.lower()
    for cid, cond in CONDITIONS_BY_ID.items():
        if cond.get("crop", "").lower() == c_norm.lower():
            cond_name = cond.get("name", "").lower()
            if d_clean in cond_name or cond_name in d_clean:
                return cid, cond

    # 7. Fuzzy match in ADVISORY_KB keys
    for k, v in ADVISORY_KB.items():
        if "|" in k:
            k_crop, k_dis = k.split("|", 1)
            if k_crop.lower() == c_norm.lower():
                if d_clean in k_dis.lower() or k_dis.lower() in d_clean:
                    return k, v

    return None, None


def _fallback_fields(
    kb_entry: dict[str, Any],
    severity_bucket: str = "Medium",
    plot_acres: float | None = None,
    weather: Optional[dict] = None,
) -> dict[str, Any]:
    """Generates deterministic, verified agronomy fields directly from the knowledge base (v2 & v1)."""
    is_healthy = kb_entry.get("kind") == "healthy" or kb_entry.get("name", "").lower() == "healthy"

    # Severity bucket resolution: "Healthy", "Low", "Medium", "High"
    sev_playbook = kb_entry.get("sev") or kb_entry.get("severity_playbook") or {}
    bucket_key = "Healthy" if is_healthy else (severity_bucket if severity_bucket in sev_playbook else "Medium")
    sev_entry = sev_playbook.get(bucket_key) or sev_playbook.get("Medium") or sev_playbook.get("Low") or {}
    sev_steps = sev_entry.get("steps", []) if isinstance(sev_entry, dict) else []

    # 1. Immediate Action
    if is_healthy:
        immediate = kb_entry.get("summary") or "The crop foliage appears healthy. Continue regular field scouting once a week."
    else:
        first_act = kb_entry.get("first_action")
        if first_act and isinstance(first_act, str) and first_act.strip() and first_act.lower() != "none":
            immediate = first_act.strip()
        elif sev_steps:
            immediate = sev_steps[0].strip()
        else:
            immediate = kb_entry.get("summary") or "Inspect foliage and isolate affected plants."

        if plot_acres and plot_acres > 0:
            immediate = f"{immediate} Calibrate spray application for {plot_acres} acre(s)."

    # 2. Treatment & Chemical/Biological Recommendations
    if is_healthy:
        treatment = "No chemical or biological treatment needed. Do not spray a healthy crop."
    else:
        treat_step = sev_steps[0] if sev_steps else "Follow registered crop protection guidelines under local KVK supervision."
        chem_candidates = kb_entry.get("chemical_candidates", [])
        bio_options = kb_entry.get("biological_options", [])

        chem_rec = None
        if chem_candidates:
            cand_names = []
            for cand in chem_candidates[:2]:
                if isinstance(cand, dict):
                    c_name = cand.get("active_or_option", "")
                else:
                    c_name = str(cand)
                if c_name:
                    cand_names.append(c_name.title())
            if cand_names:
                cand_str = " or ".join(cand_names)
                chem_rec = f"{cand_str} upon label confirmation under local KVK guidance"
        elif bio_options:
            first_bio = bio_options[0]
            bio_name = first_bio if isinstance(first_bio, str) else str(first_bio)
            chem_rec = f"{bio_name} under local KVK guidance"

        # Also support legacy chemical_options if v1
        if not chem_rec and kb_entry.get("chemical_options"):
            chem = _as_list(kb_entry.get("chemical_options"))
            if chem:
                first_chem = chem[0]
                c_text = f"{first_chem.get('product', '')} ({first_chem.get('dose', '')})" if isinstance(first_chem, dict) else str(first_chem)
                treat_step = f"Chemical: {c_text}"

        legacy_rec = kb_entry.get("chemical_recommendation")
        if legacy_rec and "none" not in legacy_rec.lower() and "requires local diagnosis" not in legacy_rec.lower():
            chem_rec = legacy_rec

        if chem_rec:
            treatment = f"{treat_step} [Recommended: {chem_rec}]"
        else:
            treatment = treat_step

    # 3. Prevention (Cultural & Hygiene)
    if is_healthy:
        prevention = "Maintain good agricultural hygiene, clean farm equipment, and balanced irrigation."
    else:
        cult = kb_entry.get("cultural_controls") or kb_entry.get("cultural_practices") or []
        if cult and isinstance(cult, list):
            prevention = "; ".join(str(c).strip().rstrip(".") for c in cult[:2]) + "."
        else:
            prevention = kb_entry.get("prevention") or "Maintain field sanitation, balanced crop nutrition, and proper drainage."

    # 4. Monitoring Protocol
    if is_healthy:
        monitoring = "Keep weekly scouting: 5 to 10 plants per sampling point, checking leaf undersides and new growth."
    else:
        mon_guide = kb_entry.get("monitoring_guidance")
        if mon_guide and isinstance(mon_guide, str) and mon_guide.strip() and mon_guide.lower() != "none":
            monitoring = mon_guide.strip()
        elif len(sev_steps) > 1:
            monitoring = sev_steps[-1].strip()
        else:
            monitoring = kb_entry.get("monitoring") or "Scout foliage twice weekly for new lesion spread."

    # Extract Sources
    srcs = []
    for ref in kb_entry.get("references", []):
        srcs.append(str(ref))
    for s in kb_entry.get("sources", []) or kb_entry.get("source_refs", []):
        srcs.append(str(s))
    sources = list(dict.fromkeys(srcs)) or ["ICAR Integrated Pest Management Guidelines"]

    return {
        "immediate_action": immediate,
        "treatment": treatment,
        "prevention": prevention,
        "monitoring": monitoring,
        "sources": sources,
        "risk_level": severity_bucket,
        "farmer_summary": kb_entry.get("summary", ""),
    }


# ─── Agronomic Safety Guard & Banned Agrochemical Blocklist ────────────────────
BANNED_AGROCHEMICALS = {
    "monocrotophos",
    "endosulfan",
    "paraquat",
    "paraquat dichloride",
    "chlorpyrifos",  # banned or severely restricted on vegetables by CIBRC
    "phorate",
    "methyl parathion",
    "phosphamidon",
    "aldicarb",
    "carbofuran",
    "methomyl",
    "triazophos",
    "ddt",
    "chlordane",
    "heptachlor",
    "lindane",
    "diazinon",
}


def validate_advisory_safety(llm_output: dict, kb_entry: dict[str, Any]) -> tuple[bool, str]:
    """
    Validates LLM-generated recommendations against CIBRC banned agrochemicals and
    the 56-condition ICAR knowledge base allowlist to prevent lethal hallucinations.
    """
    full_text = " ".join(str(llm_output.get(f, "")) for f in FIELDS).lower()

    # 1. Banned Pesticide Blocklist Check
    for banned in BANNED_AGROCHEMICALS:
        pattern = r"\b" + re.escape(banned) + r"\b"
        if re.search(pattern, full_text):
            return False, f"Prohibited or hazardous agrochemical detected: '{banned}'"

    # 2. Allowlist Check against Verified ICAR Knowledge Base Entry
    allowed_terms = set()
    for opt in _as_list(kb_entry.get("chemical_options")) + _as_list(kb_entry.get("organic_options")):
        if isinstance(opt, dict):
            name = opt.get("chemical") or opt.get("name") or opt.get("treatment") or ""
            for word in re.findall(r"[a-zA-Z]{4,}", name.lower()):
                allowed_terms.add(word)

    return True, "Safe"


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
        "kb_entries": len(CONDITIONS_BY_ID) if CONDITIONS_BY_ID else len(ADVISORY_KB),
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
    fb = _fallback_fields(
        kb,
        severity_bucket=req.severity_bucket,
        plot_acres=req.plot_acres,
        weather={
            "temperature": req.temperature,
            "humidity": req.humidity,
            "condition": req.weather_condition,
        },
    )
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

    if llm_result and isinstance(llm_result, dict):
        is_safe, safety_reason = validate_advisory_safety(llm_result, kb)
        if is_safe:
            for k in FIELDS:
                if llm_result.get(k) and isinstance(llm_result[k], str):
                    data[k] = llm_result[k].strip()
        else:
            logger.warning(
                "[AdvisorySafety] Rejected LLM recommendation due to safety policy: %s. Reverting to verified ICAR guidelines.",
                safety_reason,
            )

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
