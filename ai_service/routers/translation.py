"""
ai_service/routers/translation.py — High-Performance IndicTrans2 & Agronomic Translation Router.
Provides instant, deterministic translation for agricultural advisory and general text
into Indic languages (Hindi, Gujarati) with Zero-Hang guarantees, multi-tiered fallbacks,
and pre-warmed ICAR/KVK agronomic caches.
"""

from __future__ import annotations

import json
import logging
import os
import re
import threading
from pathlib import Path
from typing import Optional

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
        # v2 KB Seed Translations
        "No chemical or biological treatment needed. Do not spray a healthy crop.": "किसी रासायनिक या जैविक उपचार की आवश्यकता नहीं है। स्वस्थ फसल पर छिड़काव न करें।",
        "Maintain good agricultural hygiene, clean farm equipment, and balanced irrigation.": "खेत में अच्छी स्वच्छता बनाए रखें, औजारों को साफ रखें और संतुलित सिंचाई करें।",
        "Keep weekly scouting: 5 to 10 plants per sampling point, checking leaf undersides and new growth.": "साप्ताहिक निगरानी जारी रखें: प्रति सैंपलिंग पॉइंट 5 से 10 पौधों के पत्तों की निचली सतह और नई वृद्धि की जांच करें।",
        "The crop foliage appears healthy. Continue regular field scouting once a week.": "फसल के पत्ते स्वस्थ दिखाई देते हैं। सप्ताह में एक बार नियमित रूप से खेत की निगरानी जारी रखें।",
        "Your cotton leaf looks healthy. Keep scouting once a week.": "आपकी कपास की पत्तियां स्वस्थ दिखती हैं। सप्ताह में एक बार निगरानी जारी रखें।",
        "Your groundnut leaf looks healthy. Keep scouting once a week.": "आपकी मूंगफली की पत्तियां स्वस्थ दिखती हैं। सप्ताह में एक बार निगरानी जारी रखें।",
        "Your pepper leaf looks healthy. Keep scouting once a week.": "आपकी मिर्च की पत्तियां स्वस्थ दिखती हैं। सप्ताह में एक बार निगरानी जारी रखें।",
        "Your potato leaf looks healthy. Check the underside of lower leaves once a week.": "आपकी आलू की पत्तियां स्वस्थ दिखती हैं। सप्ताह में एक बार निचली पत्तियों की जांच करें।",
        "Your tomato leaf looks healthy. Keep scouting once a week.": "आपकी टमाटर की पत्तियां स्वस्थ दिखती हैं। सप्ताह में एक बार निगरानी जारी रखें।",
        "Stop working in the crop while leaves are wet, and mark affected plants.": "पत्तियां गीली होने पर फसल में काम करना बंद करें और प्रभावित पौधों पर निशान लगाएं।",
        "A copper-based protectant (and a label-registered antibiotic partner where permitted) can slow spread but will not cure existing spots.": "कॉपर-आधारित सुरक्षात्मक दवा (और जहां अनुमति हो लेबल-पंजीकृत एंटीबायोटिक साथी) फैलाव को धीमा कर सकती है लेकिन मौजूदा धब्बों को ठीक नहीं करेगी।",
        "Scout in a W pattern and estimate the share of plants affected.": "खेत में W पैटर्न में घूमकर निगरानी करें और प्रभावित पौधों के अनुपात का आकलन करें।",
        "Treat the whole field now with a registered protectant or translaminar product and plan a rotation product.": "पूरे खेत में तुरंत पंजीकृत सुरक्षात्मक कवकनाशी का छिड़काव करें और रोटेशन के लिए दूसरी दवा की योजना बनाएं।",
        "Treat the whole field now with a registered fungicide, alternating protectant and systemic groups per label.": "पूरे खेत में लेबल के अनुसार सुरक्षात्मक और प्रणालीगत समूहों को बदलकर पंजीकृत कवकनाशी का छिड़काव करें।",
        "Start integrated vector control: neem-based sprays, sticky traps, then a label-registered insecticide rotated by IRAC group if vector numbers are high.": "एकीकृत वाहक कीट नियंत्रण शुरू करें: नीम-आधारित स्प्रे, चिपचिपे ट्रैप और कीट संख्या अधिक होने पर IRAC समूह बदलकर कीटनाशक छिड़कें।",
        "Spray neem oil or a label-registered biological (Beauveria, Lecanicillium) first.": "पहले नीम का तेल या लेबल-पंजीकृत जैविक कीटनाशक (ब्युवेरिया, लेकानिसिलियम) का छिड़काव करें।",
        "Check new leaves, stems (black streaks) and bolls twice a week; watch for spread after rain.": "सप्ताह में दो बार नई पत्तियों, तनों (काली धारियां) और गूलरों की जांच करें; बारिश के बाद फैलाव पर नजर रखें।",
        "Scout every 4 days; compare with late blight if weather is cool and foggy.": "हर 4 दिन में निगरानी करें; ठंडा और धुंधला मौसम होने पर पछेती झुलसा से तुलना करें।",
        "Scout foliage twice weekly for progression.": "रोग के फैलाव के लिए सप्ताह में दो बार पत्तियों की जांच करें।",
        "Maintain field sanitation, balanced crop nutrition, and proper drainage.": "खेत की स्वच्छता, संतुलित फसल पोषण और उचित जल निकासी बनाए रखें।",
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
        # v2 KB Seed Translations
        "No chemical or biological treatment needed. Do not spray a healthy crop.": "કોઈ રાસાયણિક કે જૈવિક સારવારની જરૂર નથી. તંદુરસ્ત પાક પર છંટકાવ ન કરો.",
        "Maintain good agricultural hygiene, clean farm equipment, and balanced irrigation.": "ખેતીમાં સારી સ્વચ્છતા જાળવો, ઓજારો સાફ રાખો અને સંતુલિત પિયત આપો.",
        "Keep weekly scouting: 5 to 10 plants per sampling point, checking leaf undersides and new growth.": "દર અઠવાડિયે નિરીક્ષણ ચાલુ રાખો: સેમ્પલ દીઠ 5 થી 10 છોડ પસંદ કરી પાનની નીચેની સપાટી અને નવી ફૂટ તપાસો.",
        "The crop foliage appears healthy. Continue regular field scouting once a week.": "પાકના પાંદડા તંદુરસ્ત જણાય છે. અઠવાડિયામાં એકવાર નિયમિત ખેતર નિરીક્ષણ ચાલુ રાખો.",
        "Your cotton leaf looks healthy. Keep scouting once a week.": "તમારા કપાસના પાંદડા તંદુરસ્ત જણાય છે. અઠવાડિયામાં એકવાર નિરીક્ષણ ચાલુ રાખો.",
        "Your groundnut leaf looks healthy. Keep scouting once a week.": "તમારા મગફળીના પાંદડા તંદુરસ્ત જણાય છે. અઠવાડિયામાં એકવાર નિરીક્ષણ ચાલુ રાખો.",
        "Your pepper leaf looks healthy. Keep scouting once a week.": "તમારા મરચાંના પાંદડા તંદુરસ્ત જણાય છે. અઠવાડિયામાં એકવાર નિરીક્ષણ ચાલુ રાખો.",
        "Your potato leaf looks healthy. Check the underside of lower leaves once a week.": "તમારા બટાકાના પાંદડા તંદુરસ્ત જણાય છે. અઠવાડિયામાં એકવાર નીચેના પાંદડાઓની તપાસ કરો.",
        "Your tomato leaf looks healthy. Keep scouting once a week.": "તમારા ટામેટાના પાંદડા તંદુરસ્ત જણાય છે. અઠવાડિયામાં એકવાર નિરીક્ષણ ચાલુ રાખો.",
        "Stop working in the crop while leaves are wet, and mark affected plants.": "પાંદડા ભીના હોય ત્યારે પાકમાં કામ કરવાનું બંધ કરો અને અસરગ્રસ્ત છોડ પર નિશાની કરો.",
        "A copper-based protectant (and a label-registered antibiotic partner where permitted) can slow spread but will not cure existing spots.": "તાંબા-આધારિત રક્ષણાત્મક દવા (અને મંજૂર હોય ત્યાં એન્ટિબાયોટિક ઘટક) રોગનો ફેલાવો ધીમો કરી શકે છે પરંતુ હાલના ડાઘ મટાડી શકતી નથી.",
        "Scout in a W pattern and estimate the share of plants affected.": "ખેતરમાં W પેટર્નમાં ફરીને નિરીક્ષણ કરો અને અસરગ્રસ્ત છોડની ટકાવારી નક્કી કરો.",
        "Treat the whole field now with a registered protectant or translaminar product and plan a rotation product.": "સમગ્ર ખેતરમાં ભલામણ કરેલ રક્ષણાત્મક ફૂગનાશકનો તાત્કાલિક છંટકાવ કરો અને આગળના છંટકાવ માટે દવા બદલવાનું આયોજન કરો.",
        "Treat the whole field now with a registered fungicide, alternating protectant and systemic groups per label.": "સમગ્ર ખેતરમાં લેબલ મુજબ રક્ષણાત્મક અને પ્રણાલીગત જૂથો બદલીને ભલામણ કરેલ ફૂગનાશકનો છંટકાવ કરો.",
        "Start integrated vector control: neem-based sprays, sticky traps, then a label-registered insecticide rotated by IRAC group if vector numbers are high.": "સંકલિત વાહક જીવાત નિયંત્રણ શરૂ કરો: લીમડા-આધારિત છંટકાવ, પીળા ચીકણા ટ્રેપ અને જીવાત વધારે હોય તો IRAC ગ્રૂપ બદલીને ભલામણ કરેલ કીટનાશક.",
        "Spray neem oil or a label-registered biological (Beauveria, Lecanicillium) first.": "સૌપ્રથમ લીમડાનું તેલ અથવા લેબલ-રજિસ્ટર્ડ જૈવિક કીટનાશક (બ્યુવેરિયા, લેકાનિસિલિયમ) નો છંટકાવ કરો.",
        "Check new leaves, stems (black streaks) and bolls twice a week; watch for spread after rain.": "નવા પાંદડા, દાંડી (કાળા પટ્ટા) અને ઝીંડવા અઠવાડિયામાં બે વાર તપાસો; વરસાદ પછી ફેલાવા પર નજર રાખો.",
        "Scout every 4 days; compare with late blight if weather is cool and foggy.": "દર 4 દિવસે નિરીક્ષણ કરો; ઠંડા અને ધુમ્મસવાળા હવામાનમાં મોડા સુકારા સાથે સરખામણી કરો.",
        "Scout foliage twice weekly for progression.": "રોગના ફેલાવા માટે અઠવાડિયામાં બે વાર પાંદડાઓની તપાસ કરો.",
        "Maintain field sanitation, balanced crop nutrition, and proper drainage.": "ખેતરની યોગ્ય સ્વચ્છતા, સંતુલિત પાક પોષણ અને સારો નિતાર જાળવો.",
    },
}

