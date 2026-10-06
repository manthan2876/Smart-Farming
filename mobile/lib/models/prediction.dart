import '../i18n/domain_translations.dart';

class Prediction {
  const Prediction({
    required this.id,
    required this.crop,
    required this.disease,
    required this.confidence,
    required this.severity,
    required this.recommendation,
    this.imagePath,
    this.rawPath,
    this.rawUrl,
    this.processedUrl,
    this.severityBucket,
    this.pending = false,
    this.immediateAction,
    this.treatment,
    this.prevention,
    this.monitoring,
    this.status = 'completed',
    this.qualityScore,
    this.pests = const [],
    this.pestClassificationStatus,
    this.isPestAvailable = true,
    this.createdAt,
    this.notes = const [],
    this.translations,
    this.expertDecision,
    this.expertGuidance,
    this.correctedDisease,
    this.expertReviewStatus,
    this.isFallback = false,
    this.isMasked = false,
    this.isUncertain = false,
    this.modelUsed,
    this.durationMs,
    this.schemaVersion,
    this.weatherTemp,
    this.weatherHumidity,
    this.weatherCondition,
    this.historicalImages = const [],
    this.treatmentProgress,
    this.plotInfo,
    this.farmInfo,
  });

  final int id;
  final String crop;
  final String disease;
  final double confidence;
  final int severity;
  final String recommendation;
  final String? imagePath;
  final String? rawPath;
  final String? rawUrl;
  final String? processedUrl;
  final String? severityBucket;
  final bool pending;
  final String? immediateAction;
  final String? treatment;
  final String? prevention;
  final String? monitoring;
  final String status;
  final double? qualityScore;
  final List<String> pests;
  final String? pestClassificationStatus;
  final bool isPestAvailable;
  final String? createdAt;
  final List<String> notes;
  final Map<String, dynamic>? translations;
  final String? expertDecision;
  final String? expertGuidance;
  final String? correctedDisease;
  final String? expertReviewStatus;
  final bool isFallback;
  final bool isMasked;
  final bool isUncertain;
  final String? modelUsed;
  final int? durationMs;
  final String? schemaVersion;
  final double? weatherTemp;
  final int? weatherHumidity;
  final String? weatherCondition;
  final List<Map<String, dynamic>> historicalImages;
  final Map<String, dynamic>? treatmentProgress;
  final Map<String, dynamic>? plotInfo;
  final Map<String, dynamic>? farmInfo;

  bool get isPestUnavailable =>
      !isPestAvailable ||
      pestClassificationStatus == 'unavailable' ||
      pestClassificationStatus == 'skipped';

  bool get isUnsupportedCrop =>
      crop.toLowerCase().contains('unsupported') ||
      disease.toLowerCase().contains('unsupported') ||
      status == 'unsupported_crop';

  bool get isVerified => expertReviewStatus == 'verified' || status == 'verified';

  String? get processedPath => imagePath;

  /// Returns the complete comprehensive spoken recommendation combining all actionable paragraphs.
  String get fullAudioRecommendation {
    final buffer = StringBuffer();
    buffer.write('Diagnosis for $crop. Detected condition: $disease. ');
    buffer.write('Severity is $severity percent, with ${(confidence * 100).round()} percent confidence. ');

    if (immediateAction != null && immediateAction!.trim().isNotEmpty) {
      buffer.write('Immediate Action: ${immediateAction!.trim()} ');
    }
    if (treatment != null && treatment!.trim().isNotEmpty) {
      buffer.write('Treatment Guidance: ${treatment!.trim()} ');
    }
    if (prevention != null && prevention!.trim().isNotEmpty) {
      buffer.write('Prevention Strategy: ${prevention!.trim()} ');
    }
    if (monitoring != null && monitoring!.trim().isNotEmpty) {
      buffer.write('Monitoring Plan: ${monitoring!.trim()} ');
    }
    if (immediateAction == null && treatment == null && prevention == null && recommendation.isNotEmpty) {
      buffer.write(recommendation);
    }
    return buffer.toString().trim();
  }

