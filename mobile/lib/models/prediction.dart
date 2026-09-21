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

  factory Prediction.fromJson(Map<String, dynamic> json) {
    final crop = (json['crop'] as Map?)?.cast<String, dynamic>() ?? {};
    final disease = (json['disease'] as Map?)?.cast<String, dynamic>() ?? {};
    final severity = (json['severity'] as Map?)?.cast<String, dynamic>() ?? {};
    final recommendation = (json['recommendation'] as Map?)?.cast<String, dynamic>() ?? {};
    final image = (json['image'] as Map?)?.cast<String, dynamic>() ?? {};
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
    );
  }
}