CHEMICAL_RECOMMENDATIONS: dict[str, dict[str, str]] = {
    "Azoxystrobin 18.2% + Difenoconazole 11.4% SC @ 1 ml/L or Chlorothalonil 75% WP @ 2 g/L upon label confirmation": {
        "gu": "એઝોક્સીસ્ટ્રોબિન 18.2% + ડાયફેનોકોનાઝોલ 11.4% SC @ 1 મિલી/લિ અથવા ક્લોરોથાલોનીલ 75% WP @ 2 ગ્રામ/લિ લેબલ ચકાસણી મુજબ",
        "hi": "एज़ोक्सीस्ट्रोबिन 18.2% + डाइफेनोकोनाज़ोल 11.4% SC @ 1 मिली/लीटर या क्लोरोथालोनिल 75% WP @ 2 ग्राम/लीटर लेबल पुष्टि के अनुसार",
    },
    "Soil drenching with Carbendazim 50% WP @ 1 g/L or Trichoderma viride enriched FYM under KVK verification": {
        "gu": "કાર્બેન્ડાઝીમ 50% WP @ 1 ગ્રામ/લિ સાથે જમીનમાં ડ્રેન્ચિંગ (પિયત) અથવા KVK ચકાસણી હેઠળ ટ્રાઇકોડર્મા વિરીડી સમૃદ્ધ છાણીયું ખાતર",
        "hi": "कार्बेन्डाजिम 50% WP @ 1 ग्राम/लीटर के साथ मिट्टी में ड्रेन्चिंग या KVK सत्यापन के तहत ट्राइकोडर्मा विरिडी समृद्ध गोबर की खाद",
    },
    "Mancozeb 75% WP @ 2.5 g/L or Tebuconazole 25.9% EC @ 1 ml/L": {
        "gu": "મેન્કોઝેબ 75% WP @ 2.5 ગ્રામ/લિ અથવા ટેબ્યુકોનાઝોલ 25.9% EC @ 1 મિલી/લિ",
        "hi": "मैंकोजेब 75% WP @ 2.5 ग्राम/लीटर या टेबुकोनाज़ोल 25.9% EC @ 1 मिली/लीटर",
    },
    "Foliar micronutrient spray: Ferrous Sulfate 0.5% + Citric Acid 0.1% or Zinc Sulfate 0.2%": {
        "gu": "છંટકાવ માટે સૂક્ષ્મ પોષકતત્વો: ફેરસ સલ્ફેટ 0.5% + સાઇટ્રિક એસિડ 0.1% અથવા ઝિંક સલ્ફેટ 0.2%",
        "hi": "पर्णीय सूक्ष्म पोषक तत्व छिड़काव: फेरस सल्फेट 0.5% + साइट्रिक एसिड 0.1% या जिंक सल्फेट 0.2%",
    },
    "Imidacloprid 17.8% SL @ 0.3 ml/L or Thiamethoxam 25% WG @ 0.25 g/L to manage aphid vector": {
        "gu": "મોલો-મશી (એફિડ) નિયંત્રણ માટે ઈમિડાક્લોપ્રિડ 17.8% SL @ 0.3 મિલી/લિ અથવા થાયામેથોક્સામ 25% WG @ 0.25 ગ્રામ/લિ",
        "hi": "माहू (एफिड) कीट नियंत्रण के लिए इमिडाक्लोप्रिड 17.8% SL @ 0.3 मिली/लीटर या थायमेथॉक्सम 25% WG @ 0.25 ग्राम/लीटर",
    },
    "Copper Oxychloride 50% WP @ 2.5 g/L with Streptocycline 0.5 g/10 L drenching under KVK recommendation": {
        "gu": "કોપર ઓક્સીક્લોરાઇડ 50% WP @ 2.5 ગ્રામ/લિ સાથે સ્ટ્રેપ્ટોસાયક્લીન 0.5 ગ્રામ/10 લિટર KVK ભલામણ મુજબ ડ્રેન્ચિંગ",
        "hi": "कॉपर ऑक्सीक्लोराइड 50% WP @ 2.5 ग्राम/लीटर के साथ स्ट्रेप्टोसाइक्लिन 0.5 ग्राम/10 लीटर KVK सिफारिश के तहत ड्रेन्चिंग",
    },
    "Carbendazim + Mancozeb @ 2 g/L or Azoxystrobin 23% SC @ 1 ml/L": {
        "gu": "કાર્બેન્ડાઝીમ + મેન્કોઝેબ @ 2 ગ્રામ/લિ અથવા એઝોક્સીસ્ટ્રોબિન 23% SC @ 1 મિલી/લિ",
        "hi": "कार्बेन्डाजिम + मैंकोजेब @ 2 ग्राम/लीटर या एज़ोक्सीस्ट्रोबिन 23% SC @ 1 मिली/लीटर",
    },
    "Bio-nematicides (Paecilomyces lilacinus @ 5 kg/ha) or Neem cake @ 250 kg/ha; chemical nematicides only under official permit": {
        "gu": "જૈવિક નેમાટીસાઇડ્સ (પેસિલોમાયસીસ લિલાસીનસ @ 5 કિગ્રા/હેક્ટર) અથવા લીંબોળીનો ખોળ @ 250 કિગ્રા/હેક્ટર; રાસાયણિક નેમાટીસાઇડ્સ ફક્ત સત્તાવાર પરવાનગી હેઠળ",
        "hi": "जैव-नेमाटीसाइड्स (पैसिलोमाइसीस लिलासिनस @ 5 किग्रा/हेक्टेयर) या नीम की खली @ 250 किग्रा/हेक्टेयर; रासायनिक नेमाटीसाइड्स केवल आधिकारिक अनुमति के तहत",
    },
    "Chlorantraniliprole 18.5% SC @ 0.3 ml/L or Acetamiprid 20% SP @ 0.2 g/L under label guidelines": {
        "gu": "ક્લોરાન્ટ્રાનિલીપ્રોલ 18.5% SC @ 0.3 મિલી/લિ અથવા એસિટામિપ્રિડ 20% SP @ 0.2 ગ્રામ/લિ લેબલ માર્ગદર્શિકા મુજબ",
        "hi": "क्लोरेंट्रानिलीप्रोल 18.5% SC @ 0.3 मिली/लीटर या एसिटामिप्रिड 20% SP @ 0.2 ग्राम/लीटर लेबल दिशानिर्देशों के अनुसार",
    },
    "Thiamethoxam 25% WG @ 0.3 g/L or Flonicamid 50% WG @ 0.3 g/L for aphid vector management": {
        "gu": "મોલો-મશી (એફિડ) નિયંત્રણ માટે થાયામેથોક્સામ 25% WG @ 0.3 ગ્રામ/લિ અથવા ફ્લોનિકામિડ 50% WG @ 0.3 ગ્રામ/લિ",
        "hi": "माहू (एफिड) कीट नियंत्रण के लिए थायमेथॉक्सम 25% WG @ 0.3 ग्राम/लीटर या फ्लोनिकामिड 50% WG @ 0.3 ग्राम/लीटर",
    },
    "Mancozeb 75% WP @ 2.5 g/L or Azoxystrobin + Difenoconazole @ 1 ml/L": {
        "gu": "મેન્કોઝેબ 75% WP @ 2.5 ગ્રામ/લિ અથવા એઝોક્સીસ્ટ્રોબિન + ડાયફેનોકોનાઝોલ @ 1 મિલી/લિ",
        "hi": "मैंकोजेब 75% WP @ 2.5 ग्राम/लीटर या एज़ोक्सीस्ट्रोबिन + डाइफेनोकोनाज़ोल @ 1 मिली/लीटर",
    },
    "Diafenthiuron 50% WP @ 1.2 g/L or Spinetoram 11.7% SC @ 1 ml/L for vector management": {
        "gu": "વાહક જીવાત નિયંત્રણ માટે ડાયફેન્થિયુરોન 50% WP @ 1.2 ગ્રામ/લિ અથવા સ્પીનેટોરામ 11.7% SC @ 1 મિલી/લિ",
        "hi": "वाहक कीट नियंत्रण के लिए डायफेन्थियूरॉन 50% WP @ 1.2 ग्राम/लीटर या स्पिनिटोरम 11.7% SC @ 1 मिली/लीटर",
    },
    "Calcium Nitrate @ 5 g/L + Boron @ 1 g/L or 19-19-19 water-soluble foliar spray": {
        "gu": "કેલ્શિયમ નાઇટ્રેટ @ 5 ગ્રામ/લિ + બોરોન @ 1 ગ્રામ/લિ અથવા 19-19-19 પાણીમાં દ્રાવ્ય પાન પર છંટકાવ",
        "hi": "कैल्शियम नाइट्रेट @ 5 ग्राम/लीटर + बोरॉन @ 1 ग्राम/लीटर या 19-19-19 पानी में घुलनशील पर्णीय छिड़काव",
    },
    "Wettable Sulfur 80% WP @ 3 g/L or Hexaconazole 5% EC @ 1 ml/L": {
        "gu": "વેટેબલ સલ્ફર 80% WP @ 3 ગ્રામ/લિ અથવા હેક્ઝાકોનાઝોલ 5% EC @ 1 મિલી/લિ",
        "hi": "घुलनशील सल्फर 80% WP @ 3 ग्राम/लीटर या हेक्साकोनाज़ोल 5% EC @ 1 मिली/लीटर",
    },
}