  Map<String, dynamic>? _getLangMap(String languageCode) {
    if (translations == null) return null;
    final norm = DomainTranslations.normalizeLang(languageCode);
    final entry = translations![languageCode] ??
        translations![norm] ??
        (norm == 'hi' ? (translations!['Hindi'] ?? translations!['hi_IN']) : null) ??
        (norm == 'gu' ? (translations!['Gujarati'] ?? translations!['gu_IN']) : null);
    if (entry is Map) return entry.cast<String, dynamic>();
    if (entry is String && entry.trim().isNotEmpty) return {'summary': entry.trim()};
    return null;
  }

  /// Returns localized recommendation text for the given language code ('en', 'hi', 'gu').
  String localizedRecommendation(String languageCode) {
    if (languageCode == 'en') return recommendation;
    final t = _getLangMap(languageCode);
    if (t != null) {
      final sections = <String>[];
      final imm = t['immediate_action']?.toString();
      final treat = t['treatment']?.toString();
      final prev = t['prevention']?.toString();
      final mon = t['monitoring']?.toString();
      if (imm != null && imm.trim().isNotEmpty) sections.add(imm.trim());
      if (treat != null && treat.trim().isNotEmpty) sections.add(treat.trim());
      if (prev != null && prev.trim().isNotEmpty) sections.add(prev.trim());
      if (mon != null && mon.trim().isNotEmpty) sections.add(mon.trim());
      if (sections.isNotEmpty) return sections.join('\n\n');
      final summary = t['summary']?.toString();
      if (summary != null && summary.trim().isNotEmpty) return summary.trim();
    }
    return recommendation;
  }

  /// Returns localized immediate action for the given language code.
  String? localizedImmediateAction(String languageCode) {
    if (languageCode == 'en') return immediateAction;
    final t = _getLangMap(languageCode);
    if (t != null) {
      final val = t['immediate_action']?.toString();
      if (val != null && val.trim().isNotEmpty) return val.trim();
      return null;
    }
    return immediateAction;
  }

  /// Returns localized treatment for the given language code.
  String? localizedTreatment(String languageCode) {
    if (languageCode == 'en') return treatment;
    final t = _getLangMap(languageCode);
    if (t != null) {
      final val = t['treatment']?.toString();
      if (val != null && val.trim().isNotEmpty) return val.trim();
      return null;
    }
    return treatment;
  }

  /// Returns localized prevention for the given language code.
  String? localizedPrevention(String languageCode) {
    if (languageCode == 'en') return prevention;
    final t = _getLangMap(languageCode);
    if (t != null) {
      final val = t['prevention']?.toString();
      if (val != null && val.trim().isNotEmpty) return val.trim();
      return null;
    }
    return prevention;
  }

  /// Returns localized monitoring for the given language code.
  String? localizedMonitoring(String languageCode) {
    if (languageCode == 'en') return monitoring;
    final t = _getLangMap(languageCode);
    if (t != null) {
      final val = t['monitoring']?.toString();
      if (val != null && val.trim().isNotEmpty) return val.trim();
      return null;
    }
    return monitoring;
  }

