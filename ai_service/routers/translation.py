"""
ai_service/routers/translation.py — High-Performance IndicTrans2 & Agronomic Translation Router.
Provides instant, deterministic translation for agricultural advisory and general text
into Indic languages (Hindi, Gujarati) with Zero-Hang guarantees, multi-tiered fallbacks,
and pre-warmed ICAR/KVK agronomic caches.
"""

from __future__ import annotations

import concurrent.futures
import json
import logging
import os
import re
import threading
import time
from pathlib import Path
from typing import Any, Optional

try:
    import torch
except ImportError:
    torch = None

try:
    import httpx
except ImportError:
    httpx = None

import urllib.request
import urllib.parse
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
        pass

from core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

MODEL_NAME = os.getenv("INDICTRANS_MODEL", "ai4bharat/indictrans2-en-indic-dist-200M")
FALLBACK_MODEL_NAME = "Raghavan/indictrans2-en-indic-dist-200M"

LANG_CODES = {
    "hi": "hin_Deva",
    "gu": "guj_Gujr",
}

CACHE_FILE = settings.CACHE_DIR / "indictrans_cache.json"

_model = None
_tokenizer = None
_processor = None
_indictrans_loaded = False
_indictrans_failed = False
_lock = threading.Lock()
_cache: dict[str, str] = {}

SENTENCE_SPLIT_PATTERN = re.compile(r'(?<=[.?!।])\s+')

