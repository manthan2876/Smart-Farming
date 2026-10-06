/// Agricultural Domain Lexicon
///
/// Curated, precise botanical and agronomic translations for Crops, Diseases,
/// Pests, Severity stages, and Weather conditions across English, Hindi, and Gujarati.
class DomainTranslations {
  static String normalizeLang(String? lang) {
    if (lang == null) return 'en';
    final l = lang.trim().toLowerCase();
    if (l.startsWith('hi')) return 'hi';
    if (l.startsWith('gu')) return 'gu';
    return 'en';
  }

  // ── Crops ────────────────────────────────────────────────────────────────
  static const Map<String, Map<String, String>> _crops = {
    'cotton': {'en': 'Cotton', 'hi': 'कपास', 'gu': 'કપાસ'},
    'groundnut': {'en': 'Groundnut', 'hi': 'मूंगफली', 'gu': 'મગફળી'},
    'pepper bell': {'en': 'Pepper Bell', 'hi': 'शिमला मिर्च', 'gu': 'કેપ્સિકમ / ભોળર મરચાં'},
    'pepper_bell': {'en': 'Pepper Bell', 'hi': 'शिमला मिर्च', 'gu': 'કેપ્સિકમ / ભોળર મરચાં'},
    'capsicum': {'en': 'Pepper Bell', 'hi': 'शिमला मिर्च', 'gu': 'કેપ્સિકમ / ભોળર મરચાં'},
    'potato': {'en': 'Potato', 'hi': 'आलू', 'gu': 'બટાકા'},
    'tomato': {'en': 'Tomato', 'hi': 'टमाटर', 'gu': 'ટામેટા'},
  };

  static String translateCrop(String? crop, String lang) {
    if (crop == null || crop.isEmpty) return 'Unknown Crop';
    final code = normalizeLang(lang);
    final key = crop.trim().toLowerCase();
    final entry = _crops[key];
    if (entry != null && entry[code] != null) return entry[code]!;
    return crop;
  }