  /// Returns localized full audio text for TTS for the given language code.
  String localizedAudioText(String languageCode, {String? localizedCropName, String? localizedDiseaseName}) {
    final cName = localizedCropName ?? crop;
    final dName = localizedDiseaseName ?? disease;
    final imm = localizedImmediateAction(languageCode);
    final treat = localizedTreatment(languageCode);
    final prev = localizedPrevention(languageCode);
    final mon = localizedMonitoring(languageCode);

    final norm = DomainTranslations.normalizeLang(languageCode);
    final buffer = StringBuffer();
    if (norm == 'hi') {
      buffer.write('$cName की जांच रिपोर्ट। स्थिति: $dName। ');
      buffer.write('गंभीरता $severity प्रतिशत है। ');
      if (imm != null && imm.isNotEmpty) buffer.write('त्वरित कार्रवाई: $imm. ');
      if (treat != null && treat.isNotEmpty) buffer.write('उपचार सलाह: $treat. ');
      if (prev != null && prev.isNotEmpty) buffer.write('बचाव रणनीति: $prev. ');
      if (mon != null && mon.isNotEmpty) buffer.write('निगरानी योजना: $mon. ');
    } else if (norm == 'gu') {
      buffer.write('$cName નો તપાસ અહેવાલ. સ્થિતિ: $dName. ');
      buffer.write('તીવ્રતા $severity ટકા છે. ');
      if (imm != null && imm.isNotEmpty) buffer.write('તાત્કાલિક પગલાં: $imm. ');
      if (treat != null && treat.isNotEmpty) buffer.write('સારવાર માર્ગદર્શન: $treat. ');
      if (prev != null && prev.isNotEmpty) buffer.write('નિવારણ વ્યૂહરચના: $prev. ');
      if (mon != null && mon.isNotEmpty) buffer.write('દેખરેખ યોજના: $mon. ');
    } else {
      buffer.write('Diagnosis for $cName. Detected condition: $dName. ');
      buffer.write('Severity is $severity percent, with ${(confidence * 100).round()} percent confidence. ');
      if (imm != null && imm.isNotEmpty) buffer.write('Immediate Action: $imm. ');
      if (treat != null && treat.isNotEmpty) buffer.write('Treatment Guidance: $treat. ');
      if (prev != null && prev.isNotEmpty) buffer.write('Prevention Strategy: $prev. ');
      if (mon != null && mon.isNotEmpty) buffer.write('Monitoring Plan: $mon. ');
    }

    if (imm == null && treat == null && prev == null) {
      buffer.write(localizedRecommendation(languageCode));
    }
    return buffer.toString().trim();
  }

  /// Returns a copy of Prediction with updated translations
  Prediction copyWithTranslations(Map<String, dynamic> newTranslations) {
    final merged = Map<String, dynamic>.from(translations ?? {});
    newTranslations.forEach((key, value) {
      if (value is Map && merged[key] is Map) {
        merged[key] = Map<String, dynamic>.from(merged[key] as Map)..addAll(value.cast<String, dynamic>());
      } else {
        merged[key] = value;
      }
    });
    return copyWith(translations: merged);
  }