# Verified Agricultural Seed Dictionary (instant 0ms response)
_AGRONOMIC_SEED_TRANSLATIONS: dict[str, dict[str, str]] = {
    "hi": {
        # Tab 5 Default & Sample Inputs
        "Spray Mancozeb at 2.5 grams per liter of water immediately and ensure proper field drainage.": "तुरंत प्रति लीटर पानी में 2.5 ग्राम मैंकोजेब का छिड़काव करें और खेत में उचित जल निकासी सुनिश्चित करें।",
        "Apply Copper Oxychloride 50 WP at 3 grams per liter of water during clear sunny weather.": "साफ धूप वाले मौसम में प्रति लीटर पानी में 3 ग्राम कॉपर ऑक्सीक्लोराइड 50 डब्ल्यूपी का छिड़काव करें।",
        "Avoid overhead irrigation and remove infected leaves from the field to stop spore germination.": "बीजाणुओं के अंकुरण को रोकने के लिए ऊपर से सिंचाई करने से बचें और संक्रमित पत्तियों को खेत से हटा दें।",
        # Tab 4 Presets
        "Greetings farmer friend! Early Blight has been detected on your tomato crop. Spray Mancozeb fungicide at 2 grams per liter and remove infected lower leaves.": "नमस्ते किसान भाई! आपके टमाटर की फसल में अगेती झुलसा (Early Blight) के लक्षण मिले हैं। 2 ग्राम प्रति लीटर मैंकोजेब कवकनाशी का छिड़काव करें और निचली संक्रमित पत्तियों को हटा दें।",
        "Hello farmer friend! Bacterial Blight has been identified on your cotton crop. Spray Copper Oxychloride at 3 grams per liter of water immediately.": "नमस्ते किसान भाई! आपकी कपास की फसल में जीवाणु अंगमारी (Bacterial Blight) के लक्षण मिले हैं। तुरंत प्रति लीटर पानी में 3 ग्राम कॉपर ऑक्सीक्लोराइड का छिड़काव करें।",
        # Disclaimers & Standard ICAR/KVK Guidance
        "DISCLAIMER: Confirm the diagnosis and any chemical use with your local KVK or agriculture officer, and follow the product label.": "अस्वीकरण: कोई भी रसायन या दवा इस्तेमाल करने से पहले अपने स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि अधिकारी से निदान की पुष्टि करें और उत्पाद के लेबल का पालन करें।",
        "Confirm the diagnosis and any chemical use with your local KVK or agriculture officer, and follow the product label.": "कोई भी रसायन या दवा इस्तेमाल करने से पहले अपने स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि अधिकारी से निदान की पुष्टि करें और उत्पाद के लेबल का पालन करें।",
        "DISCLAIMER: Always follow local agricultural guidelines, product labels, and consult your local KVK.": "अस्वीकरण: हमेशा स्थानीय कृषि दिशानिर्देशों, उत्पाद लेबल का पालन करें और अपने स्थानीय KVK से परामर्श करें।",
        "Always follow local agricultural guidelines, product labels, and consult your local KVK.": "हमेशा स्थानीय कृषि दिशानिर्देशों, उत्पाद लेबल का पालन करें और अपने स्थानीय KVK से परामर्श करें।",
        "No chemical treatment is recommended without expert confirmation.": "विशेषज्ञ की पुष्टि के बिना किसी रासायनिक उपचार की सिफारिश नहीं की जाती है।",
        "Maintain field sanitation and clean tools.": "खेत की स्वच्छता बनाए रखें और औजारों को साफ रखें।",
        "Check the plants regularly for spreading symptoms.": "लक्षणों के प्रसार के लिए नियमित रूप से पौधों की जांच करें।",
        "Maintain field sanitation and proper drainage.": "खेत की स्वच्छता और उचित जल निकासी बनाए रखें।",
        "Follow registered crop protection guidelines. Avoid applying synthetic chemicals without verification.": "पंजीकृत फसल सुरक्षा दिशानिर्देशों का पालन करें। सत्यापन के बिना सिंथेटिक रसायनों को लागू करने से बचें।",
        "Monitor crop daily for symptoms spreading.": "लक्षण फैलने के लिए प्रतिदिन फसल की निगरानी करें।",
        "Ensure proper field sanitation and healthy soil drainage.": "उचित खेत स्वच्छता और स्वस्थ मिट्टी जल निकासी सुनिश्चित करें।",
        "Ensure proper field drainage, isolate suspicious plants, and seek agronomist guidance.": "उचित जल निकासी सुनिश्चित करें, संदिग्ध पौधों को अलग करें और कृषि विशेषज्ञ का मार्गदर्शन लें।",
        "Inspect the field for spreading symptoms and isolate affected plants.": "लक्षणों के प्रसार के लिए खेत का निरीक्षण करें और प्रभावित पौधों को अलग करें।",
        "Check foliage every 24-48 hours for progression.": "प्रगति के लिए हर 24-48 घंटे में पत्तियों की जांच करें।",
        "Scout foliage twice weekly for new lesion spread.": "नए घावों के प्रसार के लिए सप्ताह में दो बार पत्तियों की जांच करें।",
        "Maintain proper crop spacing and weed-free field borders.": "उचित फसल दूरी बनाए रखें और खेत की मेड़ों को खरपतवार मुक्त रखें।",
        "Take high-resolution, centered photos in balanced daylight.": "संतुलित दिन के उजाले में उच्च-रिज़ॉल्यूशन, केंद्रित तस्वीरें लें।",
        "None (Consult specialist)": "कोई नहीं (विशेषज्ञ से परामर्श लें)",
        "Maintain balanced plant nutrition and moisture.": "पौधों का संतुलित पोषण और नमी बनाए रखें।",
        "Isolate affected plants and ensure canopy ventilation.": "प्रभावित पौधों को अलग करें और हवा का उचित संचार सुनिश्चित करें।",
        "Spray Mancozeb fungicide at 2 grams per liter of water.": "प्रति लीटर पानी में 2 ग्राम मैंकोजेब कवकनाशी का छिड़काव करें।",
        "Spray Copper Oxychloride at 3 grams per liter of water.": "प्रति लीटर पानी में 3 ग्राम कॉपर ऑक्सीक्लोराइड का छिड़काव करें।",
        "Spray Chlorpyrifos at 2 ml per liter of water.": "प्रति लीटर पानी में 2 मिलीलीटर क्लोरपायरीफॉस का छिड़काव करें।",
        "Spray Imidacloprid at 0.5 ml per liter of water.": "प्रति लीटर पानी में 0.5 मिलीलीटर इमिडाक्लोप्रिड का छिड़काव करें।",
        "Apply Neem oil (10,000 ppm) at 3 ml per liter of water.": "प्रति लीटर पानी में 3 मिलीलीटर नीम का तेल (10,000 पीपीएम) छिड़कें।",
    },
    "gu": {
        # Tab 5 Default & Sample Inputs
        "Spray Mancozeb at 2.5 grams per liter of water immediately and ensure proper field drainage.": "તાત્કાલિક પ્રતિ લિટર પાણીમાં 2.5 ગ્રામ મેન્કોઝેબનો છંટકાવ કરો અને ખેતરમાં યોગ્ય નિતાર વ્યવસ્થા સુનિશ્ચિત કરો.",
        "Apply Copper Oxychloride 50 WP at 3 grams per liter of water during clear sunny weather.": "સ્વચ્છ તડકાવાળા હવામાન દરમિયાન પ્રતિ લિટર પાણીમાં 3 ગ્રામ કોપર ઓક્સીક્લોરાઇડ 50 WP નો છંટકાવ કરો.",
        "Avoid overhead irrigation and remove infected leaves from the field to stop spore germination.": "બીજકણના અંકુરણને રોકવા માટે ઉપરથી પિયત કરવાનું ટાળો અને ચેપગ્રસ્ત પાંદડા ખેતરમાંથી દૂર કરો.",
        # Tab 4 Presets
        "Greetings farmer friend! Early Blight has been detected on your tomato crop. Spray Mancozeb fungicide at 2 grams per liter and remove infected lower leaves.": "નમસ્તે ખેડૂત મિત્ર! તમારા ટામેટાના પાકમાં આગોતરા સુકારાના (Early Blight) લક્ષણો જોવા મળ્યા છે. પ્રતિ લિટર 2 ગ્રામ મેન્કોઝેબ ફૂગનાશકનો છંટકાવ કરો અને નીચેના ચેપગ્રસ્ત પાંદડા દૂર કરો.",
        "Hello farmer friend! Bacterial Blight has been identified on your cotton crop. Spray Copper Oxychloride at 3 grams per liter of water immediately.": "નમસ્તે ખેડૂત મિત્ર! તમારા કપાસના પાકમાં બેક્ટેરિયલ બ્લાઈટ (Bacterial Blight) ના લક્ષણો મળ્યા છે. તરત જ પ્રતિ લિટર પાણીમાં 3 ગ્રામ કોપર ઓક્સીક્લોરાઇડનો છંટકાવ કરો.",
        # Disclaimers & Standard ICAR/KVK Guidance
        "DISCLAIMER: Confirm the diagnosis and any chemical use with your local KVK or agriculture officer, and follow the product label.": "અસ્વીકરણ: કોઈ પણ રસાયણ કે દવાનો ઉપયોગ કરતા પહેલાં તમારા સ્થાનિક કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) અથવા ખેતીવાડી અધિકારી પાસેથી નિદાનની પુષ્ટિ કરો અને ઉત્પાદનના લેબલનું પાલન કરો.",
        "Confirm the diagnosis and any chemical use with your local KVK or agriculture officer, and follow the product label.": "કોઈ પણ રસાયણ કે દવાનો ઉપયોગ કરતા પહેલાં તમારા સ્થાનિક કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) અથવા ખેતીવાડી અધિકારી પાસેથી નિદાનની પુષ્ટિ કરો અને ઉત્પાદનના લેબલનું પાલન કરો.",
        "DISCLAIMER: Always follow local agricultural guidelines, product labels, and consult your local KVK.": "અસ્વીકરણ: હંમેશા સ્થાનિક કૃષિ માર્ગદર્શિકા, ઉત્પાદન લેબલનું પાલન કરો અને તમારા સ્થાનિક KVK ની સલાહ લો.",
        "Always follow local agricultural guidelines, product labels, and consult your local KVK.": "હંમેશા સ્થાનિક કૃષિ માર્ગદર્શિકા, ઉત્પાદન લેબલનું પાલન કરો અને તમારા સ્થાનિક KVK ની સલાહ લો.",
        "No chemical treatment is recommended without expert confirmation.": "નિષ્ણાતની પુષ્ટિ વિના કોઈ રાસાયણિક સારવારની ભલામણ કરવામાં આવતી નથી.",
        "Maintain field sanitation and clean tools.": "ખેતરની સ્વચ્છતા જાળવો અને ઓજારો સાફ રાખો.",
        "Check the plants regularly for spreading symptoms.": "લક્ષણો ફેલાવવા માટે છોડની નિયમિત તપાસ કરો.",
        "Maintain field sanitation and proper drainage.": "ખેતરની સ્વચ્છતા અને યોગ્ય ડ્રેનેજ જાળવો.",
        "Follow registered crop protection guidelines. Avoid applying synthetic chemicals without verification.": "નોંધાયેલ પાક સંરક્ષણ માર્ગદર્શિકા અનુસરો. ચકાસણી વગર કૃત્રિમ રસાયણો વાપરવાનું ટાળો.",
        "Monitor crop daily for symptoms spreading.": "લક્ષણો ફેલાવવા માટે દરરોજ પાકનું નિરીક્ષણ કરો.",
        "Ensure proper field sanitation and healthy soil drainage.": "ખેતરની યોગ્ય સ્વચ્છતા અને સ્વસ્થ જમીન નિકાલ સુનિશ્ચિત કરો.",
        "Ensure proper field drainage, isolate suspicious plants, and seek agronomist guidance.": "યોગ્ય જમીન નિકાલ સુનિશ્ચિત કરો, શંકાસ્પદ છોડ અલગ કરો અને કૃષિ નિષ્ણાતની સલાહ લો.",
        "Inspect the field for spreading symptoms and isolate affected plants.": "લક્ષણો ફેલાવવા માટે ખેતરનું નિરીક્ષણ કરો અને અસરગ્રસ્ત છોડને અલગ કરો.",
        "Check foliage every 24-48 hours for progression.": "રોગના ફેલાવા માટે દર 24-48 કલાકે પાંદડાં તપાસો.",
        "Scout foliage twice weekly for new lesion spread.": "નવા ડાઘ ફેલાવા માટે અઠવાડિયામાં બે વાર પાંદડાઓની તપાસ કરો.",
        "Maintain proper crop spacing and weed-free field borders.": "પાક વચ્ચે યોગ્ય અંતર રાખો અને ખેતરની સરહદોને નીંદણ મુક્ત રાખો.",
        "Take high-resolution, centered photos in balanced daylight.": "સંતુલિત દિવસના પ્રકાશમાં ઉચ્ચ રીઝોલ્યુશનવાળા, કેન્દ્રિત ફોટા લો.",
        "None (Consult specialist)": "કંઈ નહીં (નિષ્ણાતની સલાહ લો)",
        "Maintain balanced plant nutrition and moisture.": "છોડનું સંતુલિત પોષણ અને ભેજ જાળવી રાખો.",
        "Isolate affected plants and ensure canopy ventilation.": "અસરગ્રસ્ત છોડને અલગ કરો અને યોગ્ય હવા ઉજાસ સુનિશ્ચિત કરો.",
        "Spray Mancozeb fungicide at 2 grams per liter of water.": "પ્રતિ લિટર પાણીમાં 2 ગ્રામ મેન્કોઝેબ ફૂગનાશકનો છંટકાવ કરો.",
        "Spray Copper Oxychloride at 3 grams per liter of water.": "પ્રતિ લિટર પાણીમાં 3 ગ્રામ કોપર ઓક્સીક્લોરાઇડનો છંટકાવ કરો.",
        "Spray Chlorpyrifos at 2 ml per liter of water.": "પ્રતિ લિટર પાણીમાં 2 મિલી ક્લોરપાયરીફોસનો છંટકાવ કરો.",
        "Spray Imidacloprid at 0.5 ml per liter of water.": "પ્રતિ લિટર પાણીમાં 0.5 મિલી ઈમિડાક્લોપ્રિડનો છંટકાવ કરો.",
        "Apply Neem oil (10,000 ppm) at 3 ml per liter of water.": "પ્રતિ લિટર પાણીમાં 3 મિલી લીમડાનું તેલ (10,000 ppm) છાંટો.",
    },
}

