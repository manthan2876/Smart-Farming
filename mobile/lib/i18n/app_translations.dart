import 'domain_translations.dart';

/// Complete UI string translations for Smart Farming Mobile App
/// across English (en), Hindi (hi), and Gujarati (gu).
class AppTranslations {
  static const Map<String, Map<String, String>> _strings = {
    // ── App & Common ────────────────────────────────────────────────────────
    'appTitle': {'en': 'Smart Farming', 'hi': 'स्मार्ट फार्मिंग', 'gu': 'સ્માર્ટ ફાર્મિંગ'},
    'loading': {'en': 'Loading...', 'hi': 'लोड हो रहा है...', 'gu': 'લોડ થઈ રહ્યું છે...'},
    'error': {'en': 'Error', 'hi': 'त्रुटि', 'gu': 'ભૂલ'},
    'cancel': {'en': 'Cancel', 'hi': 'रद्द करें', 'gu': 'રદ કરો'},
    'save': {'en': 'Save', 'hi': 'सहेजें', 'gu': 'સાચવો'},
    'retry': {'en': 'Retry', 'hi': 'पुनः प्रयास करें', 'gu': 'ફરી પ્રયાસ કરો'},
    'language': {'en': 'Language', 'hi': 'भाषा', 'gu': 'ભાષા'},
    'selectLanguage': {'en': 'Select Language', 'hi': 'भाषा चुनें', 'gu': 'ભાષા પસંદ કરો'},

    // ── Authentication & Login ──────────────────────────────────────────────
    'loginTitle': {'en': 'Farmer Login', 'hi': 'किसान लॉगिन', 'gu': 'ખેડૂત લૉગિન'},
    'loginSubtitle': {'en': 'Sign in to monitor your crops and get AI diagnostics', 'hi': 'अपनी फसलों की निगरानी और AI निदान के लिए लॉगिन करें', 'gu': 'તમારા પાકની દેખરેખ અને AI નિદાન માટે લૉગિન કરો'},
    'identifierHint': {'en': 'Email or phone number', 'hi': 'ईमेल या मोबाइल नंबर', 'gu': 'ઈમેલ અથવા મોબાઈલ નંબર'},
    'passwordHint': {'en': 'Password', 'hi': 'पासवर्ड', 'gu': 'પાસવર્ડ'},
    'signInBtn': {'en': 'Sign In', 'hi': 'लॉगिन करें', 'gu': 'લૉગિન કરો'},
    'signingIn': {'en': 'Signing in...', 'hi': 'लॉगिन हो रहा है...', 'gu': 'લૉગિન થઈ રહ્યું છે...'},
    'farmersOnlyNotice': {'en': 'Mobile app is exclusively for registered farmers', 'hi': 'मोबाइल ऐप केवल पंजीकृत किसानों के लिए है', 'gu': 'મોબાઇલ એપ્લિકેશન માત્ર નોંધાયેલા ખેડૂતો માટે છે'},
    'accessRestrictedMsg': {'en': 'Access restricted: This mobile app is exclusively for farmers.', 'hi': 'पहुंच प्रतिबंधित: यह ऐप केवल किसानों के लिए है।', 'gu': 'પ્રવેશ પ્રતિબંધિત: આ એપ ફક્ત ખેડૂતો માટે છે.'},
    'emptyCredentialsMsg': {'en': 'Please enter both your identifier and password.', 'hi': 'कृपया अपना पहचानकर्ता और पासवर्ड दोनों दर्ज करें।', 'gu': 'કૃપા કરીને ઓળખકર્તા અને પાસવર્ડ બંને દાખલ કરો.'},

    // ── Navigation Tabs ─────────────────────────────────────────────────────
    'navToday': {'en': 'Today', 'hi': 'आज', 'gu': 'આજે'},
    'navHistory': {'en': 'History', 'hi': 'इतिहास', 'gu': 'ઇતિહાસ'},
    'navWeather': {'en': 'Weather', 'hi': 'मौसम', 'gu': 'હવામાન'},
    'navFarm': {'en': 'My Farm', 'hi': 'मेरा खेत', 'gu': 'મારું ખેતર'},
    'navAlerts': {'en': 'Alerts', 'hi': 'सूचनाएं', 'gu': 'સૂચનાઓ'},
    'navScan': {'en': 'Scan Leaf', 'hi': 'पत्ती स्कैन करें', 'gu': 'પાન સ્કેન કરો'},

    // ── Today Screen ────────────────────────────────────────────────────────
    'welcomeBack': {'en': 'Welcome,', 'hi': 'नमस्ते,', 'gu': 'નમસ્તે,'},
    'farmerBadge': {'en': 'Farmer', 'hi': 'किसान', 'gu': 'ખેડૂત'},
    'startScanCtaTitle': {'en': 'Inspect Crop Health', 'hi': 'फसल स्वास्थ्य की जांच करें', 'gu': 'પાકના સ્વાસ્થ્યની તપાસ કરો'},
    'startScanCtaSubtitle': {'en': 'Snap a clear leaf photo for instant AI diagnosis and advisory', 'hi': 'तुरंत AI रोग निदान और सलाह के लिए पत्ती का फोटो लें', 'gu': 'તાત્કાલિક AI રોગ નિદાન અને સલાહ માટે પાનનો ફોટો લો'},
    'startScanBtn': {'en': 'Start Diagnostic Scan', 'hi': 'निदान स्कैन शुरू करें', 'gu': 'નિદાન સ્કેન શરૂ કરો'},
    'recentDiagnoses': {'en': 'Recent Diagnoses', 'hi': 'हाल के निदान', 'gu': 'તાજેતરના નિદાન'},
    'viewAll': {'en': 'View All', 'hi': 'सभी देखें', 'gu': 'બધા જુઓ'},
    'noRecentScans': {'en': 'No scans recorded yet. Tap below to diagnose your first leaf.', 'hi': 'अभी कोई स्कैन नहीं है। अपनी पहली पत्ती की जांच के लिए नीचे टैप करें।', 'gu': 'હજુ સુધી કોઈ સ્કેન નોંધાયેલ નથી. પ્રથમ પાન તપાસવા નીચે ટેપ કરો.'},
    'quickWeather': {'en': 'Live Farm Weather', 'hi': 'खेत का मौसम', 'gu': 'ખેતરનું હવામાન'},
    'activeAlertsCount': {'en': 'Active Advisories', 'hi': 'सक्रिय सूचनाएं', 'gu': 'સક્રિય સૂચનાઓ'},
    'syncingBadge': {'en': 'Syncing offline scans...', 'hi': 'ऑफ़लाइन स्कैन सिंक हो रहे हैं...', 'gu': 'ઓફલાઇન સ્કેન સિંક થઈ રહ્યા છે...'},

    // ── History Screen ──────────────────────────────────────────────────────
    'scanHistoryTitle': {'en': 'Diagnosis History', 'hi': 'निदान इतिहास', 'gu': 'નિદાન ઇતિહાસ'},
    'searchScans': {'en': 'Search by crop or disease...', 'hi': 'फसल या रोग से खोजें...', 'gu': 'પાક અથવા રોગથી શોધો...'},
    'allCrops': {'en': 'All Crops', 'hi': 'सभी फसलें', 'gu': 'બધા પાક'},
    'emptyHistory': {'en': 'No matching scan records found.', 'hi': 'कोई स्कैन रिकॉर्ड नहीं मिला।', 'gu': 'કોઈ મેળ ખાતા સ્કેન રેકોર્ડ મળ્યા નથી.'},
    'offlineQueued': {'en': 'Queued Offline', 'hi': 'ऑफ़लाइन कतारबद्ध', 'gu': 'ઓફલાઇન કતારબદ્ધ'},
    'completedStatus': {'en': 'Diagnosed', 'hi': 'निदान पूर्ण', 'gu': 'નિદાન પૂર્ણ'},
    'pendingStatus': {'en': 'Processing', 'hi': 'प्रक्रिया में', 'gu': 'પ્રક્રિયામાં'},
    'aiConfidence': {'en': 'AI Confidence', 'hi': 'AI सटीकता', 'gu': 'AI ચોકસાઈ'},
    'severity': {'en': 'Severity', 'hi': 'तीव्रता', 'gu': 'તીવ્રતા'},

    // ── Weather Screen ──────────────────────────────────────────────────────
    'weatherTitle': {'en': 'Weather & Spray Advisory', 'hi': 'मौसम और छिड़काव सलाह', 'gu': 'હવામાન અને છંટકાવ સલાહ'},
    'currentWeather': {'en': 'Current Conditions', 'hi': 'वर्तमान स्थिति', 'gu': 'વર્તમાન પરિસ્થિતિ'},
    'temperature': {'en': 'Temperature', 'hi': 'तापमान', 'gu': 'તાપમાન'},
    'humidity': {'en': 'Humidity', 'hi': 'आर्द्रता (नमी)', 'gu': 'ભેજનું પ્રમાણ'},
    'windSpeed': {'en': 'Wind Speed', 'hi': 'हवा की गति', 'gu': 'પવનની ઝડપ'},
    'sprayConditions': {'en': 'Spraying Advice', 'hi': 'छिड़काव की उपयुक्तता', 'gu': 'છંટકાવ અનુકૂળતા'},
    'favorableSpray': {'en': 'Good conditions for pesticide/fertilizer application', 'hi': 'दवा छिड़काव के लिए मौसम अनुकूल है', 'gu': 'દવા છંટકાવ માટે હવામાન અનુકૂળ છે'},
    'unfavorableSpray': {'en': 'High winds or rain expected; postpone spraying', 'hi': 'तेज हवा या बारिश की संभावना; छिड़काव टालें', 'gu': 'તેજ પવન કે વરસાદની શક્યતા; છંટકાવ મોકૂફ રાખો'},

    // ── Farm Screen ─────────────────────────────────────────────────────────
    'farmTitle': {'en': 'Farm & Plots', 'hi': 'खेत और प्लॉट', 'gu': 'ખેતર અને પ્લોટ'},
    'farmDetails': {'en': 'Farm Overview', 'hi': 'खेत का विवरण', 'gu': 'ખેતરની વિગતો'},
    'plotsTitle': {'en': 'Cultivated Plots', 'hi': 'फसल प्लॉट', 'gu': 'વાવેતર કરેલ પ્લોટ'},
    'totalArea': {'en': 'Total Area', 'hi': 'कुल क्षेत्रफल', 'gu': 'કુલ વિસ્તાર'},
    'acres': {'en': 'acres', 'hi': 'एकड़', 'gu': 'એકર'},
    'soilType': {'en': 'Soil Type', 'hi': 'मिट्टी का प्रकार', 'gu': 'જમીનનો પ્રકાર'},
    'irrigation': {'en': 'Irrigation', 'hi': 'सिंचाई प्रणाली', 'gu': 'પિયત પદ્ધતિ'},
    'noPlotsFound': {'en': 'No plots configured yet.', 'hi': 'अभी कोई प्लॉट नहीं जोड़ा गया है।', 'gu': 'હજુ સુધી કોઈ પ્લોટ ઉમેરાયો નથી.'},

    // ── Alerts Screen ───────────────────────────────────────────────────────
    'alertsTitle': {'en': 'Farm Alerts & Advisories', 'hi': 'खेत अलर्ट और सूचनाएं', 'gu': 'ખેતર એલર્ટ અને સૂચનાઓ'},
    'noAlerts': {'en': 'No active alerts for your farm. All crops healthy!', 'hi': 'आपके खेत के लिए कोई सक्रिय चेतावनी नहीं है। सभी फसलें स्वस्थ हैं!', 'gu': 'તમારા ખેતર માટે કોઈ સક્રિય ચેતવણી નથી. બધા પાક તંદુરસ્ત છે!'},
    'markAllRead': {'en': 'Mark All as Read', 'hi': 'सभी को पढ़ा हुआ चिह्नित करें', 'gu': 'બધા વાંચેલા તરીકે ચિહ્નિત કરો'},
    'alertAction': {'en': 'Action Required', 'hi': 'कार्रवाई आवश्यक', 'gu': 'પગલાં લેવા જરૂરી'},

    // ── Camera Overlay Guidance ─────────────────────────────────────────────
    'cameraGuideTitle': {'en': 'Position Leaf in Frame', 'hi': 'पत्ती को फ्रेम के बीच में रखें', 'gu': 'પાનને ફ્રેમની વચ્ચે રાખો'},
    'centerLeaf': {'en': 'Place infected area inside the box', 'hi': 'रोगग्रस्त भाग को बॉक्स के अंदर रखें', 'gu': 'રોગગ્રસ્ત ભાગને બોક્સની અંદર રાખો'},
    'goodLighting': {'en': 'Ensure bright, natural daylight', 'hi': 'पर्याप्त प्राकृतिक रोशनी सुनिश्चित करें', 'gu': 'પૂરતો કુદરતી પ્રકાશ હોવાની ખાતરી કરો'},
    'holdSteady': {'en': 'Hold phone steady to avoid blur', 'hi': 'धुंधलापन से बचने के लिए फोन स्थिर रखें', 'gu': 'ઝાંખાપણું ટાળવા માટે ફોન સ્થિર રાખો'},
    'tapToCapture': {'en': 'Tap shutter to capture leaf', 'hi': 'पत्ती का फोटो लेने के लिए बटन दबाएं', 'gu': 'ફોટો લેવા માટે બટન દબાવો'},
    'uploadGallery': {'en': 'Choose from Gallery', 'hi': 'गैलरी से फोटो चुनें', 'gu': 'ગેલેરીમાંથી ફોટો પસંદ કરો'},

    // ── Create Prediction Sheet ─────────────────────────────────────────────
    'newDiagnosisTitle': {'en': 'New Leaf Diagnosis', 'hi': 'नया पत्ती निदान', 'gu': 'નવું પાન નિદાન'},
    'selectPlot': {'en': 'Select Plot', 'hi': 'प्लॉट चुनें', 'gu': 'પ્લોટ પસંદ કરો'},
    'locationField': {'en': 'Farm Location', 'hi': 'खेत का स्थान', 'gu': 'ખેતરનું સ્થળ'},
    'submitScan': {'en': 'Submit for Diagnosis', 'hi': 'निदान के लिए भेजें', 'gu': 'નિદાન માટે મોકલો'},
    'submitting': {'en': 'Analyzing leaf scan...', 'hi': 'पत्ती का विश्लेषण हो रहा है...', 'gu': 'પાનનું વિશ્લેષણ થઈ રહ્યું છે...'},
    'takePhotoBtn': {'en': 'Take Camera Photo', 'hi': 'कैमरे से फोटो लें', 'gu': 'કેમેરાથી ફોટો લો'},
    'chooseGalleryBtn': {'en': 'Upload from Gallery', 'hi': 'गैलरी से अपलोड करें', 'gu': 'ગેલેરીમાંથી અપલોડ કરો'},
    'photoRequiredError': {'en': 'Please take or choose a leaf photo first.', 'hi': 'कृपया पहले पत्ती का फोटो लें या चुनें।', 'gu': 'કૃપા કરીને પહેલા પાનનો ફોટો લો અથવા પસંદ કરો.'},

    // ── Processing Sheet Stages ─────────────────────────────────────────────
    'stagePreprocessing': {'en': 'Validating leaf image quality...', 'hi': 'पत्ती की फोटो गुणवत्ता जांची जा रही है...', 'gu': 'પાનના ફોટાની ગુણવત્તા તપાસાઈ રહી છે...'},
    'stageCrop': {'en': 'Identifying crop species...', 'hi': 'फसल के प्रकार की पहचान हो रही है...', 'gu': 'પાકના પ્રકારની ઓળખ થઈ રહી છે...'},
    'stageDisease': {'en': 'Analyzing leaf disease...', 'hi': 'पत्ती के रोग का विश्लेषण हो रहा है...', 'gu': 'પાનના રોગનું વિશ્લેષણ થઈ રહ્યું છે...'},
    'stageSeverity': {'en': 'Estimating infection severity...', 'hi': 'संक्रमण की गंभीरता का आकलन हो रहा है...', 'gu': 'ચેપની ગંભીરતાનો અંદાજ લગાવાઈ રહ્યો છે...'},
    'stagePest': {'en': 'Scanning for pest presence...', 'hi': 'कीटों की उपस्थिति जांची जा रही है...', 'gu': 'જીવાતોની હાજરી તપાસાઈ રહી છે...'},
    'stageAdvisory': {'en': 'Synthesizing agronomic advisory...', 'hi': 'कृषि विशेषज्ञ सलाह तैयार की जा रही है...', 'gu': 'કૃષિ સલાહ તૈયાર થઈ રહી છે...'},

    // ── Result Detail Sheet ─────────────────────────────────────────────────
    'cropDiagnosis': {'en': 'DIAGNOSIS', 'hi': 'रोग निदान', 'gu': 'રોગ નિદાન'},
    'listenComplete': {'en': 'Listen to complete recommendation', 'hi': 'पूरी सलाह ऑडियो सुनें', 'gu': 'સંપૂર્ણ સલાહ ઓડિયો સાંભળો'},
    'playAudio': {'en': 'Play Complete Advice', 'hi': 'ऑडियो चलाएं', 'gu': 'ઓડિયો ચલાવો'},
    'pauseAudio': {'en': 'Pause Audio', 'hi': 'ऑडियो रोकें', 'gu': 'ઓડિયો થોભાવો'},
    'resumeAudio': {'en': 'Resume Audio', 'hi': 'ऑडियो पुनः चलाएं', 'gu': 'ઓડિયો ફરી ચલાવો'},
    'playingFullAudio': {'en': 'Playing full recommendation...', 'hi': 'पूरी सलाह ऑडियो चल रहा है...', 'gu': 'સંપૂર્ણ ભલામણ ઓડિયો ચાલી રહ્યો છે...'},
    'audioPaused': {'en': 'Audio paused', 'hi': 'ऑडियो रुका हुआ है', 'gu': 'ઓડિયો થોભાયેલ છે'},
    'audioAdviceSubtitle': {'en': 'Immediate action, treatment, prevention & monitoring', 'hi': 'त्वरित कार्रवाई, उपचार, रोकथाम और निगरानी', 'gu': 'ત્વરિત પગલાં, સારવાર, નિવારણ અને દેખરેખ'},
    'immediateAction': {'en': 'Immediate Action:', 'hi': 'त्वरित कार्रवाई:', 'gu': 'ત્વરિત પગલાં:'},
    'treatmentGuidance': {'en': 'Treatment Guidance:', 'hi': 'उपचार निर्देश:', 'gu': 'સારવાર માર્ગદર્શન:'},
    'preventionStrategy': {'en': 'Prevention Strategy:', 'hi': 'रोकथाम रणनीति:', 'gu': 'નિવારણ વ્યૂહરચના:'},
    'monitoringPlan': {'en': 'Monitoring Plan:', 'hi': 'निगरानी योजना:', 'gu': 'દેખરેખ યોજના:'},
    'wasDiagnosisAccurate': {'en': 'Was this diagnosis accurate?', 'hi': 'क्या यह निदान सटीक था?', 'gu': 'શું આ નિદાન સાચું હતું?'},
    'accurateBtn': {'en': 'Accurate', 'hi': 'सटीक है', 'gu': 'સાચું છે'},
    'incorrectBtn': {'en': 'Incorrect', 'hi': 'गलत है', 'gu': 'ખોટું છે'},
    'optionalNoteHint': {'en': 'Optional note for agronomy research...', 'hi': 'कृषि अनुसंधान के लिए टिप्पणी...', 'gu': 'કૃષિ સંશોધન માટે વૈકલ્પિક નોંધ...'},
    'feedbackConfirmed': {'en': 'Thank you for confirming your feedback!', 'hi': 'अपनी प्रतिक्रिया दर्ज करने के लिए धन्यवाद!', 'gu': 'તમારો પ્રતિસાદ નોંધવા બદલ આભાર!'},
    'requestExpertReview': {'en': 'Request Specialist Verification', 'hi': 'विशेषज्ञ से जांच का अनुरोध करें', 'gu': 'નિષ્ણાત તપાસ માટે વિનંતી કરો'},
    'expertRequested': {'en': 'Specialist review requested', 'hi': 'विशेषज्ञ समीक्षा का अनुरोध भेजा गया', 'gu': 'નિષ્ણાત સમીક્ષા વિનંતી મોકલાઈ'},
    'translatingAdvisory': {'en': 'Translating advisory into your language...', 'hi': 'सलाह का अनुवाद हो रहा है...', 'gu': 'ભલામણનું ભાષાંતર થઈ રહ્યું છે...'},
  };

  static String get(String key, String lang) {
    final code = DomainTranslations.normalizeLang(lang);
    final entry = _strings[key];
    if (entry != null && entry[code] != null) {
      return entry[code]!;
    }
    return entry?['en'] ?? key;
  }
}