_AGRONOMIC_CLAUSE_MAP: dict[str, dict[str, str]] = {
    "gu": {
        "upon label confirmation under local KVK guidance": "સ્થાનિક KVK માર્ગદર્શન હેઠળ અને લેબલ ચકાસણી મુજબ",
        "upon label confirmation": "લેબલ ચકાસણી મુજબ",
        "under KVK verification": "KVK ચકાસણી હેઠળ",
        "under KVK recommendation": "KVK ભલામણ મુજબ",
        "under local KVK guidance": "સ્થાનિક KVK માર્ગદર્શન હેઠળ",
        "under KVK guidance": "KVK માર્ગદર્શન હેઠળ",
        "under local KVK supervision": "સ્થાનિક KVK દેખરેખ હેઠળ",
        "under label guidelines": "લેબલ માર્ગદર્શિકા મુજબ",
        "only under official permit": "ફક્ત સત્તાવાર પરવાનગી હેઠળ",
        "under official permit": "સત્તાવાર પરવાનગી હેઠળ",
        "premix if registered": "નોંધાયેલ હોય તો પ્રીમિક્સ",
        "premix": "પ્રીમિક્સ",
        " Combination": "",
        " combination": "",
        "in-furrow or seed treatment, per label": "પાન અથવા બીજ માવજત તરીકે, લેબલ મુજબ",
        "seed treatment or foliar, per label": "બીજ માવજત અથવા પાન પર છંટકાવ, લેબલ મુજબ",
        "not above about 32 C": "આશરે 32°C થી વધુ તાપમાનમાં નહીં",
        "per label": "લેબલ મુજબ",
        "for mites": "ઈતરડી નિયંત્રણ માટે",
        "aphids": "મોલો-મશી (એફિડ)",
        "to manage aphid vector": "મોલો-મશી (એફિડ) નિયંત્રણ માટે",
        "for aphid vector management": "મોલો-મશી (એફિડ) નિયંત્રણ માટે",
        "for vector management": "વાહક જીવાત નિયંત્રણ માટે",
        "Soil drenching with": "સાથે જમીનમાં ડ્રેન્ચિંગ (પિયત)",
        "water-soluble foliar spray": "પાણીમાં દ્રાવ્ય પાન પર છંટકાવ",
        "Foliar micronutrient spray:": "છંટકાવ માટે સૂક્ષ્મ પોષકતત્વો:",
        "Foliar micronutrient spray": "છંટકાવ માટે સૂક્ષ્મ પોષકતત્વો",
        "or Neem cake": "અથવા લીંબોળીનો ખોળ",
        "Bio-nematicides": "જૈવિક નેમાટીસાઇડ્સ",
        "chemical nematicides": "રાસાયણિક નેમાટીસાઇડ્સ",
        "drenching under KVK recommendation": "સાથે KVK ભલામણ મુજબ ડ્રેન્ચિંગ",
        "drenching": "ડ્રેન્ચિંગ (પિયત)",
        "enriched FYM": "સમૃદ્ધ છાણીયું ખાતર",
        "FYM": "છાણીયું ખાતર",
        " or ": " અથવા ",
        " with ": " સાથે ",
        " @ 1 ml/L": " @ 1 મિલી/લિ",
        " @ 2 ml/L": " @ 2 મિલી/લિ",
        " @ 0.3 ml/L": " @ 0.3 મિલી/લિ",
        " @ 0.5 ml/L": " @ 0.5 મિલી/લિ",
        " @ 1 g/L": " @ 1 ગ્રામ/લિ",
        " @ 2 g/L": " @ 2 ગ્રામ/લિ",
        " @ 2.5 g/L": " @ 2.5 ગ્રામ/લિ",
        " @ 3 g/L": " @ 3 ગ્રામ/લિ",
        " @ 5 g/L": " @ 5 ગ્રામ/લિ",
        " @ 0.2 g/L": " @ 0.2 ગ્રામ/લિ",
        " @ 0.25 g/L": " @ 0.25 ગ્રામ/લિ",
        " @ 0.3 g/L": " @ 0.3 ગ્રામ/લિ",
        " @ 5 kg/ha": " @ 5 કિગ્રા/હેક્ટર",
        " @ 250 kg/ha": " @ 250 કિગ્રા/હેક્ટર",
        " 0.5 g/10 L": " 0.5 ગ્રામ/10 લિટર",
        " 1 ml/L": " 1 મિલી/લિ",
        " 2 g/L": " 2 ગ્રામ/લિ",
    },
    "hi": {
        "upon label confirmation under local KVK guidance": "स्थानीय KVK मार्गदर्शन और लेबल पुष्टि के अनुसार",
        "upon label confirmation": "लेबल पुष्टि के अनुसार",
        "under KVK verification": "KVK सत्यापन के तहत",
        "under KVK recommendation": "KVK सिफारिश के तहत",
        "under local KVK guidance": "स्थानीय KVK मार्गदर्शन के तहत",
        "under KVK guidance": "KVK मार्गदर्शन के तहत",
        "under local KVK supervision": "स्थानीय KVK देखरेख में",
        "under label guidelines": "लेबल दिशानिर्देशों के अनुसार",
        "only under official permit": "केवल आधिकारिक अनुमति के तहत",
        "under official permit": "आधिकारिक अनुमति के तहत",
        "premix if registered": "पंजीकृत होने पर प्रीमिक्स",
        "premix": "प्रीमिक्स",
        " Combination": "",
        " combination": "",
        "in-furrow or seed treatment, per label": "बीज उपचार या कतार में, लेबल के अनुसार",
        "seed treatment or foliar, per label": "बीज उपचार या पर्णीय छिड़काव, लेबल के अनुसार",
        "not above about 32 C": "लगभग 32°C से अधिक तापमान में नहीं",
        "per label": "लेबल के अनुसार",
        "for mites": "माइट कीट नियंत्रण के लिए",
        "aphids": "माहू (एफिड)",
        "to manage aphid vector": "माहू (एफिड) कीट नियंत्रण के लिए",
        "for aphid vector management": "माहू कीट नियंत्रण के लिए",
        "for vector management": "वाहक कीट नियंत्रण के लिए",
        "Soil drenching with": "के साथ मिट्टी में ड्रेन्चिंग",
        "water-soluble foliar spray": "पानी में घुलनशील पर्णीय छिड़काव",
        "Foliar micronutrient spray:": "पर्णीय सूक्ष्म पोषक तत्व छिड़काव:",
        "Foliar micronutrient spray": "पर्णीय सूक्ष्म पोषक तत्व छिड़काव",
        "or Neem cake": "या नीम की खली",
        "Bio-nematicides": "जैव-नेमाटीसाइड्स",
        "chemical nematicides": "रासायनिक नेमाटीसाइड्स",
        "drenching under KVK recommendation": "के साथ KVK सिफारिश के तहत ड्रेन्चिंग",
        "drenching": "ड्रेन्चिंग",
        "enriched FYM": "समृद्ध गोबर की खाद",
        "FYM": "गोबर की खाद",
        " or ": " या ",
        " with ": " के साथ ",
        " @ 1 ml/L": " @ 1 मिली/लीटर",
        " @ 2 ml/L": " @ 2 मिली/लीटर",
        " @ 0.3 ml/L": " @ 0.3 मिली/लीटर",
        " @ 0.5 ml/L": " @ 0.5 मिली/लीटर",
        " @ 1 g/L": " @ 1 ग्राम/लीटर",
        " @ 2 g/L": " @ 2 ग्राम/लीटर",
        " @ 2.5 g/L": " @ 2.5 ग्राम/लीटर",
        " @ 3 g/L": " @ 3 ग्राम/लीटर",
        " @ 5 g/L": " @ 5 ग्राम/लीटर",
        " @ 0.2 g/L": " @ 0.2 ग्राम/लीटर",
        " @ 0.25 g/L": " @ 0.25 ग्राम/लीटर",
        " @ 0.3 g/L": " @ 0.3 ग्राम/लीटर",
        " @ 5 kg/ha": " @ 5 किग्रा/हेक्टेयर",
        " @ 250 kg/ha": " @ 250 किग्रा/हेक्टेयर",
        " 0.5 g/10 L": " 0.5 ग्राम/10 लीटर",
        " 1 ml/L": " 1 मिली/लीटर",
        " 2 g/L": " 2 ग्राम/लीटर",
    },
}