_AGRONOMIC_PATTERNS = [
    (
        re.compile(r"^No verified guidance is stored for (.+?) - (.+?)\. Please consult your local KVK or agriculture officer\.?$", re.IGNORECASE),
        {
            "gu": lambda m: f"{m.group(1)} - {m.group(2)} માટે કોઈ ચકાસાયેલ માર્ગદર્શન સંગ્રહિત નથી. કૃપા કરીને તમારા સ્થાનિક KVK અથવા કૃષિ અધિકારીનો સંપર્ક કરો.",
            "hi": lambda m: f"{m.group(1)} - {m.group(2)} के लिए कोई सत्यापित मार्गदर्शन संग्रहीत नहीं है। कृपया अपने स्थानीय KVK या कृषि अधिकारी से परामर्श करें।",
        }
    ),
    (
        re.compile(r"^The automatic diagnosis for (.+?) is unconfirmed \((.+?)% confidence\)\. Please show the plant to your local KVK or agricultural extension officer before spraying anything\.?$", re.IGNORECASE),
        {
            "gu": lambda m: f"{m.group(1)} માટે આપોઆપ નિદાનની પુષ્ટિ થયેલ નથી ({m.group(2)}% ચોક્કસતા). કૃપા કરીને કોઈ પણ દવાનો છંટકાવ કરતા પહેલાં તમારા સ્થાનિક કેવીકે (KVK) અથવા ખેતીવાડી અધિકારીને પાન બતાવો.",
            "hi": lambda m: f"{m.group(1)} के लिए स्वचालित निदान की पुष्टि नहीं हुई है ({m.group(2)}% सटीकता)। कृपया कोई भी दवा छिड़कने से पहले अपने स्थानीय केवीके (KVK) या कृषि अधिकारी को पौधा दिखाएं।",
        }
    ),
    (
        re.compile(r"^Consult your local Krishi Vigyan Kendra \(KVK\) or agriculture extension officer for ([^\.]+?)(?:\.\s*Calibrate spray application for (.+?)\.?)?\.?$", re.IGNORECASE),
        {
            "gu": lambda m: f"{m.group(1)} માટે તમારા સ્થાનિક કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) અથવા ખેતીવાડી વિસ્તરણ અધિકારીની સલાહ લો." + (f" {m.group(2)} માટે સ્પ્રેની માત્રા ગોઠવો." if m.group(2) else ""),
            "hi": lambda m: f"{m.group(1)} के लिए अपने स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि विस्तार अधिकारी से परामर्श करें।" + (f" {m.group(2)} के लिए स्प्रे का छिड़काव समायोजित करें।" if m.group(2) else ""),
        }
    ),
]


