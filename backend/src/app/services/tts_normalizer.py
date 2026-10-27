"""TTS text normalization and number expansion for Indic-TTS."""
from __future__ import annotations

import re

GU_UNITS = [
    "શૂન્ય", "એક", "બે", "ત્રણ", "ચાર", "પાંચ", "છ", "સાત", "આઠ", "નવ",
    "દસ", "અગિયાર", "બાર", "તેર", "ચૌદ", "પંદર", "સોળ", "સત્તર", "અઢાર", "ઓગણીસ",
    "વીસ", "એકવીસ", "બાવીસ", "ત્રેવીસ", "ચોવીસ", "પચ્ચીસ", "છવીસ", "સત્તાવીસ", "અઠ્ઠાવીસ", "ઓગણત્રીસ",
    "ત્રીસ", "એકત્રીસ", "બત્રીસ", "તેત્રીસ", "ચોત્રીસ", "પાંત્રીસ", "છત્રીસ", "સાડત્રીસ", "આડત્રીસ", "ઓગણચાલીસ",
    "ચાલીસ", "એકતાલીસ", "બેતાલીસ", "તેતાલીસ", "ચુંમાલીસ", "પિસ્તાલીસ", "છેતાલીસ", "સુડતાલીસ", "અડતાલીસ", "ઓગણપચાસ",
    "પચાસ", "એકાવન", "બાવન", "ત્રેપન", "ચોપન", "પંચાવન", "છપ્પન", "સત્તાવન", "અઠ્ઠાવન", "ઓગણસાઠ",
    "સાઠ", "એકસઠ", "બાસઠ", "ત્રેસઠ", "ચોસઠ", "પાંસઠ", "છાસઠ", "સડસઠ", "અડસઠ", "ઓગણસિત્તેર",
    "સિત્તેર", "એકોતેર", "બોતેર", "તોતેર", "ચુમોતેર", "પંચોતેર", "છોતેર", "સંતોતેર", "અઠોતેર", "ઓગણાએંસી",
    "એંસી", "એક્યાસી", "બ્યાસી", "ત્યાસી", "ચોર્યાસી", "પંચાસી", "છ્યાસી", "સત્યાસી", "અઠ્યાસી", "નેવ્યાસી",
    "નેવું", "એકાણું", "બાણું", "ત્રાણું", "ચોરાણું", "પંચાણું", "છન્નું", "સત્તાણું", "અઠ્ઠાણું", "નવ્વાણું",
    "સો"
]

HI_UNITS = [
    "शून्य", "एक", "दो", "तीन", "चार", "पांच", "छह", "सात", "आठ", "नौ",
    "दस", "ग्यारह", "बारह", "तेरह", "चौदह", "पंद्रह", "सोलह", "सत्रह", "अठारह", "उन्नीस",
    "बीस", "इक्कीस", "बाईस", "तेईस", "चौबीस", "पच्चीस", "छब्बीस", "सत्ताईस", "अट्ठाइस", "उनतीस",
    "तीस", "इकत्तीस", "बत्तीस", "तैंतीस", "चौंतीस", "पैंतीस", "छत्तीस", "सैंतीस", "अड़तीस", "उनतालीस",
    "चालीस", "इकतालीस", "बयालीस", "तैंतालीस", "चवालीस", "पैंतालीस", "छियालीस", "सैंतालीस", "अड़तालीस", "उनचास",
    "पचास", "इक्यावन", "बावन", "तिरेपन", "चौवन", "पचपन", "छप्पन", "सत्तावन", "अट्ठावन", "उनसठ",
    "साठ", "इकसठ", "बासठ", "तिरेसठ", "चौंसठ", "पैंसठ", "छियासठ", "सरसठ", "अड़सठ", "उनहत्तर",
    "सत्तर", "इकहत्तर", "बहत्तर", "तिहत्तर", "चौहत्तर", "पचहत्तर", "छिहत्तर", "सतहत्तर", "अठहत्तर", "उनासी",
    "अस्सी", "इक्यासी", "बयासी", "तिरासी", "चौरासी", "पचासी", "छियासी", "सत्तासी", "अट्ठासी", "नवासी",
    "नब्बे", "इक्यानवे", "बानवे", "तिरानवे", "चौरानवे", "पंचानवे", "छियानवे", "सत्तानवे", "अट्ठानवे", "निन्यानवे",
    "सौ"
]