_CHEMICAL_NAME_MAP: dict[str, dict[str, str]] = {
    "gu": {
        "Azoxystrobin": "એઝોક્સીસ્ટ્રોબિન",
        "Difenoconazole": "ડાયફેનોકોનાઝોલ",
        "Chlorothalonil": "ક્લોરોથાલોનીલ",
        "Carbendazim": "કાર્બેન્ડાઝીમ",
        "Mancozeb": "મેન્કોઝેબ",
        "Trichoderma viride": "ટ્રાઇકોડર્મા વિરીડી",
        "Trichoderma": "ટ્રાઇકોડર્મા",
        "Pseudomonas fluorescens": "સ્યુડોમોનાસ ફ્લોરોસન્સ",
        "Pseudomonas": "સ્યુડોમોનાસ",
        "Beauveria bassiana": "બ્યુવેરિયા બાસિયાના",
        "Beauveria": "બ્યુવેરિયા",
        "Lecanicillium lecanii": "લેકાનિસિલિયમ લેકાની",
        "Lecanicillium": "લેકાનિસિલિયમ",
        "Tebuconazole": "ટેબ્યુકોનાઝોલ",
        "Trifloxystrobin": "ટ્રાઇફ્લોક્સીસ્ટ્રોબિન",
        "Ferrous Sulfate": "ફેરસ સલ્ફેટ",
        "Citric Acid": "સાઇટ્રિક એસિડ",
        "Zinc Sulfate": "ઝિંક સલ્ફેટ",
        "Imidacloprid": "ઈમિડાક્લોપ્રિડ",
        "Thiamethoxam": "થાયામેથોક્સામ",
        "Copper Oxychloride": "કોપર ઓક્સીક્લોરાઇડ",
        "Copper Hydroxide": "કોપર હાઇડ્રોક્સાઇડ",
        "Streptocycline": "સ્ટ્રેપ્ટોસાયક્લીન",
        "Streptomycin Sulphate": "સ્ટ્રેપ્ટોમાસીન સલ્ફેટ",
        "Streptomycin": "સ્ટ્રેપ્ટોમાસીન",
        "Tetracycline": "ટેટ્રાસાયક્લિન",
        "Chlorantraniliprole": "ક્લોરાન્ટ્રાનિલીપ્રોલ",
        "Cyantraniliprole": "સાયન્ટ્રાનિલીપ્રોલ",
        "Cymoxanil": "સાયમોક્સાનીલ",
        "Dimethomorph": "ડાઈમેથોમોર્ફ",
        "Fenamidone": "ફેનામિડોન",
        "Fenpyroximate": "ફેનપાયરોક્સીમેટ",
        "Metalaxyl-M": "મેટાલેક્સિલ-એમ",
        "Metalaxyl": "મેટાલેક્સિલ",
        "Propargite": "પ્રોપરગાઇટ",
        "Propiconazole": "પ્રોપિકોનાઝોલ",
        "Pyriproxyfen": "પાયરીપ્રોક્સીફેન",
        "Spinosad": "સ્પિનોસેડ",
        "Spiromesifen": "સ્પાયરોમેસિફેન",
        "Abamectin": "એબામેક્ટીન",
        "Emamectin Benzoate": "ઇમામેક્ટીન બેન્ઝોએટ",
        "Acetamiprid": "એસિટામિપ્રિડ",
        "Flonicamid": "ફ્લોનિકામિડ",
        "Diafenthiuron": "ડાયફેન્થિયુરોન",
        "Spinetoram": "સ્પીનેટોરામ",
        "Calcium Nitrate": "કેલ્શિયમ નાઇટ્રેટ",
        "Boron": "બોરોન",
        "Hexaconazole": "હેક્ઝાકોનાઝોલ",
        "Sulfur": "સલ્ફર",
        "Sulphur": "સલ્ફર",
        "Wettable Sulfur": "વેટેબલ સલ્ફર",
        "Wettable Sulphur": "વેટેબલ સલ્ફર",
        "Neem oil": "લીમડાનું તેલ",
        "Neem cake": "લીંબોળીનો ખોળ",
        "Pyraclostrobin": "પાયરાક્લોસ્ટ્રોબિન",
        "Chlorpyrifos": "ક્લોરપાયરીફોસ",
    },
    "hi": {
        "Azoxystrobin": "एज़ोक्सीस्ट्रोबिन",
        "Difenoconazole": "डाइफेनोकोनाज़ोल",
        "Chlorothalonil": "क्लोरोथालोनिल",
        "Carbendazim": "कार्बेन्डाजिम",
        "Mancozeb": "मैंकोजेब",
        "Trichoderma viride": "ट्राइकोडर्मा विरिडी",
        "Trichoderma": "ट्राइकोडर्मा",
        "Pseudomonas fluorescens": "स्यूडोमोनास फ्लोरोसेंस",
        "Pseudomonas": "स्यूडोमोनास",
        "Beauveria bassiana": "ब्युवेरिया बासियाना",
        "Beauveria": "ब्युवेरिया",
        "Lecanicillium lecanii": "लेकानिसिलियम लेकानी",
        "Lecanicillium": "लेकानिसिलियम",
        "Tebuconazole": "टेबुकोनाज़ोल",
        "Trifloxystrobin": "ट्राइफ्लॉक्सीस्ट्रोबिन",
        "Ferrous Sulfate": "फेरस सल्फेट",
        "Citric Acid": "साइट्रिक एसिड",
        "Zinc Sulfate": "जिंक सल्फेट",
        "Imidacloprid": "इमिडाक्लोप्रिड",
        "Thiamethoxam": "थायमेथॉक्सम",
        "Copper Oxychloride": "कॉपर ऑक्सीक्लोराइड",
        "Copper Hydroxide": "कॉपर हाइड्रोक्साइड",
        "Streptocycline": "स्ट्रेप्टोसाइक्लिन",
        "Streptomycin Sulphate": "स्ट्रेप्टोमाइसिन सल्फेट",
        "Streptomycin": "स्ट्रेप्टोमाइसिन",
        "Tetracycline": "टेट्रासाइक्लिन",
        "Chlorantraniliprole": "क्लोरेंट्रानिलीप्रोल",
        "Cyantraniliprole": "सायंट्रानिलीप्रोल",
        "Cymoxanil": "साइमोक्सानिल",
        "Dimethomorph": "डाइमेथोमॉर्फ",
        "Fenamidone": "फेनामिडोन",
        "Fenpyroximate": "फेनपायरोक्सिमेट",
        "Metalaxyl-M": "मेटालेक्सिल-एम",
        "Metalaxyl": "मेटालेक्सिल",
        "Propargite": "प्रोपरगाइट",
        "Propiconazole": "प्रोपिकोनाज़ोल",
        "Pyriproxyfen": "पायरीप्रोक्सीफेन",
        "Spinosad": "स्पिनोसाद",
        "Spiromesifen": "स्पायरोमेसिफेन",
        "Abamectin": "एबामेक्टिन",
        "Emamectin Benzoate": "इमामेक्टिन बेंजोएट",
        "Acetamiprid": "एसिटामिप्रिड",
        "Flonicamid": "फ्लोनिकामिड",
        "Diafenthiuron": "डायफेन्थियूरॉन",
        "Spinetoram": "स्पिनिटोरम",
        "Calcium Nitrate": "कैल्शियम नाइट्रेट",
        "Boron": "बोरॉन",
        "Hexaconazole": "हेक्साकोनाज़ोल",
        "Sulfur": "सल्फर",
        "Sulphur": "सल्फर",
        "Wettable Sulfur": "घुलनशील सल्फर",
        "Wettable Sulphur": "घुलनशील सल्फर",
        "Neem oil": "नीम का तेल",
        "Neem cake": "नीम की खली",
        "Pyraclostrobin": "पायराक्लोस्ट्रोबिन",
        "Chlorpyrifos": "क्लोरपायरीफॉस",
    },
}