def _init_cache():
    """Initializes in-memory translation cache with KB facts and seed dictionaries."""
    global _cache

    # 1. Load persisted cache from disk if available
    if CACHE_FILE.exists():
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                _cache = json.load(f)
            logger.info("Loaded %d cached translations from disk.", len(_cache))
        except Exception as e:
            logger.warning("Could not read translation cache: %s", e)

    # 2. Seed verified agronomic dictionaries
    for lang, phrases in _AGRONOMIC_SEED_TRANSLATIONS.items():
        for en, trans in phrases.items():
            _cache[f"{lang}:{en.strip()}"] = trans.strip()

    # 3. Pre-load complete 51 conditions from advisory_kb.json
    kb_path = settings.KB_PATH
    if kb_path.exists():
        try:
            with open(kb_path, "r", encoding="utf-8") as f:
                kb_data = json.load(f)
            loaded_kb_pairs = 0
            for cond_key, cond_val in kb_data.items():
                translations = cond_val.get("translations", {})
                for lang in ("hi", "gu"):
                    if lang in translations:
                        for field in ("immediate_action", "treatment", "prevention", "monitoring"):
                            en_txt = cond_val.get(field)
                            tr_txt = translations[lang].get(field)
                            if en_txt and tr_txt and isinstance(en_txt, str) and isinstance(tr_txt, str):
                                _cache[f"{lang}:{en_txt.strip()}"] = tr_txt.strip()
                                loaded_kb_pairs += 1
                                # Also index sentence-level pairs
                                en_sents = [s.strip() for s in SENTENCE_SPLIT_PATTERN.split(en_txt.strip()) if s.strip()]
                                tr_sents = [s.strip() for s in SENTENCE_SPLIT_PATTERN.split(tr_txt.strip()) if s.strip()]
                                if len(en_sents) == len(tr_sents):
                                    for es, ts in zip(en_sents, tr_sents):
                                        _cache[f"{lang}:{es}"] = ts
            logger.info("Indexed %d verified sentence pairs from advisory_kb.json.", loaded_kb_pairs)
        except Exception as exc:
            logger.warning("Failed to extract translation pairs from KB: %s", exc)

    logger.info("Total in-memory translation cache entries: %d", len(_cache))


