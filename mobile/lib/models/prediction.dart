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
    this.pending = false,
    this.immediateAction,
    this.treatment,
    this.prevention,
    this.monitoring,
    this.status = 'completed',
    this.qualityScore,
    this.pests = const [],
    this.createdAt,
    this.notes = const [],
    this.translations,
  });

  final int id;
  final String crop;
  final String disease;
  final double confidence;
  final int severity;
  final String recommendation;
  final String? imagePath;
  final String? rawPath;
  final bool pending;
  final String? immediateAction;
  final String? treatment;
  final String? prevention;
  final String? monitoring;
  final String status;
  final double? qualityScore;
  final List<String> pests;
  final String? createdAt;
  final List<String> notes;
  final Map<String, dynamic>? translations;

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
    return Prediction(
      id: id,
      crop: crop,
      disease: disease,
      confidence: confidence,
      severity: severity,
      recommendation: recommendation,
      imagePath: imagePath,
      rawPath: rawPath,
      pending: pending,
      immediateAction: immediateAction,
      treatment: treatment,
      prevention: prevention,
      monitoring: monitoring,
      status: status,
      qualityScore: qualityScore,
      pests: pests,
      createdAt: createdAt,
      notes: notes,
      translations: merged,
    );
  }

  factory Prediction.fromJson(Map<String, dynamic> json) {
    final crop = (json['crop'] as Map?)?.cast<String, dynamic>() ?? {};
    final disease = (json['disease'] as Map?)?.cast<String, dynamic>() ?? {};
    final severity = (json['severity'] as Map?)?.cast<String, dynamic>() ?? {};
    final recommendation = (json['recommendation'] as Map?)?.cast<String, dynamic>() ?? {};
    final image = (json['image'] as Map?)?.cast<String, dynamic>() ?? {};
    final rawTranslations = (json['translations'] as Map?)?.cast<String, dynamic>() ??
        (json['result'] is Map ? (json['result']['translations'] as Map?)?.cast<String, dynamic>() : null);
    final pestsList = (json['pests'] as List?)
            ?.map((p) => (p as Map)['label']?.toString() ?? '')
            .where((label) => label.isNotEmpty)
            .toList() ??
        [];

    final immediate = recommendation['immediate_action']?.toString();
    final treat = recommendation['treatment']?.toString();
    final prev = recommendation['prevention']?.toString();
    final monitor = recommendation['monitoring']?.toString();

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

    final recText = sections.isNotEmpty
        ? sections.join('\n\n')
        : (recommendation['summary']?.toString() ?? 'Follow local agricultural guidance.');

    final rawStatus = json['status'];
    String statusStr = 'completed';
    if (rawStatus is String) {
      statusStr = rawStatus;
    } else if (rawStatus is Map) {
      statusStr = rawStatus['pipeline']?.toString() ?? 'completed';
    }

    return Prediction(
      id: (json['prediction_id'] as num?)?.toInt() ?? (json['id'] as num?)?.toInt() ?? 0,
      crop: crop['label']?.toString() ?? 'Unknown crop',
      disease: disease['label']?.toString() ?? 'Unknown condition',
      confidence: (disease['confidence'] as num?)?.toDouble() ?? 0,
      severity: (severity['percent'] as num?)?.round() ?? 0,
      recommendation: recText,
      immediateAction: immediate,
      treatment: treat,
      prevention: prev,
      monitoring: monitor,
      imagePath: image['processed_path']?.toString() ?? image['raw_path']?.toString(),
      rawPath: image['raw_path']?.toString(),
      qualityScore: (image['quality_score'] as num?)?.toDouble(),
      pests: pestsList,
      status: statusStr,
      createdAt: json['created_at']?.toString(),
      notes: (json['notes'] as List?)?.map((n) => n.toString()).toList() ?? [],
      translations: rawTranslations,
    );
  }
}