  // ── Diseases & Conditions ────────────────────────────────────────────────
  static const Map<String, Map<String, String>> _diseases = {
    'alternaria leaf spot': {'en': 'Alternaria Leaf Spot', 'hi': 'अल्टरनेरिया पत्ती धब्बा', 'gu': 'અલ્ટરનેરિયા પાનના ટપકાં'},
    'althernaria leaf spot': {'en': 'Alternaria Leaf Spot', 'hi': 'अल्टरनेरिया पत्ती धब्बा', 'gu': 'અલ્ટરનેરિયા પાનના ટપકાં'},
    'bacterial blight': {'en': 'Bacterial Blight', 'hi': 'जीवाणु झुलसा', 'gu': 'જીવાણુજન્ય સુકારો (અંગારિયો)'},
    'bacterial spot': {'en': 'Bacterial Spot', 'hi': 'जीवाणु धब्बा रोग', 'gu': 'જીવાણુજન્ય ટપકાંનો રોગ'},
    'bacteria': {'en': 'Bacterial Infection', 'hi': 'जीवाणु संक्रमण', 'gu': 'જીવાણુજન્ય ચેપ'},
    'cercospora leaf spot': {'en': 'Cercospora Leaf Spot', 'hi': 'सर्कोस्पोरा पत्ती धब्बा', 'gu': 'સર્કોસ્પોરા પાનના ટપકાં (ટીક્કા)'},
    'curl virus': {'en': 'Curl Virus', 'hi': 'पर्ण कुंचन विषाणु', 'gu': 'કોકડવા / પર્ણ મોડ વાઈરસ'},
    'early blight': {'en': 'Early Blight', 'hi': 'अगेती झुलसा', 'gu': 'અગેતરો સુકારો (અંગારિયો)'},
    'edema': {'en': 'Edema', 'hi': 'एडेमा (जलभराव विकार)', 'gu': 'એડીમા (જલભરાવ વિકાર)'},
    'fungi': {'en': 'Fungal Infection', 'hi': 'फफूंद संक्रमण', 'gu': 'ફૂગજન્ય ચેપ'},
    'fusarium wilt': {'en': 'Fusarium Wilt', 'hi': 'उकठा (फ्यूजेरियम विल्ट)', 'gu': 'સુકારો (ફ્યુઝેરિયમ વિલ્ટ)'},
    'healthy': {'en': 'Healthy Leaf', 'hi': 'स्वस्थ पौधा', 'gu': 'તંદુરસ્ત પાક'},
    'late blight': {'en': 'Late Blight', 'hi': 'पछेती झुलसा', 'gu': 'પછેતરો સુકારો (અંગારિયો)'},
    'leaf curl': {'en': 'Leaf Curl', 'hi': 'पत्ती मरोड़ (लीफ कर्ल)', 'gu': 'કોકડવા (પાન વળવાનો રોગ)'},
    'leaf spot': {'en': 'Leaf Spot', 'hi': 'पत्ती धब्बा रोग', 'gu': 'પાનના ટપકાંનો રોગ'},
    'mold leaf': {'en': 'Leaf Mold', 'hi': 'पत्ती फफूंद (मोल्ड)', 'gu': 'પાનની ફૂગ (મોલ્ડ)'},
    'mosaic virus': {'en': 'Mosaic Virus', 'hi': 'मोजेक वायरस', 'gu': 'મોઝેક વાઈરસ (વિચિત્રતા)'},
    'nematode': {'en': 'Nematode Damage', 'hi': 'सूत्रकृमि (नेमाटोड)', 'gu': 'કૃમિ (નેમાટોડ)'},
    'nutrition deficiency': {'en': 'Nutrition Deficiency', 'hi': 'पोषक तत्वों की कमी', 'gu': 'પોષક તત્વોની ખામી'},
    'pest': {'en': 'Pest Infestation', 'hi': 'कीट प्रकोप', 'gu': 'જીવાતનો ઉપદ્રવ'},
    'powdery mildew': {'en': 'Powdery Mildew', 'hi': 'छाछिया (पाउडरी माइल्ड्यू)', 'gu': 'ભૂકી છારો (છાછિયો)'},
    'rosette': {'en': 'Rosette', 'hi': 'गुच्छा रोग (रोजेट)', 'gu': 'ગુચ્છારોગ (રોઝેટ)'},
    'rust': {'en': 'Rust', 'hi': 'गेरुआ (रतुआ)', 'gu': 'ગેરુ / રતવો'},
    'septoria': {'en': 'Septoria Leaf Spot', 'hi': 'सेप्टोरिया पत्ती धब्बा', 'gu': 'સેપ્ટોરિયા પાનના ટપકાં'},
    'target spot': {'en': 'Target Spot', 'hi': 'टारगेट स्पॉट (लक्ष्य धब्बा)', 'gu': 'ટાર્ગેટ સ્પોટ (ગોળ ટપકાં)'},
    'verticillium wilt': {'en': 'Verticillium Wilt', 'hi': 'वर्टिसिलियम विल्ट', 'gu': 'વર્ટિસિલિયમ સુકારો'},
    'virus': {'en': 'Viral Infection', 'hi': 'विषाणु (वायरस)', 'gu': 'વાઈરસનો ચેપ'},
    'yellow curl virus': {'en': 'Yellow Leaf Curl Virus', 'hi': 'पीला पत्ती मरोड़ वायरस', 'gu': 'પીળો કોકડવા વાઈરસ'},
  };

  static String translateDisease(String? disease, String lang) {
    if (disease == null || disease.isEmpty) return 'Undetermined Condition';
    final code = normalizeLang(lang);
    final key = disease.trim().toLowerCase();
    final entry = _diseases[key];
    if (entry != null && entry[code] != null) return entry[code]!;
    return disease;
  }

  // ── Pests ────────────────────────────────────────────────────────────────
  static const Map<String, Map<String, String>> _pests = {
    'aphid': {'en': 'Aphid', 'hi': 'माहू (चेपा)', 'gu': 'મોલોમશી'},
    'aphids': {'en': 'Aphids', 'hi': 'माहू (चेपा)', 'gu': 'મોલોમશી'},
    'army worm': {'en': 'Army Worm', 'hi': 'सैनिक कीट (लश्करी सुंडी)', 'gu': 'લશ્કરી ઈયળ'},
    'army_worm': {'en': 'Army Worm', 'hi': 'सैनिक कीट (लश्करी सुंडी)', 'gu': 'લશ્કરી ઈયળ'},
    'leaf miner': {'en': 'Leaf Miner', 'hi': 'लीफ माइनर (सुरंग कीट)', 'gu': 'પાન કોરીયું (ચિતરી)'},
    'leaf_miner': {'en': 'Leaf Miner', 'hi': 'लीफ माइनर (सुरंग कीट)', 'gu': 'પાન કોરીયું (ચિતરી)'},
    'spider mite': {'en': 'Spider Mite', 'hi': 'लाल मकड़ी (माइट)', 'gu': 'રાતી કથીરી (લાલ મકડી)'},
    'spider_mite': {'en': 'Spider Mite', 'hi': 'लाल मकड़ी (माइट)', 'gu': 'રાતી કથીરી (લાલ મકડી)'},
  };