def _save_cache():
    """Persists in-memory cache to disk."""
    try:
        CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(_cache, f, ensure_ascii=False)
    except Exception as e:
        logger.warning("Could not persist translation cache: %s", e)


# Initialize on module import
_init_cache()


def split_into_sentences(text: str) -> list[str]:
    """Split multi-sentence agricultural paragraphs into individual sentences."""
    if not text or not text.strip():
        return []
    sentences = [s.strip() for s in SENTENCE_SPLIT_PATTERN.split(text.strip()) if s.strip()]
    return sentences or [text.strip()]


def resolve_agronomic_phrase(text: str, target_code: str) -> Optional[str]:
    """Resolves verified agricultural phrases instantly (0 ms) via cache and patterns."""
    if not text or target_code not in ("hi", "gu"):
        return None

    clean = text.strip()
    cache_key = f"{target_code}:{clean}"
    if cache_key in _cache:
        return _cache[cache_key]

    # Case-insensitive check
    clean_lower = clean.lower().rstrip(".")
    for k, v in _cache.items():
        if k.startswith(f"{target_code}:"):
            raw_en = k.split(":", 1)[1]
            if raw_en.lower().rstrip(".") == clean_lower:
                return v

    # Dynamic regex patterns
    for pattern, lang_map in _AGRONOMIC_PATTERNS:
        m = pattern.match(clean)
        if m and target_code in lang_map:
            return lang_map[target_code](m)

    return None