def int_to_words(n: int, lang: str) -> str:
    """Convert integer to native Gujarati or Hindi words."""
    units = GU_UNITS if lang == "gu" else HI_UNITS
    if 0 <= n <= 100:
        return units[n]
    if n < 1000:
        hundred = n // 100
        rem = n % 100
        h_word = "સો" if lang == "gu" else "सौ"
        if rem == 0:
            return f"{units[hundred]} {h_word}"
        return f"{units[hundred]} {h_word} {int_to_words(rem, lang)}"
    if n < 100000:
        thousand = n // 1000
        rem = n % 1000
        t_word = "હજાર" if lang == "gu" else "हज़ार"
        if rem == 0:
            return f"{int_to_words(thousand, lang)} {t_word}"
        return f"{int_to_words(thousand, lang)} {t_word} {int_to_words(rem, lang)}"
    if n < 10000000:
        lakh = n // 100000
        rem = n % 100000
        l_word = "લાખ" if lang == "gu" else "लाख"
        if rem == 0:
            return f"{int_to_words(lakh, lang)} {l_word}"
        return f"{int_to_words(lakh, lang)} {l_word} {int_to_words(rem, lang)}"
    return " ".join(units[int(d)] for d in str(n))


def expand_numbers_for_tts(text: str, lang: str) -> str:
    """Expand numbers, decimals, percentages, and units into speakable words for Indic-TTS."""
    if not text or lang not in ("gu", "hi"):
        return text

    # 1. Convert Indic numerals (Gujarati ૦-૯ & Devanagari ०-९) to standard ASCII 0-9
    for i in range(10):
        text = text.replace(chr(0x0AE6 + i), str(i))  # Gujarati
        text = text.replace(chr(0x0966 + i), str(i))  # Devanagari

    # 2. Units / symbols replacement
    if lang == "gu":
        text = re.sub(r"\b(\d+)\s*%", r"\1 ટકા", text)
        text = re.sub(r"\b(\d+)\s*°\s*[cC]", r"\1 ડિગ્રી સેલ્સિયસ", text)
        text = text.replace(" / ", " પ્રતિ ")
        text = text.replace("/", " પ્રતિ ")
        point_word = "પોઇન્ટ"
    else:
        text = re.sub(r"\b(\d+)\s*%", r"\1 प्रतिशत", text)
        text = re.sub(r"\b(\d+)\s*°\s*[cC]", r"\1 डिग्री सेल्सियस", text)
        text = text.replace(" / ", " प्रति ")
        text = text.replace("/", " प्रति ")
        point_word = "दशमलव"

    units = GU_UNITS if lang == "gu" else HI_UNITS

    # 3. Replace decimal numbers (e.g. 2.5, 33.15, 0.75)
    def replace_decimal(match: re.Match) -> str:
        whole = int(match.group(1))
        frac = match.group(2)
        whole_str = int_to_words(whole, lang)
        frac_words = " ".join(units[int(d)] for d in frac)
        return f"{whole_str} {point_word} {frac_words}"

    text = re.sub(r"\b(\d+)\.(\d+)\b", replace_decimal, text)

    # 4. Replace remaining standalone integers
    def replace_int(match: re.Match) -> str:
        val = int(match.group(1))
        return int_to_words(val, lang)

    text = re.sub(r"\b(\d+)\b", replace_int, text)

    # 5. Clean up any extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text