  static String translatePest(String? pest, String lang) {
    if (pest == null || pest.isEmpty) return 'Pest';
    final code = normalizeLang(lang);
    final key = pest.trim().toLowerCase();
    final entry = _pests[key];
    if (entry != null && entry[code] != null) return entry[code]!;
    return pest;
  }

  // ── Severity Buckets ─────────────────────────────────────────────────────
  static const Map<String, Map<String, String>> _severity = {
    'healthy': {'en': 'Healthy', 'hi': 'स्वस्थ', 'gu': 'તંદુરસ્ત'},
    'low': {'en': 'Low Severity', 'hi': 'कम प्रकोप', 'gu': 'ઓછો ઉપદ્રવ'},
    'moderate': {'en': 'Moderate Severity', 'hi': 'मध्यम प्रकोप', 'gu': 'મધ્યમ ઉપદ્રવ'},
    'medium': {'en': 'Moderate Severity', 'hi': 'मध्यम प्रकोप', 'gu': 'મધ્યમ ઉપદ્રવ'},
    'high': {'en': 'High Severity', 'hi': 'अधिक प्रकोप', 'gu': 'વધુ ઉપદ્રવ'},
    'severe': {'en': 'Severe Infection', 'hi': 'गंभीर संक्रमण', 'gu': 'ગંભીર ચેપ'},
    'critical': {'en': 'Critical Stage', 'hi': 'अत्यधिक गंभीर', 'gu': 'અત્યંત ગંભીર'},
  };

  static String translateSeverityBucket(String? bucket, String lang) {
    if (bucket == null || bucket.isEmpty) return '';
    final code = normalizeLang(lang);
    final key = bucket.trim().toLowerCase();
    final entry = _severity[key];
    if (entry != null && entry[code] != null) return entry[code]!;
    return bucket;
  }

  // ── Weather Conditions ───────────────────────────────────────────────────
  static const Map<String, Map<String, String>> _weather = {
    'clear': {'en': 'Clear Sky', 'hi': 'साफ आसमान', 'gu': 'સ્વચ્છ આકાશ'},
    'clear sky': {'en': 'Clear Sky', 'hi': 'साफ आसमान', 'gu': 'સ્વચ્છ આકાશ'},
    'sunny': {'en': 'Sunny', 'hi': 'धूप खिली', 'gu': 'તડકો'},
    'few clouds': {'en': 'Few Clouds', 'hi': 'हल्के बादल', 'gu': 'હળવા વાદળાં'},
    'scattered clouds': {'en': 'Scattered Clouds', 'hi': 'बिखरे बादल', 'gu': 'છૂટાછવાયા વાદળાં'},
    'broken clouds': {'en': 'Broken Clouds', 'hi': 'घने बादल', 'gu': 'વાદળછાયું'},
    'overcast': {'en': 'Overcast', 'hi': 'बादल छाए रहेंगे', 'gu': 'ઘેરાયેલું આકાશ'},
    'overcast clouds': {'en': 'Overcast Clouds', 'hi': 'बादल छाए रहेंगे', 'gu': 'ઘેરાયેલું આકાશ'},
    'light rain': {'en': 'Light Rain', 'hi': 'हल्की बारिश', 'gu': 'હળવો વરસાદ'},
    'moderate rain': {'en': 'Moderate Rain', 'hi': 'मध्यम बारिश', 'gu': 'મધ્યમ વરસાદ'},
    'heavy rain': {'en': 'Heavy Rain', 'hi': 'भारी बारिश', 'gu': 'ભારે વરસાદ'},
    'rain': {'en': 'Rainy', 'hi': 'बारिश', 'gu': 'વરસાદ'},
    'thunderstorm': {'en': 'Thunderstorm', 'hi': 'गरज के साथ बारिश', 'gu': 'ગાજવીજ સાથે વરસાદ'},
    'haze': {'en': 'Hazy', 'hi': 'धुंध', 'gu': 'ધુમ્મસભર્યું'},
    'mist': {'en': 'Mist', 'hi': 'हल्का कोहरा', 'gu': 'હળવું ધુમ્મસ'},
    'fog': {'en': 'Foggy', 'hi': 'घना कोहरा', 'gu': 'ગાઢ ધુમ્મસ'},
  };