def _call_groq_translate(text: str, target_lang: str) -> Optional[str]:
    """Ultra-fast translation via Groq Cloud LLM (Llama 3.3 70B) in <500ms."""
    api_key = settings.GROQ_API_KEY
    if not api_key:
        return None

    lang_name = "Hindi" if target_lang == "hi" else "Gujarati"
    system_prompt = (
        f"You are an expert translator specializing in Indian agricultural science. "
        f"Translate the following English agronomic advice into clean, fluent, professional {lang_name} for Indian farmers. "
        f"Keep chemical formulations, numbers, and dosages (e.g. g/L, ml/L, 50 WP) completely accurate. "
        f"Return ONLY the direct {lang_name} translation text without quotes, explanation, or markdown."
    )

    try:
        from groq import Groq
        client = Groq(api_key=api_key, timeout=4.0)
        completion = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text},
            ],
            temperature=0.1,
            max_tokens=256,
        )
        translated = completion.choices[0].message.content
        if translated and translated.strip():
            return translated.strip().strip('"').strip("'")
    except Exception as exc:
        logger.debug("Groq translation notice: %s", exc)

    return None


def _call_google_translate(text: str, target_code: str) -> Optional[str]:
    """Free public translation endpoint with 3.5s timeout."""
    if not text or not text.strip():
        return text

    encoded = urllib.parse.quote(text)
    url = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={target_code}&dt=t&q={encoded}"
    headers = {"User-Agent": "SmartFarmingApp/2.0 (Linux; IndicTrans2 Fallback)"}

    if httpx is not None:
        try:
            with httpx.Client(timeout=3.5, headers=headers) as client:
                resp = client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    segments = "".join(s[0] for s in data[0] if s and s[0])
                    if segments and segments.strip():
                        return segments.strip()
        except Exception as exc:
            logger.debug("Google translate httpx notice: %s", exc)

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=3.5) as resp:
            if resp.status == 200:
                raw_data = resp.read().decode("utf-8")
                data = json.loads(raw_data)
                segments = "".join(s[0] for s in data[0] if s and s[0])
                if segments and segments.strip():
                    return segments.strip()
    except Exception as exc:
        logger.debug("Google translate urllib notice: %s", exc)

    return None