  /// Flexible copyWith helper
  Prediction copyWith({
    int? id,
    String? crop,
    String? disease,
    double? confidence,
    int? severity,
    String? recommendation,
    String? imagePath,
    String? rawPath,
    String? rawUrl,
    String? processedUrl,
    String? severityBucket,
    bool? pending,
    String? immediateAction,
    String? treatment,
    String? prevention,
    String? monitoring,
    String? status,
    double? qualityScore,
    List<String>? pests,
    String? pestClassificationStatus,
    bool? isPestAvailable,
    String? createdAt,
    List<String>? notes,
    Map<String, dynamic>? translations,
    String? expertDecision,
    String? expertGuidance,
    String? correctedDisease,
    String? expertReviewStatus,
    bool? isFallback,
    bool? isMasked,
    bool? isUncertain,
    String? modelUsed,
    int? durationMs,
    String? schemaVersion,
    double? weatherTemp,
    int? weatherHumidity,
    String? weatherCondition,
    List<Map<String, dynamic>>? historicalImages,
    Map<String, dynamic>? treatmentProgress,
    Map<String, dynamic>? plotInfo,
    Map<String, dynamic>? farmInfo,
  }) {
    return Prediction(
      id: id ?? this.id,
      crop: crop ?? this.crop,
      disease: disease ?? this.disease,
      confidence: confidence ?? this.confidence,
      severity: severity ?? this.severity,
      recommendation: recommendation ?? this.recommendation,
      imagePath: imagePath ?? this.imagePath,
      rawPath: rawPath ?? this.rawPath,
      rawUrl: rawUrl ?? this.rawUrl,
      processedUrl: processedUrl ?? this.processedUrl,
      severityBucket: severityBucket ?? this.severityBucket,
      pending: pending ?? this.pending,
      immediateAction: immediateAction ?? this.immediateAction,
      treatment: treatment ?? this.treatment,
      prevention: prevention ?? this.prevention,
      monitoring: monitoring ?? this.monitoring,
      status: status ?? this.status,
      qualityScore: qualityScore ?? this.qualityScore,
      pests: pests ?? this.pests,
      pestClassificationStatus: pestClassificationStatus ?? this.pestClassificationStatus,
      isPestAvailable: isPestAvailable ?? this.isPestAvailable,
      createdAt: createdAt ?? this.createdAt,
      notes: notes ?? this.notes,
      translations: translations ?? this.translations,
      expertDecision: expertDecision ?? this.expertDecision,
      expertGuidance: expertGuidance ?? this.expertGuidance,
      correctedDisease: correctedDisease ?? this.correctedDisease,
      expertReviewStatus: expertReviewStatus ?? this.expertReviewStatus,
      isFallback: isFallback ?? this.isFallback,
      isMasked: isMasked ?? this.isMasked,
      isUncertain: isUncertain ?? this.isUncertain,
      modelUsed: modelUsed ?? this.modelUsed,
      durationMs: durationMs ?? this.durationMs,
      schemaVersion: schemaVersion ?? this.schemaVersion,
      weatherTemp: weatherTemp ?? this.weatherTemp,
      weatherHumidity: weatherHumidity ?? this.weatherHumidity,
      weatherCondition: weatherCondition ?? this.weatherCondition,
      historicalImages: historicalImages ?? this.historicalImages,
      treatmentProgress: treatmentProgress ?? this.treatmentProgress,
      plotInfo: plotInfo ?? this.plotInfo,
      farmInfo: farmInfo ?? this.farmInfo,
    );
  }