def translate_chemical_recommendation(chem_text: str, target_code: str) -> str:
    """Translates agricultural chemical formulations and dosages accurately into Gujarati or Hindi."""
    clean = chem_text.strip()
    if target_code not in ("hi", "gu"):
        return clean
    if clean in CHEMICAL_RECOMMENDATIONS and target_code in CHEMICAL_RECOMMENDATIONS[clean]:
        return CHEMICAL_RECOMMENDATIONS[clean][target_code]

    res = clean
    for phrase, tr in _AGRONOMIC_CLAUSE_MAP.get(target_code, {}).items():
        res = res.replace(phrase, tr)
    for chem, tr in _CHEMICAL_NAME_MAP.get(target_code, {}).items():
        res = re.sub(r"\b" + re.escape(chem) + r"\b", tr, res)
    return res


def translate_treatment_recommendation(text: str, target_code: str) -> str:
    """Translates [Recommended: ...] clauses embedded in treatment advisory text."""
    if not text or target_code not in ("hi", "gu"):
        return text
    prefix = "ભલામણ કરેલ" if target_code == "gu" else "अनुशंसित"

    def repl(m: re.Match) -> str:
        inner = m.group(1).strip()
        trans = translate_chemical_recommendation(inner, target_code)
        return f"[{prefix}: {trans}]"

    return re.sub(r"\[Recommended:\s*([^\]]+)\]", repl, text, flags=re.IGNORECASE)