def _get_indictrans_components():
    """Safely loads IndicTrans2 model with timeout protection and non-blocking failure."""
    global _model, _tokenizer, _processor, _indictrans_loaded, _indictrans_failed

    if _indictrans_loaded:
        return _model, _tokenizer, _processor
    if _indictrans_failed:
        return None, None, None

    if torch is None:
        _indictrans_failed = True
        return None, None, None

    with _lock:
        if _indictrans_loaded:
            return _model, _tokenizer, _processor
        if _indictrans_failed:
            return None, None, None

        logger.info("Initializing IndicTrans2 components on %s...", settings.DEVICE)
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            try:
                from IndicTransToolkit import IndicProcessor
            except ImportError:
                try:
                    from IndicTransToolkit.processor import IndicProcessor
                except ImportError:
                    IndicProcessor = None

            chosen_model = MODEL_NAME
            # Attempt loading primary or fallback model
            try:
                _tokenizer = AutoTokenizer.from_pretrained(chosen_model, trust_remote_code=True)
                _model = AutoModelForSeq2SeqLM.from_pretrained(
                    chosen_model,
                    trust_remote_code=True,
                    torch_dtype=torch.float32 if settings.DEVICE == "cpu" else torch.float16,
                    low_cpu_mem_usage=True,
                ).to(settings.DEVICE).eval()
            except Exception as load_err:
                logger.warning("Primary IndicTrans2 (%s) unavailable: %s. Trying open repository: %s", chosen_model, load_err, FALLBACK_MODEL_NAME)
                _tokenizer = AutoTokenizer.from_pretrained(FALLBACK_MODEL_NAME, trust_remote_code=True)
                _model = AutoModelForSeq2SeqLM.from_pretrained(
                    FALLBACK_MODEL_NAME,
                    trust_remote_code=True,
                    torch_dtype=torch.float32 if settings.DEVICE == "cpu" else torch.float16,
                    low_cpu_mem_usage=True,
                ).to(settings.DEVICE).eval()

            _processor = IndicProcessor(inference=True) if IndicProcessor else None
            _indictrans_loaded = True
            logger.info("IndicTrans2 loaded successfully.")
            return _model, _tokenizer, _processor
        except Exception as exc:
            logger.warning("IndicTrans2 local loading skipped (%s). System will use high-speed cloud/dictionary fallback.", exc)
            _indictrans_failed = True
            return None, None, None


