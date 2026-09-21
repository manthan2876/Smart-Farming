export type SupportedLang = "en" | "hi" | "gu" | "English" | "Hindi" | "Gujarati";

export function normalizeLangCode(lang?: string): "en" | "hi" | "gu" {
  if (!lang) return "en";
  const l = lang.trim().toLowerCase();
  if (l.startsWith("hi")) return "hi";
  if (l.startsWith("gu")) return "gu";
  return "en";
}

// ── Crops ────────────────────────────────────────────────────────────────
const cropsMap: Record<string, Record<"en" | "hi" | "gu", string>> = {
  cotton: { en: "Cotton", hi: "कपास", gu: "કપાસ" },
  groundnut: { en: "Groundnut", hi: "मूंगफली", gu: "મગફળી" },
  "pepper bell": { en: "Pepper Bell", hi: "शिमला मिर्च", gu: "કેપ્સિકમ" },
  pepper_bell: { en: "Pepper Bell", hi: "शिमला मिर्च", gu: "કેપ્સિકમ" },
  potato: { en: "Potato", hi: "आलू", gu: "બટાકા" },
  tomato: { en: "Tomato", hi: "टमाटर", gu: "ટામેટા" },
};

export function translateCrop(crop?: string | null, lang?: string): string {
  if (!crop) return "Unknown Crop";
  const code = normalizeLangCode(lang);
  const key = crop.trim().toLowerCase();
  return cropsMap[key]?.[code] || crop;
}

// ── Diseases ─────────────────────────────────────────────────────────────
const diseasesMap: Record<string, Record<"en" | "hi" | "gu", string>> = {
  "alternaria leaf spot": { en: "Alternaria Leaf Spot", hi: "अल्टरनेरिया पत्ती धब्बा", gu: "અલ્ટરનેરિયા પાન ટપકાં" },
  "althernaria leaf spot": { en: "Alternaria Leaf Spot", hi: "अल्टरनेरिया पत्ती धब्बा", gu: "અલ્ટરનેરિયા પાન ટપકાં" },
  "bacterial blight": { en: "Bacterial Blight", hi: "जीवाणु झुलसा", gu: "જીવાણુજન્ય સુકારો" },
  "bacterial spot": { en: "Bacterial Spot", hi: "जीवाणु धब्बा रोग", gu: "જીવાણુજન્ય ટપકાં" },
  bacteria: { en: "Bacterial Infection", hi: "जीवाणु संक्रमण", gu: "જીવાણુજન્ય ચેપ" },
  "cercospora leaf spot": { en: "Cercospora Leaf Spot", hi: "सर्कोस्पोरा पत्ती धब्बा", gu: "સર્કોસ્પોરા પાન ટપકાં" },
  "curl virus": { en: "Curl Virus", hi: "पर्ण कुंचन विषाणु", gu: "પાન વળવું (કોકડવા)" },
  "early blight": { en: "Early Blight", hi: "अगेती झुलसा", gu: "અગેતી સુકારો" },
  edema: { en: "Edema", hi: "एडेमा (जलभराव विकार)", gu: "એડીમા" },
  fungi: { en: "Fungal Infection", hi: "फफूंद संक्रमण", gu: "ફૂગજન્ય ચેપ" },
  "fusarium wilt": { en: "Fusarium Wilt", hi: "उकठा (फ्यूजेरियम विल्ट)", gu: "સુકારો (ફ્યુઝેરિયમ વિલ્ટ)" },
  healthy: { en: "Healthy Leaf", hi: "स्वस्थ पौधा", gu: "તંદુરસ્ત પાક" },
  "late blight": { en: "Late Blight", hi: "पछेती झुलसा", gu: "પછેતી સુકારો" },
  "leaf curl": { en: "Leaf Curl", hi: "पत्ती मरोड़ (लीफ कर्ल)", gu: "પાન વળવાનો રોગ" },
  "leaf spot": { en: "Leaf Spot", hi: "पत्ती धब्बा रोग", gu: "પાનના ટપકાંનો રોગ" },
  "mold leaf": { en: "Leaf Mold", hi: "पत्ती फफूंद (मोल्ड)", gu: "પાનની ફૂગ (મોલ્ડ લીફ)" },
  "mosaic virus": { en: "Mosaic Virus", hi: "मोजेक वायरस", gu: "મોઝેક વાઈરસ" },
  nematode: { en: "Nematode Damage", hi: "सूत्रकृमि (नेमाटोड)", gu: "કૃમિ (નેમાટોડ)" },
  "nutrition deficiency": { en: "Nutrition Deficiency", hi: "पोषक तत्वों की कमी", gu: "પોષક તત્વોની ખામી" },
  pest: { en: "Pest Infestation", hi: "कीट प्रकोप", gu: "જીવાતનો ઉપદ્રવ" },
  "powdery mildew": { en: "Powdery Mildew", hi: "सफेद चूर्ण (छाछिया)", gu: "ભૂકી છારો" },
  rosette: { en: "Rosette", hi: "गुच्छा रोग (रोजेट)", gu: "ગુચ્છારોગ (રોઝેટ)" },
  rust: { en: "Rust", hi: "गेरुआ (रतुआ)", gu: "ગેરુ (રતવો)" },
  septoria: { en: "Septoria Leaf Spot", hi: "सेप्टोरिया पत्ती धब्बा", gu: "સેપ્ટોરિયા પાન ટપકાં" },
  "target spot": { en: "Target Spot", hi: "टारगेट स्पॉट (लक्ष्य धब्बा)", gu: "ટાર્ગેટ સ્પોટ" },
  "verticillium wilt": { en: "Verticillium Wilt", hi: "वर्टिसिलियम विल्ट", gu: "વર્ટિસિલિયમ સુકારો" },
  virus: { en: "Viral Infection", hi: "विषाणु (वायरस)", gu: "વાઈરસનો ચેપ" },
  "yellow curl virus": { en: "Yellow Leaf Curl Virus", hi: "पीला पत्ती मरोड़ वायरस", gu: "પીળો પર્ણ વલન વાઈરસ" },
};