  factory Prediction.fromJson(Map<String, dynamic> json) {
    // Unfold follow_up if present
    final target = json['follow_up'] is Map ? (json['follow_up'] as Map).cast<String, dynamic>() : json;

    // 1. Robust crop parsing (handles Map, String, or null)
    final cropRaw = target['crop'];
    Map<String, dynamic> crop = {};
    String cropLabel = 'Unknown crop';
    double cropConfidence = 0.0;
    if (cropRaw is Map) {
      crop = cropRaw.cast<String, dynamic>();
      cropLabel = crop['label']?.toString() ?? 'Unknown crop';
      cropConfidence = (crop['confidence'] as num?)?.toDouble() ?? 0.0;
    } else if (cropRaw is String && cropRaw.isNotEmpty) {
      cropLabel = cropRaw;
      crop = {'label': cropRaw};
    }
    if (cropConfidence == 0.0 && target['crop_conf'] is num) {
      cropConfidence = (target['crop_conf'] as num).toDouble();
    }

    // 2. Robust disease parsing (handles Map, String, or null)
    final diseaseRaw = target['disease'];
    Map<String, dynamic> disease = {};
    String diseaseLabel = 'Unknown condition';
    double diseaseConfidence = 0.0;
    if (diseaseRaw is Map) {
      disease = diseaseRaw.cast<String, dynamic>();
      diseaseLabel = disease['label']?.toString() ?? 'Unknown condition';
      diseaseConfidence = (disease['confidence'] as num?)?.toDouble() ?? 0.0;
    } else if (diseaseRaw is String && diseaseRaw.isNotEmpty) {
      diseaseLabel = diseaseRaw;
      disease = {'label': diseaseRaw};
    }
    if (diseaseConfidence == 0.0 && target['disease_conf'] is num) {
      diseaseConfidence = (target['disease_conf'] as num).toDouble();
    }

    // 3. Robust severity parsing (handles Map, num, or string)
    final sevRaw = target['severity'];
    int severityPercent = 0;
    String? severityBucket;
    if (sevRaw is Map) {
      severityPercent = (sevRaw['percent'] as num?)?.round() ?? 0;
      severityBucket = sevRaw['bucket']?.toString();
    } else if (sevRaw is num) {
      severityPercent = sevRaw.round();
    } else if (target['severity_pct'] is num) {
      severityPercent = (target['severity_pct'] as num).round();
    }
    if (severityBucket == null && target['severity_bucket'] != null) {
      severityBucket = target['severity_bucket']?.toString();
    }

    // 4. Robust recommendation parsing (handles Map, String, or null)
    final recRaw = target['recommendation'];
    Map<String, dynamic> recommendation = {};
    String? immediate;
    String? treat;
    String? prev;
    String? monitor;
    String recText = '';

    if (recRaw is Map) {
      recommendation = recRaw.cast<String, dynamic>();
      immediate = recommendation['immediate_action']?.toString();
      treat = recommendation['treatment']?.toString();
      prev = recommendation['prevention']?.toString();
      monitor = recommendation['monitoring']?.toString();

      final sections = <String>[];
      if (immediate != null && immediate.trim().isNotEmpty) {
        sections.add('Immediate Action: ${immediate.trim()}');
      }
      if (treat != null && treat.trim().isNotEmpty) {
        sections.add('Treatment: ${treat.trim()}');
      }
      if (prev != null && prev.trim().isNotEmpty) {
        sections.add('Prevention: ${prev.trim()}');
      }
      if (monitor != null && monitor.trim().isNotEmpty) {
        sections.add('Monitoring: ${monitor.trim()}');
      }
      if (recommendation['pesticide'] != null &&
          recommendation['pesticide'].toString().trim().isNotEmpty &&
          recommendation['pesticide'] != 'N/A') {
        sections.add('Pesticide: ${recommendation['pesticide']}');
      }
      recText = sections.isNotEmpty
          ? sections.join('\n\n')
          : (recommendation['summary']?.toString() ?? 'Follow local agricultural guidance.');
    } else if (recRaw is String && recRaw.isNotEmpty) {
      recText = recRaw;
    } else {
      recText = target['error']?.toString() ?? 'Follow local agricultural guidance.';
    }

    // 5. Robust image parsing
    final imgRaw = target['image'];
    Map<String, dynamic> image = {};
    if (imgRaw is Map) {
      image = imgRaw.cast<String, dynamic>();
    }
    final rawPath = image['raw_path']?.toString() ?? target['raw_path']?.toString();
    final processedPath = image['processed_path']?.toString() ?? target['processed_path']?.toString();
    final rawUrl = image['raw_url']?.toString() ?? target['raw_url']?.toString();
    final processedUrl = image['processed_url']?.toString() ?? target['processed_url']?.toString();

    // 6. Robust pests parsing
    final pestsList = (target['pests'] as List?)
            ?.map((p) => p is Map ? (p['label']?.toString() ?? '') : p?.toString() ?? '')
            .where((label) => label.isNotEmpty)
            .toList() ??
        [];
    final pestClassRaw = target['pest_classification'] as Map?;
    final pestClassStatus = pestClassRaw?['status']?.toString() ??
        (target['status'] is Map ? (target['status'] as Map)['pest_detection']?.toString() : null);
    final isPestAvailable = pestClassRaw != null
        ? (pestClassRaw['available'] == true && pestClassStatus != 'unavailable')
        : (pestClassStatus != 'unavailable' && pestClassStatus != 'skipped');

    // 7. Robust status parsing
    final rawStatus = target['status'];
    String statusStr = 'completed';
    String? expertReviewStatus;
    bool isMasked = false;
    if (rawStatus is String) {
      statusStr = rawStatus;
    } else if (rawStatus is Map) {
      statusStr = rawStatus['pipeline']?.toString() ?? 'completed';
      expertReviewStatus = rawStatus['expert_review']?.toString();
      isMasked = rawStatus['mask_advisory'] == true ||
          (expertReviewStatus == 'pending' && (immediate == null || immediate.isEmpty));
    }

    final isFallback = (recRaw is Map && recRaw['is_fallback'] == true) || target['is_fallback'] == true;
    final isUncertain = (diseaseRaw is Map && diseaseRaw['is_uncertain'] == true) ||
        (diseaseConfidence > 0 && diseaseConfidence < 0.60);

    // 8. Expert review data
    final expRaw = target['expert_review_data'] as Map?;
    final expertDecision = expRaw?['decision']?.toString();
    final expertGuidance = expRaw?['farmer_guidance']?.toString();
    final correctedDisease = expRaw?['corrected_disease']?.toString();

    // 9. Weather snapshot
    final weatherMap = target['weather'] as Map?;
    final weatherTemp = (weatherMap?['temperature_celsius'] as num?)?.toDouble();
    final weatherHumidity = (weatherMap?['humidity_percent'] as num?)?.round();
    final weatherCondition = weatherMap?['condition']?.toString();

    // 10. Provenance & model
    final provenance = target['provenance'] as Map?;
    final modelsMap = provenance?['models'] as Map?;
    final diseaseModelMap = modelsMap?['disease'] as Map?;
    final modelUsed = (diseaseRaw is Map ? diseaseRaw['model_used']?.toString() : null) ??
        diseaseModelMap?['name']?.toString();
    final durationMs = (target['total_duration_ms'] as num?)?.round();
    final schemaVersion = target['schema_version']?.toString();

    // 11. Historical images timeline
    final histRaw = target['historical_images'] as List?;
    final historicalImages = histRaw?.map((e) => e is Map ? e.cast<String, dynamic>() : <String, dynamic>{}).toList() ?? [];

    final rawTranslations = (target['translations'] as Map?)?.cast<String, dynamic>() ??
        (target['result'] is Map ? (target['result']['translations'] as Map?)?.cast<String, dynamic>() : null);

    final treatmentProgress = (target['treatment_progress'] as Map?)?.cast<String, dynamic>();
    final plotInfo = (target['plot'] as Map?)?.cast<String, dynamic>();
    final farmInfo = (target['farm'] as Map?)?.cast<String, dynamic>();

    return Prediction(
      id: (target['prediction_id'] as num?)?.toInt() ?? (target['id'] as num?)?.toInt() ?? 0,
      crop: cropLabel,
      disease: diseaseLabel,
      confidence: diseaseConfidence > 0 ? diseaseConfidence : cropConfidence,
      severity: severityPercent,
      severityBucket: severityBucket,
      recommendation: recText,
      immediateAction: immediate,
      treatment: treat,
      prevention: prev,
      monitoring: monitor,
      imagePath: processedPath ?? rawPath,
      rawPath: rawPath,
      rawUrl: rawUrl,
      processedUrl: processedUrl,
      qualityScore: (image['quality_score'] as num?)?.toDouble(),
      pests: pestsList,
      pestClassificationStatus: pestClassStatus,
      isPestAvailable: isPestAvailable,
      status: statusStr,
      expertReviewStatus: expertReviewStatus,
      isFallback: isFallback,
      isMasked: isMasked,
      isUncertain: isUncertain,
      expertDecision: expertDecision,
      expertGuidance: expertGuidance,
      correctedDisease: correctedDisease,
      modelUsed: modelUsed,
      durationMs: durationMs,
      schemaVersion: schemaVersion,
      weatherTemp: weatherTemp,
      weatherHumidity: weatherHumidity,
      weatherCondition: weatherCondition,
      historicalImages: historicalImages,
      treatmentProgress: treatmentProgress,
      plotInfo: plotInfo,
      farmInfo: farmInfo,
      createdAt: target['created_at']?.toString(),
      notes: (target['notes'] as List?)?.map((n) => n.toString()).toList() ?? [],
      translations: rawTranslations,
    );
  }
}