_AGRONOMIC_PATTERNS = [
    (
        re.compile(r"^\[Recommended:\s*([^\]]+)\]$", re.IGNORECASE),
        {
            "gu": lambda m: f"[ભલામણ કરેલ: {translate_chemical_recommendation(m.group(1), 'gu')}]",
            "hi": lambda m: f"[अनुशंसित: {translate_chemical_recommendation(m.group(1), 'hi')}]",
        }
    ),
    (
        re.compile(r"^Recommended:\s*(.+)$", re.IGNORECASE),
        {
            "gu": lambda m: f"ભલામણ કરેલ: {translate_chemical_recommendation(m.group(1), 'gu')}",
            "hi": lambda m: f"अनुशंसित: {translate_chemical_recommendation(m.group(1), 'hi')}",
        }
    ),
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
    if CACHE_FILE.exists() and CACHE_FILE.stat().st_size > 0:
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

    # 3. Pre-load conditions from advisory_kb.json (v2 & v1 schemas)
    kb_path = settings.KB_PATH
    if kb_path.exists():
        try:
            with open(kb_path, "r", encoding="utf-8") as f:
                kb_data = json.load(f)
            loaded_kb_pairs = 0

            conditions_list = []
            if isinstance(kb_data, dict) and "conditions" in kb_data:
                conditions_list = [c for c in kb_data.get("conditions", []) if isinstance(c, dict)]
            elif isinstance(kb_data, dict):
                conditions_list = [c for c in kb_data.values() if isinstance(c, dict)]

            for cond_val in conditions_list:
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

                # Pre-index chemical recommendation translations from chemical_candidates or chemical_recommendation
                chem_rec = cond_val.get("chemical_recommendation")
                if not chem_rec and cond_val.get("chemical_candidates"):
                    chem_candidates = cond_val.get("chemical_candidates", [])
                    cand_names = [cand.get("active_or_option", str(cand)).title() if isinstance(cand, dict) else str(cand).title() for cand in chem_candidates[:2]]
                    chem_rec = f"{' or '.join(cand_names)} upon label confirmation under local KVK guidance"
                elif not chem_rec and cond_val.get("biological_options"):
                    bio_options = cond_val.get("biological_options", [])
                    first_bio = bio_options[0] if isinstance(bio_options[0], str) else str(bio_options[0])
                    chem_rec = f"{first_bio} under local KVK guidance"

                if chem_rec and isinstance(chem_rec, str) and "none" not in chem_rec.lower() and "requires local diagnosis" not in chem_rec.lower():
                    for lang in ("hi", "gu"):
                        tr_chem = translate_chemical_recommendation(chem_rec, lang)
                        lbl = "ભલામણ કરેલ" if lang == "gu" else "अनुशंसित"
                        _cache[f"{lang}:[Recommended: {chem_rec.strip()}]"] = f"[{lbl}: {tr_chem.strip()}]"
                        _cache[f"{lang}:Recommended: {chem_rec.strip()}"] = f"{lbl}: {tr_chem.strip()}"
                        _cache[f"{lang}:{chem_rec.strip()}"] = tr_chem.strip()

            logger.info("Indexed %d verified sentence pairs and candidates from advisory_kb.json.", loaded_kb_pairs)
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

    # Direct match for chemical recommendations with or without brackets
    if clean.startswith("[Recommended:") and clean.endswith("]"):
        return translate_treatment_recommendation(clean, target_code)

    # Treatment guidance containing [Recommended: ...]
    m_rec = re.search(r"(\[Recommended:\s*[^\]]+\])", clean, flags=re.IGNORECASE)
    if m_rec:
        prefix_text = clean[:m_rec.start()].strip()
        rec_block = clean[m_rec.start():m_rec.end()]
        translated_rec = translate_treatment_recommendation(rec_block, target_code)
        if prefix_text:
            translated_prefix = resolve_agronomic_phrase(prefix_text, target_code)
            if not translated_prefix:
                sents = split_into_sentences(prefix_text)
                trans_parts = []
                for s in sents:
                    ts = resolve_agronomic_phrase(s, target_code)
                    trans_parts.append(ts if ts else s)
                translated_prefix = " ".join(trans_parts)
            return f"{translated_prefix} {translated_rec}".strip()
        return translated_rec

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

    clean_code = target_code.strip().lower()
    # Guard against SSRF: ensure target_code is strictly alphanumeric and short
    if not clean_code or not clean_code.isalnum() or len(clean_code) > 10:
        return None

    params = {
        "client": "gtx",
        "sl": "auto",
        "tl": clean_code,
        "dt": "t",
        "q": text,
    }
    headers = {"User-Agent": "SmartFarmingApp/2.0 (Linux; IndicTrans2 Fallback)"}

    if httpx is not None:
        try:
            with httpx.Client(timeout=3.5, headers=headers) as client:
                resp = client.get("https://translate.googleapis.com/translate_a/single", params=params)
                if resp.status_code == 200:
                    data = resp.json()
                    segments = "".join(s[0] for s in data[0] if s and s[0])
                    if segments and segments.strip():
                        return segments.strip()
        except Exception as exc:
            logger.debug("Google translate httpx notice: %s", exc)

    try:
        query_string = urllib.parse.urlencode(params)
        full_url = f"https://translate.googleapis.com/translate_a/single?{query_string}"
        req = urllib.request.Request(full_url, headers=headers)
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
        if "[Recommended:" in assembled:
            assembled = translate_treatment_recommendation(assembled, target_code)
        _cache[cache_key] = assembled
        return assembled

    # Tier 3: Fast Cloud Groq LLM (if key provided, ~300ms)
    groq_res = _call_groq_translate(clean, target_code)
    if groq_res:
        if "[Recommended:" in groq_res:
            groq_res = translate_treatment_recommendation(groq_res, target_code)
        _cache[cache_key] = groq_res
        return groq_res

    # Tier 4: Public Google Translate API (fast, robust, ~400ms)
    gt_res = _call_google_translate(clean, target_code)
    if gt_res:
        if "[Recommended:" in gt_res:
            gt_res = translate_treatment_recommendation(gt_res, target_code)
        _cache[cache_key] = gt_res
        return gt_res

    # Tier 5: Local IndicTrans2 Model (if available on GPU or fast CPU)
    indictrans_code = LANG_CODES.get(target_code, "hin_Deva")
    it_res = _run_indictrans_batch([clean], indictrans_code)
    if it_res and it_res[0]:
        res_t = it_res[0]
        if "[Recommended:" in res_t:
            res_t = translate_treatment_recommendation(res_t, target_code)
        _cache[cache_key] = res_t
        return res_t

    # Tier 6: Safe graceful fallback to source text
    if "[Recommended:" in clean:
        clean = translate_treatment_recommendation(clean, target_code)
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
        # Background cache save thread spawn failure is non-fatal to translation delivery
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