  static String translateWeather(String? condition, String lang) {
    if (condition == null || condition.isEmpty) return 'Current Conditions';
    final code = normalizeLang(lang);
    final key = condition.trim().toLowerCase();
    final entry = _weather[key];
    if (entry != null && entry[code] != null) return entry[code]!;
    return condition;
  }

  // ── Alert Titles ─────────────────────────────────────────────────────────
  static const Map<String, Map<String, String>> _alertTitles = {
    'weather advisory': {'en': 'Weather Advisory', 'hi': 'मौसम सलाह', 'gu': 'હવામાન સલાહ'},
    'heavy rain alert': {'en': 'Heavy Rain Alert', 'hi': 'भारी बारिश की चेतावनी', 'gu': 'ભારે વરસાદની ચેતવણી'},
    'rain warning': {'en': 'Rain Warning', 'hi': 'बारिश की चेतावनी', 'gu': 'વરસાદની ચેતવણી'},
    'high humidity alert': {'en': 'High Humidity Alert', 'hi': 'उच्च आर्द्रता चेतावनी', 'gu': 'વધુ ભેજની ચેતવણી'},
    'extreme heat advisory': {'en': 'Extreme Heat Advisory', 'hi': 'अत्यधिक गर्मी की सलाह', 'gu': 'અતિશય ગરમીની સલાહ'},
    'heat advisory': {'en': 'Heat Advisory', 'hi': 'गर्मी की सलाह', 'gu': 'ગરમીની સલાહ'},
    'pest advisory': {'en': 'Pest Advisory', 'hi': 'कीट सलाह', 'gu': 'જીવાત સલાહ'},
    'pest warning': {'en': 'Pest Warning', 'hi': 'कीट चेतावनी', 'gu': 'જીવાત ચેતવણી'},
    'disease outbreak alert': {'en': 'Disease Outbreak Alert', 'hi': 'रोग प्रकोप चेतावनी', 'gu': 'રોગચાળાની ચેતવણી'},
    'expert review complete': {'en': 'Expert Review Complete', 'hi': 'विशेषज्ञ समीक्षा पूर्ण', 'gu': 'નિષ્ણાત સમીક્ષા પૂર્ણ'},
    'expert review completed': {'en': 'Expert Review Complete', 'hi': 'विशेषज्ञ समीक्षा पूर्ण', 'gu': 'નિષ્ણાત સમીક્ષા પૂર્ણ'},
    'specialist review completed': {'en': 'Specialist Review Completed', 'hi': 'विशेषज्ञ समीक्षा पूर्ण', 'gu': 'નિષ્ણાત સમીક્ષા પૂર્ણ'},
  };

  static String translateAlertTitle(String? title, String lang) {
    if (title == null || title.isEmpty) return 'Alert';
    final code = normalizeLang(lang);
    final key = title.trim().toLowerCase();
    final entry = _alertTitles[key];
    if (entry != null && entry[code] != null) return entry[code]!;

    if (code != 'en') {
      final sanitized = title.replaceAll('\u2014', ':');
      final lower = sanitized.toLowerCase();
      if (lower.contains('early blight') || lower.contains('leaf spot')) {
        final prefix = code == 'gu' ? 'પાનના ટપકાં / સુકારો જોખમ ચેતવણી' : 'अगेती झुलसा / पत्ती धब्बा जोखिम चेतावनी';
        final split = sanitized.split(':');
        return split.length > 1 ? '$prefix: ${split.last.trim()}' : prefix;
      }
      if (lower.contains('extreme heat') || lower.contains('heat stress')) {
        final prefix = code == 'gu' ? 'અતિશય ગરમીની ચેતવણી' : 'अत्यधिक गर्मी की चेतावनी';
        final split = sanitized.split(':');
        return split.length > 1 ? '$prefix: ${split.last.trim()}' : prefix;
      }
      if (lower.contains('heavy rain') || lower.contains('waterlogging') || lower.contains('flood')) {
        final prefix = code == 'gu' ? 'ભારે વરસાદ / પાણી ભરાવાની ચેતવણી' : 'भारी बारिश / जलभराव की चेतावनी';
        final split = sanitized.split(':');
        return split.length > 1 ? '$prefix: ${split.last.trim()}' : prefix;
      }
      if (lower.contains('expert review') || lower.contains('specialist')) {
        final prefix = code == 'gu' ? 'નિષ્ણાત સમીક્ષા પૂર્ણ' : 'विशेषज्ञ समीक्षा पूर्ण';
        final split = sanitized.split(':');
        return split.length > 1 ? '$prefix: ${split.last.trim()}' : prefix;
      }
    }

    return title;
  }
}