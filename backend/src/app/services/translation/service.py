from __future__ import annotations

import logging
import os
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

_AGRONOMIC_TRANSLATIONS: dict[str, dict[str, str]] = {
    "gu": {
        "DISCLAIMER: Confirm the diagnosis and any chemical use with your local KVK or agriculture officer, and follow the product label.": "અસ્વીકરણ: કોઈ પણ રસાયણ કે દવાનો ઉપયોગ કરતા પહેલાં તમારા સ્થાનિક કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) અથવા ખેતીવાડી અધિકારી પાસેથી નિદાનની પુષ્ટિ કરો અને ઉત્પાદનના લેબલનું પાલન કરો.",
        "Confirm the diagnosis and any chemical use with your local KVK or agriculture officer, and follow the product label.": "કોઈ પણ રસાયણ કે દવાનો ઉપયોગ કરતા પહેલાં તમારા સ્થાનિક કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) અથવા ખેતીવાડી અધિકારી પાસેથી નિદાનની પુષ્ટિ કરો અને ઉત્પાદનના લેબલનું પાલન કરો.",
        "DISCLAIMER: Always follow local agricultural guidelines, product labels, and consult your local KVK.": "અસ્વીકરણ: હંમેશા સ્થાનિક કૃષિ માર્ગદર્શિકા, ઉત્પાદન લેબલનું પાલન કરો અને તમારા સ્થાનિક KVK ની સલાહ લો.",
        "Always follow local agricultural guidelines, product labels, and consult your local KVK.": "હંમેશા સ્થાનિક કૃષિ માર્ગદર્શિકા, ઉત્પાદન લેબલનું પાલન કરો અને તમારા સ્થાનિક KVK ની સલાહ લો.",
        "Always follow local agricultural guidelines and chemical label instructions.": "હંમેશા સ્થાનિક કૃષિ માર્ગદર્શિકા અને રાસાયણિક લેબલ સૂચનાઓનું પાલન કરો.",
        "DISCLAIMER: Always follow local agricultural guidelines and chemical label instructions.": "અસ્વીકરણ: હંમેશા સ્થાનિક કૃષિ માર્ગદર્શિકા અને રાસાયણિક લેબલ સૂચનાઓનું પાલન કરો.",
        "DISCLAIMER: Always confirm diagnosis with your local agricultural extension officer.": "અસ્વીકરણ: હંમેશા તમારા સ્થાનિક કૃષિ વિસ્તરણ અધિકારી સાથે નિદાનની પુષ્ટિ કરો.",
        "Always confirm diagnosis with your local agricultural extension officer.": "હંમેશા તમારા સ્થાનિક કૃષિ વિસ્તરણ અધિકારી સાથે નિદાનની પુષ્ટિ કરો.",
        "DISCLAIMER: Always confirm diagnosis with your local agricultural officer.": "અસ્વીકરણ: હંમેશા તમારા સ્થાનિક કૃષિ અધિકારી સાથે રોગના નિદાનની પુષ્ટિ કરો.",
        "Always confirm diagnosis with your local agricultural officer.": "હંમેશા તમારા સ્થાનિક કૃષિ અધિકારી સાથે રોગના નિદાનની પુષ્ટિ કરો.",
        "DISCLAIMER: Automated diagnosis currently supports Cotton, Groundnut, Pepper Bell, Potato, and Tomato. Do not apply synthetic pesticides without professional verification.": "અસ્વીકરણ: સ્વચાલિત નિદાન હાલમાં કપાસ, મગફળી, શિમલા મરચાં, બટાકા અને ટામેટાંને સપોર્ટ કરે છે. વ્યાવસાયિક ચકાસણી વિના કૃત્રિમ જંતુનાશકોનો ઉપયોગ કરશો નહીં.",
        "Automated diagnosis currently supports Cotton, Groundnut, Pepper Bell, Potato, and Tomato. Do not apply synthetic pesticides without professional verification.": "સ્વચાલિત નિદાન હાલમાં કપાસ, મગફળી, શિમલા મરચાં, બટાકા અને ટામેટાંને સપોર્ટ કરે છે. વ્યાવસાયિક ચકાસણી વિના કૃત્રિમ જંતુનાશકોનો ઉપયોગ કરશો નહીં.",
        "No chemical treatment is recommended without expert confirmation.": "નિષ્ણાતની પુષ્ટિ વિના કોઈ રાસાયણિક સારવારની ભલામણ કરવામાં આવતી નથી.",
        "No automated chemical treatment is recommended for unverified crops to avoid pesticide misuse.": "જંતુનાશકોના દુરુપયોગને રોકવા માટે અણચકાસાયેલ પાકો માટે કોઈ સ્વચાલિત રાસાયણિક સારવારની ભલામણ કરવામાં આવતી નથી.",
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
    },
    "hi": {
        "DISCLAIMER: Confirm the diagnosis and any chemical use with your local KVK or agriculture officer, and follow the product label.": "अस्वीकरण: कोई भी रसायन या दवा इस्तेमाल करने से पहले अपने स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि अधिकारी से निदान की पुष्टि करें और उत्पाद के लेबल का पालन करें।",
        "Confirm the diagnosis and any chemical use with your local KVK or agriculture officer, and follow the product label.": "कोई भी रसायन या दवा इस्तेमाल करने से पहले अपने स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि अधिकारी से निदान की पुष्टि करें और उत्पाद के लेबल का पालन करें।",
        "DISCLAIMER: Always follow local agricultural guidelines, product labels, and consult your local KVK.": "अस्वीकरण: हमेशा स्थानीय कृषि दिशानिर्देशों, उत्पाद लेबल का पालन करें और अपने स्थानीय KVK से परामर्श करें।",
        "Always follow local agricultural guidelines, product labels, and consult your local KVK.": "हमेशा स्थानीय कृषि दिशानिर्देशों, उत्पाद लेबल का पालन करें और अपने स्थानीय KVK से परामर्श करें।",
        "Always follow local agricultural guidelines and chemical label instructions.": "हमेशा स्थानीय कृषि दिशानिर्देशों और रासायनिक लेबल निर्देशों का पालन करें।",
        "DISCLAIMER: Always follow local agricultural guidelines and chemical label instructions.": "अस्वीकरण: हमेशा स्थानीय कृषि दिशानिर्देशों और रासायनिक लेबल निर्देशों का पालन करें।",
        "DISCLAIMER: Always confirm diagnosis with your local agricultural extension officer.": "अस्वीकरण: हमेशा अपने स्थानीय कृषि विस्तार अधिकारी से निदान की पुष्टि करें।",
        "Always confirm diagnosis with your local agricultural extension officer.": "हमेशा अपने स्थानीय कृषि विस्तार अधिकारी से निदान की पुष्टि करें।",
        "DISCLAIMER: Always confirm diagnosis with your local agricultural officer.": "अस्वीकरण: हमेशा अपने स्थानीय कृषि अधिकारी से निदान की पुष्टि करें।",
        "Always confirm diagnosis with your local agricultural officer.": "हमेशा अपने स्थानीय कृषि अधिकारी से निदान की पुष्टि करें।",
        "DISCLAIMER: Automated diagnosis currently supports Cotton, Groundnut, Pepper Bell, Potato, and Tomato. Do not apply synthetic pesticides without professional verification.": "अस्वीकरण: स्वचालित निदान वर्तमान में कपास, मूंगफली, शिमला मिर्च, आलू और टमाटर का समर्थन करता है। पेशेवर सत्यापन के बिना सिंथेटिक कीटनाशकों का उपयोग न करें।",
        "Automated diagnosis currently supports Cotton, Groundnut, Pepper Bell, Potato, and Tomato. Do not apply synthetic pesticides without professional verification.": "स्वचालित निदान वर्तमान में कपास, मूंगफली, शिमला मिर्च, आलू और टमाटर का समर्थन करता है। पेशेवर सत्यापन के बिना सिंथेटिक कीटनाशकों का उपयोग न करें।",
        "No chemical treatment is recommended without expert confirmation.": "विशेषज्ञ की पुष्टि के बिना किसी रासायनिक उपचार की सिफारिश नहीं की जाती है।",
        "No automated chemical treatment is recommended for unverified crops to avoid pesticide misuse.": "कीटनाशकों के दुरुपयोग से बचने के लिए असत्यापित फसलों के लिए किसी स्वचालित रासायनिक उपचार की सिफारिश नहीं की जाती है।",
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
        "Maintain proper crop spacing and weed-free field borders.": "उचित फसल दूरी बनाए रखें और खेत की मेड़ों को खरपतवार मुक्त रखें.",
        "Take high-resolution, centered photos in balanced daylight.": "संतुलित दिन के उजाले में उच्च-रिज़ॉल्यूशन, केंद्रित तस्वीरें लें।",
        "None (Consult specialist)": "कोई नहीं (विशेषज्ञ से परामर्श लें)",
        "Maintain balanced plant nutrition and moisture.": "पौधों का संतुलित पोषण और नमी बनाए रखें।",
        "Isolate affected plants and ensure canopy ventilation.": "प्रभावित पौधों को अलग करें और हवा का उचित संचार सुनिश्चित करें।",
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
        "upon label confirmation": "લેબલ ચકાસણી મુજબ",
        "under KVK verification": "KVK ચકાસણી હેઠળ",
        "under KVK recommendation": "KVK ભલામણ મુજબ",
        "under KVK guidance": "KVK માર્ગદર્શન હેઠળ",
        "under local KVK supervision": "સ્થાનિક KVK દેખરેખ હેઠળ",
        "under label guidelines": "લેબલ માર્ગદર્શિકા મુજબ",
        "only under official permit": "ફક્ત સત્તાવાર પરવાનગી હેઠળ",
        "under official permit": "સત્તાવાર પરવાનગી હેઠળ",
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
        "upon label confirmation": "लेबल पुष्टि के अनुसार",
        "under KVK verification": "KVK सत्यापन के तहत",
        "under KVK recommendation": "KVK सिफारिश के तहत",
        "under KVK guidance": "KVK मार्गदर्शन के तहत",
        "under local KVK supervision": "स्थानीय KVK देखरेख में",
        "under label guidelines": "लेबल दिशानिर्देशों के अनुसार",
        "only under official permit": "केवल आधिकारिक अनुमति के तहत",
        "under official permit": "आधिकारिक अनुमति के तहत",
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
        "Tebuconazole": "ટેબ્યુકોનાઝોલ",
        "Ferrous Sulfate": "ફેરસ સલ્ફેટ",
        "Citric Acid": "સાઇટ્રિક એસિડ",
        "Zinc Sulfate": "ઝિંક સલ્ફેટ",
        "Imidacloprid": "ઈમિડાક્લોપ્રિડ",
        "Thiamethoxam": "થાયામેથોક્સામ",
        "Copper Oxychloride": "કોપર ઓક્સીક્લોરાઇડ",
        "Streptocycline": "સ્ટ્રેપ્ટોસાયક્લીન",
        "Chlorantraniliprole": "ક્લોરાન્ટ્રાનિલીપ્રોલ",
        "Acetamiprid": "એસિટામિપ્રિડ",
        "Flonicamid": "ફ્લોનિકામિડ",
        "Diafenthiuron": "ડાયફેન્થિયુરોન",
        "Spinetoram": "સ્પીનેટોરામ",
        "Calcium Nitrate": "કેલ્શિયમ નાઇટ્રેટ",
        "Boron": "બોરોન",
        "Hexaconazole": "હેક્ઝાકોનાઝોલ",
        "Sulfur": "સલ્ફર",
        "Wettable Sulfur": "વેટેબલ સલ્ફર",
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
        "Tebuconazole": "टेबुकोनाज़ोल",
        "Ferrous Sulfate": "फेरस सल्फेट",
        "Citric Acid": "साइट्रिक एसिड",
        "Zinc Sulfate": "जिंक सल्फेट",
        "Imidacloprid": "इमिडाक्लोप्रिड",
        "Thiamethoxam": "थायमेथॉक्सम",
        "Copper Oxychloride": "कॉपर ऑक्सीक्लोराइड",
        "Streptocycline": "स्ट्रेप्टोसाइक्लिन",
        "Chlorantraniliprole": "क्लोरेंट्रानिलीप्रोल",
        "Acetamiprid": "एसिटामिप्रिड",
        "Flonicamid": "फ्लोनिकामिड",
        "Diafenthiuron": "डायफेन्थियूरॉन",
        "Spinetoram": "स्पिनिटोरम",
        "Calcium Nitrate": "कैल्शियम नाइट्रेट",
        "Boron": "बोरॉन",
        "Hexaconazole": "हेक्साकोनाज़ोल",
        "Sulfur": "सल्फर",
        "Wettable Sulfur": "घुलनशील सल्फर",
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

    return re.sub(r"\[Recommended:\s*(.+?)\]", repl, text, flags=re.IGNORECASE)


_AGRONOMIC_PATTERNS = [
    (
        re.compile(r"^\[Recommended:\s*(.+?)\]$", re.IGNORECASE),
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
        re.compile(r"^Consult your local Krishi Vigyan Kendra \(KVK\) or agriculture extension officer for ([^\.]+?)(?:\.\s*Calibrate spray application for (.+?)\.?)?\.?$", re.IGNORECASE),
        {
            "gu": lambda m: f"{m.group(1)} માટે તમારા સ્થાનિક કૃષિ વિજ્ઞાન કેન્દ્ર (KVK) અથવા ખેતીવાડી વિસ્તરણ અધિકારીની સલાહ લો." + (f" {m.group(2)} માટે સ્પ્રેની માત્રા ગોઠવો." if m.group(2) else ""),
            "hi": lambda m: f"{m.group(1)} के लिए अपने स्थानीय कृषि विज्ञान केंद्र (KVK) या कृषि विस्तार अधिकारी से परामर्श करें।" + (f" {m.group(2)} के लिए स्प्रे का छिड़काव समायोजित करें।" if m.group(2) else ""),
        }
    ),
]


def resolve_agronomic_translation(text: str, target_code: str) -> str | None:
    """Returns direct high-quality verified translation for known agronomic phrases."""
    if not text or target_code not in ("hi", "gu"):
        return None
    clean = text.strip()

    # Direct match for chemical recommendations with or without brackets
    if clean.startswith("[Recommended:") and clean.endswith("]"):
        return translate_treatment_recommendation(clean, target_code)

    dict_for_lang = _AGRONOMIC_TRANSLATIONS.get(target_code, {})
    if clean in dict_for_lang:
        return dict_for_lang[clean]

    clean_lower = clean.lower().rstrip(".")
    for k, v in dict_for_lang.items():
        if k.lower().rstrip(".") == clean_lower:
            return v

    for pattern, lang_map in _AGRONOMIC_PATTERNS:
        m = pattern.match(clean)
        if m and target_code in lang_map:
            return lang_map[target_code](m)
    return None


async def translate_batch_indictrans(texts: list[str], target_lang: str) -> list[str]:
    """Translate multiple texts via the configured IndicTrans2 FastAPI service.

    Splits paragraphs into sentence-level chunks, translates in batch, and reassembles them.
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
        "User-Agent": "SmartFarmingBackend/2.0",
    }
    gateway_key = getattr(settings, "GATEWAY_API_KEY", None) or os.getenv("GATEWAY_SECRET")
    if gateway_key:
        clean_key = str(gateway_key).strip().strip('"').strip("'")
        if clean_key:
            headers["Authorization"] = f"Bearer {clean_key}"

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
        "User-Agent": "SmartFarmingBackend/2.0",
    }
    gateway_key = getattr(settings, "GATEWAY_API_KEY", None) or os.getenv("GATEWAY_SECRET")
    if gateway_key:
        clean_key = str(gateway_key).strip().strip('"').strip("'")
        if clean_key:
            headers["Authorization"] = f"Bearer {clean_key}"

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

    # 1. Resolve known agronomic translations directly (instant, verified high accuracy)
    for idx, text in enumerate(texts):
        if not text or not text.strip():
            results[idx] = text
            continue
        direct = resolve_agronomic_translation(text, target_code)
        if direct:
            results[idx] = direct

    # Prepare keys for single batch lookup in Redis for remaining texts
    items_to_lookup: list[tuple[int, str, str]] = []
    for idx, text in enumerate(texts):
        if results[idx] is None:
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

        # Primary: IndicTrans2 on Hugging Face Space AI microservice
        server_url = (getattr(settings, "TRANSLATION_SERVER_URL", "") or "").strip()
        if server_url and target_code in ("hi", "gu"):
            try:
                translated_missing = await translate_batch_indictrans(missing_texts, target_code)
            except Exception as exc:
                logger.warning("IndicTrans2 translation failed (%s); trying fallback translator.", exc)

        if translated_missing is None or len(translated_missing) != len(missing_texts):
            translated_missing = list(missing_texts)

        # Item-by-item verification: If any text from missing_texts is still untranslated English, run fallback
        if target_code in ("hi", "gu"):
            untranslated_sub_indices = []
            untranslated_sub_texts = []
            for i, (orig, trans) in enumerate(zip(missing_texts, translated_missing)):
                if any(c.isalpha() for c in orig) and (not trans or not any(ord(c) >= 0x0900 for c in trans)):
                    untranslated_sub_indices.append(i)
                    untranslated_sub_texts.append(orig)

            if untranslated_sub_texts:
                try:
                    fallback_res = await _fallback_translate_batch(untranslated_sub_texts, target_code)
                    if fallback_res:
                        for u_idx, fb_t in zip(untranslated_sub_indices, fallback_res):
                            if fb_t and any(ord(c) >= 0x0900 for c in fb_t):
                                translated_missing[u_idx] = fb_t
                except Exception as exc:
                    logger.warning("Fallback translation failed: %s", exc)

        cache_tasks = []
        for idx, trans_text, orig_text in zip(missing_indices, translated_missing, missing_texts):
            results[idx] = trans_text
            if trans_text and trans_text != orig_text and any(ord(c) >= 0x0900 for c in trans_text):
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

    keys = [
        "immediate_action", "treatment", "prevention", "monitoring",
        "safety_disclaimer", "recommendation", "action", "fertilizer",
        "pesticide", "irrigation", "prevention_tips"
    ]
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
            if "[Recommended:" in trans:
                trans = translate_treatment_recommendation(trans, target_code)
            translated_dict[k] = trans

    return translated_dict


def translate_batch_sync(texts: list[str], target_lang: str) -> list[str]:
    """Synchronous batch translation via IndicTrans2 server with direct agronomic resolution and robust fallback."""
    if not texts:
        return []
    target_code = normalize_language_code(target_lang)
    if target_code == "en":
        if not any(any(ord(c) >= 0x0900 for c in t) for t in texts if t):
            return texts

    results: list[str | None] = [None] * len(texts)
    missing_indices: list[int] = []
    missing_texts: list[str] = []

    # 1. Resolve known agronomic translations directly (instant, verified high accuracy)
    for idx, text in enumerate(texts):
        if not text or not text.strip():
            results[idx] = text
            continue
        direct = resolve_agronomic_translation(text, target_code)
        if direct:
            results[idx] = direct
        else:
            missing_indices.append(idx)
            missing_texts.append(text)

    if missing_texts:
        translated_missing: list[str] | None = None

        # Primary: IndicTrans2 on Hugging Face Space AI microservice
        server_url = (getattr(settings, "TRANSLATION_SERVER_URL", "") or "").strip()
        if server_url and target_code in ("hi", "gu"):
            try:
                translated_missing = translate_batch_indictrans_sync(missing_texts, target_code)
            except Exception as exc:
                logger.warning("IndicTrans2 sync translation failed (%s); trying fallback translator", exc)

        if translated_missing is None or len(translated_missing) != len(missing_texts):
            translated_missing = list(missing_texts)

        # Item-by-item verification: If any text from missing_texts is still untranslated English, run fallback
        if target_code in ("hi", "gu"):
            untranslated_sub_indices = []
            untranslated_sub_texts = []
            for i, (orig, trans) in enumerate(zip(missing_texts, translated_missing)):
                if any(c.isalpha() for c in orig) and (not trans or not any(ord(c) >= 0x0900 for c in trans)):
                    untranslated_sub_indices.append(i)
                    untranslated_sub_texts.append(orig)

            if untranslated_sub_texts:
                try:
                    fallback_res = _fallback_translate_batch_sync(untranslated_sub_texts, target_code)
                    if fallback_res:
                        for u_idx, fb_t in zip(untranslated_sub_indices, fallback_res):
                            if fb_t and any(ord(c) >= 0x0900 for c in fb_t):
                                translated_missing[u_idx] = fb_t
                except Exception as exc:
                    logger.warning("Fallback sync translation failed: %s", exc)

        for idx, trans_text in zip(missing_indices, translated_missing):
            results[idx] = trans_text

    return [r if r is not None else "" for r in results]


def translate_recommendation_sync(recommendation: dict[str, Any], target_lang: str) -> dict[str, Any]:
    """Synchronous recommendation translation for background worker jobs."""
    target_code = normalize_language_code(target_lang)
    if target_code == "en":
        return recommendation

    keys = [
        "immediate_action", "treatment", "prevention", "monitoring",
        "safety_disclaimer", "recommendation", "action", "fertilizer",
        "pesticide", "irrigation", "prevention_tips"
    ]
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
            if "[Recommended:" in trans:
                trans = translate_treatment_recommendation(trans, target_code)
            translated_dict[k] = trans

    return translated_dict