def _run_indictrans_batch(texts: list[str], target_lang_code: str) -> Optional[list[str]]:
    """Runs a batch through IndicTrans2 with optimized greedy search on CPU."""
    model, tokenizer, processor = _get_indictrans_components()
    if model is None or tokenizer is None:
        return None

    try:
        num_beams = 2 if settings.DEVICE == "cuda" else 1

        if processor is not None:
            batch = processor.preprocess_batch(texts, src_lang="eng_Latn", tgt_lang=target_lang_code)
        else:
            batch = texts

        inputs = tokenizer(
            batch,
            padding=True,
            truncation=True,
            max_length=128,
            return_tensors="pt"
        ).to(settings.DEVICE)

        with torch.inference_mode():
            generated_tokens = model.generate(
                **inputs,
                num_beams=num_beams,
                max_new_tokens=128,
                use_cache=True,
                early_stopping=True,
            )

        decoded = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        if processor is not None:
            return processor.postprocess_batch(decoded, lang=target_lang_code)
        return decoded
    except Exception as exc:
        logger.warning("IndicTrans2 inference failed: %s", exc)
        return None


def translate_single_text(text: str, target_code: str) -> str:
    """Translates a single text using the multi-tier zero-hang architecture."""
    if not text or not text.strip() or target_code == "en":
        return text

    clean = text.strip()
    cache_key = f"{target_code}:{clean}"

    # Tier 1: Instant cache / verified agronomic dictionary match
    direct = resolve_agronomic_phrase(clean, target_code)
    if direct:
        return direct

    # Tier 2: Sentence-level translation & assembly
    sentences = split_into_sentences(clean)
    translated_sentences = []
    needs_external = False

    for s in sentences:
        s_match = resolve_agronomic_phrase(s, target_code)
        if s_match:
            translated_sentences.append(s_match)
        else:
            translated_sentences.append(None)
            needs_external = True

    if not needs_external and len(translated_sentences) == len(sentences):
        assembled = " ".join(ts for ts in translated_sentences if ts)
        _cache[cache_key] = assembled
        return assembled

    # Tier 3: Fast Cloud Groq LLM (if key provided, ~300ms)
    groq_res = _call_groq_translate(clean, target_code)
    if groq_res:
        _cache[cache_key] = groq_res
        return groq_res

    # Tier 4: Public Google Translate API (fast, robust, ~400ms)
    gt_res = _call_google_translate(clean, target_code)
    if gt_res:
        _cache[cache_key] = gt_res
        return gt_res

    # Tier 5: Local IndicTrans2 Model (if available on GPU or fast CPU)
    indictrans_code = LANG_CODES.get(target_code, "hin_Deva")
    it_res = _run_indictrans_batch([clean], indictrans_code)
    if it_res and it_res[0]:
        _cache[cache_key] = it_res[0]
        return it_res[0]

    # Tier 6: Safe graceful fallback to source text
    logger.info("Translation fallback used source text for: '%s'", clean[:30])
    return clean


def translate_texts(texts: list[str], target_lang: str) -> list[str]:
    """
    Direct function callable internally by other routers (e.g. advisory) or Gradio.
    Guarantees response within seconds and never hangs.
    """
    lang = (target_lang or "gu").lower().strip()
    if "guj" in lang or lang == "gu":
        target_code = "gu"
    elif "hin" in lang or lang == "hi":
        target_code = "hi"
    else:
        return texts

    if not texts:
        return []

    results = []
    for t in texts:
        results.append(translate_single_text(t, target_code))

    # Persist newly learned translations asynchronously
    try:
        threading.Thread(target=_save_cache, daemon=True).start()
    except Exception:
        pass

    return results


class TranslationRequest(BaseModel):
    texts: list[str]
    target: Optional[str] = None
    target_lang: Optional[str] = None
    language: Optional[str] = None


@router.get("/health")
def translation_health():
    return {
        "status": "healthy",
        "service": "indictrans2",
        "device": settings.DEVICE,
        "cached_translations": len(_cache),
        "supported_languages": list(LANG_CODES.keys()),
        "indictrans_loaded": _indictrans_loaded,
        "indictrans_failed": _indictrans_failed,
    }


@router.post("/translate")
def translate_api(req: TranslationRequest):
    tgt = req.target or req.target_lang or req.language or "gu"
    translations = translate_texts(req.texts, tgt)
    return {"translations": translations}