export function translateDisease(disease?: string | null, lang?: string): string {
  if (!disease) return "Undetermined Condition";
  const code = normalizeLangCode(lang);
  const key = disease.trim().toLowerCase();
  return diseasesMap[key]?.[code] || disease;
}

// ── Pests ────────────────────────────────────────────────────────────────
const pestsMap: Record<string, Record<"en" | "hi" | "gu", string>> = {
  aphid: { en: "Aphid", hi: "माहू (चेपा)", gu: "મોલોમશી" },
  aphids: { en: "Aphids", hi: "माहू (चेपा)", gu: "મોલોમશી" },
  "army worm": { en: "Army Worm", hi: "सैनिक कीट (लश्करी सुंडी)", gu: "લશ્કરી ઈયળ" },
  army_worm: { en: "Army Worm", hi: "सैनिक कीट (लश्करी सुंडी)", gu: "લશ્કરી ઈયળ" },
  "leaf miner": { en: "Leaf Miner", hi: "लीफ माइनर (सुरंग कीट)", gu: "પાન કોરીયુ" },
  leaf_miner: { en: "Leaf Miner", hi: "लीफ माइनर (सुरंग कीट)", gu: "પાન કોરીયુ" },
  "spider mite": { en: "Spider Mite", hi: "लाल मकड़ी (माइट)", gu: "પાન કથીરી (લાલ મકડી)" },
  spider_mite: { en: "Spider Mite", hi: "लाल मकड़ी (माइट)", gu: "પાન કથીરી (લાલ મકડી)" },
};

export function translatePest(pest?: string | null, lang?: string): string {
  if (!pest) return "Pest";
  const code = normalizeLangCode(lang);
  const key = pest.trim().toLowerCase();
  return pestsMap[key]?.[code] || pest;
}

// ── Severity ─────────────────────────────────────────────────────────────
const severityMap: Record<string, Record<"en" | "hi" | "gu", string>> = {
  low: { en: "Low", hi: "कम", gu: "ઓછી" },
  moderate: { en: "Moderate", hi: "मध्यम", gu: "મધ્યમ" },
  high: { en: "High", hi: "उच्च", gu: "ઉચ્ચ" },
  critical: { en: "Critical", hi: "गंभीर", gu: "ગંભીર" },
  severe: { en: "Severe", hi: "गंभीर", gu: "ગંભીર" },
};

export function translateSeverityBucket(severity?: string | null, lang?: string): string {
  if (!severity) return "N/A";
  const code = normalizeLangCode(lang);
  const key = severity.trim().toLowerCase();
  return severityMap[key]?.[code] || severity;
}

// ── Weather ──────────────────────────────────────────────────────────────
const weatherMap: Record<string, Record<"en" | "hi" | "gu", string>> = {
  clear: { en: "Clear Sky", hi: "साफ आसमान", gu: "સ્વચ્છ આકાશ" },
  sunny: { en: "Sunny", hi: "धूप", gu: "તડકો" },
  clouds: { en: "Cloudy", hi: "बादल छाए रहेंगे", gu: "વાદળછાયું" },
  cloudy: { en: "Cloudy", hi: "बादल छाए रहेंगे", gu: "વાદળછાયું" },
  rain: { en: "Rainy", hi: "बारिश", gu: "વરસાદ" },
  rainy: { en: "Rainy", hi: "बारिश", gu: "વરસાદ" },
  drizzle: { en: "Drizzle", hi: "बूंदाबांदी", gu: "ઝરમર વરસાદ" },
  thunderstorm: { en: "Thunderstorm", hi: "आंधी-तूफान", gu: "ગાજવીજ સાથે વાવાઝોડું" },
  windy: { en: "Windy", hi: "तेज हवा", gu: "પવનવાળું" },
  fog: { en: "Foggy", hi: "कोहरा", gu: "ધુમ્મસ" },
  haze: { en: "Haze", hi: "धुंध", gu: "ઝાકળ" },
  mist: { en: "Mist", hi: "धुंध", gu: "ધુમ્મસ" },
};

export function translateWeather(weather?: string | null, lang?: string): string {
  if (!weather) return "Clear";
  const code = normalizeLangCode(lang);
  const key = weather.trim().toLowerCase();
  return weatherMap[key]?.[code] || weather;
}

// ── Alerts ───────────────────────────────────────────────────────────────
const alertTitlesMap: Record<string, Record<"en" | "hi" | "gu", string>> = {
  "weather advisory": { en: "Weather Advisory", hi: "मौसम सलाह", gu: "હવામાન સલાહ" },
  "heavy rain alert": { en: "Heavy Rain Alert", hi: "भारी बारिश की चेतावनी", gu: "ભારે વરસાદની ચેતવણી" },
  "rain warning": { en: "Rain Warning", hi: "बारिश की चेतावनी", gu: "વરસાદની ચેતવણી" },
  "high humidity alert": { en: "High Humidity Alert", hi: "उच्च आर्द्रता चेतावनी", gu: "વધુ ભેજની ચેતવણી" },
  "extreme heat advisory": { en: "Extreme Heat Advisory", hi: "अत्यधिक गर्मी की सलाह", gu: "અતિશય ગરમીની સલાહ" },
  "heat advisory": { en: "Heat Advisory", hi: "गर्मी की सलाह", gu: "ગરમીની સલાહ" },
  "pest advisory": { en: "Pest Advisory", hi: "कीट सलाह", gu: "જીવાત સલાહ" },
  "pest warning": { en: "Pest Warning", hi: "कीट चेतावनी", gu: "જીવાત ચેતવણી" },
  "disease outbreak alert": { en: "Disease Outbreak Alert", hi: "रोग प्रकोप चेतावनी", gu: "રોગચાળાની ચેતવણી" },
  "expert review complete": { en: "Expert Review Complete", hi: "विशेषज्ञ समीक्षा पूर्ण", gu: "નિષ્ણાત સમીક્ષા પૂર્ણ" },
  "expert review completed": { en: "Expert Review Complete", hi: "विशेषज्ञ समीक्षा पूर्ण", gu: "નિષ્ણાત સમીક્ષા પૂર્ણ" },
  "specialist review completed": { en: "Specialist Review Completed", hi: "विशेषज्ञ समीक्षा पूर्ण", gu: "નિષ્ણાત સમીક્ષા પૂર્ણ" },
};

export function translateAlertTitle(title?: string | null, lang?: string): string {
  if (!title) return "Alert";
  const code = normalizeLangCode(lang);
  const key = title.trim().toLowerCase();
  return alertTitlesMap[key]?.[code] || title;
}
