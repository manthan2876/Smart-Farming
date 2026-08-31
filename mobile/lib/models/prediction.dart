class Prediction {
  const Prediction({
    required this.id,
    required this.crop,
    required this.disease,
    required this.confidence,
    required this.severity,
    required this.recommendation,
    this.imagePath,
    this.pending = false,
  });

  final int id;
  final String crop;
  final String disease;
  final double confidence;
  final int severity;
  final String recommendation;
  final String? imagePath;
  final bool pending;

  factory Prediction.fromJson(Map<String, dynamic> json) {
    final crop = (json['crop'] as Map?)?.cast<String, dynamic>() ?? {};
    final disease = (json['disease'] as Map?)?.cast<String, dynamic>() ?? {};
    final severity = (json['severity'] as Map?)?.cast<String, dynamic>() ?? {};
    String recText = 'Follow local agricultural guidance.';
    if (recommendation['pesticide'] != null && recommendation['pesticide'] != 'N/A') {
      recText = recommendation['pesticide'].toString();
    } else if (recommendation['fertilizer'] != null && recommendation['fertilizer'] != 'N/A') {
      recText = recommendation['fertilizer'].toString();
    } else if (recommendation['prevention_tips'] != null) {
      recText = recommendation['prevention_tips'].toString();
    }

    return Prediction(
      id: (json['prediction_id'] as num?)?.toInt() ?? 0,
      crop: crop['label']?.toString() ?? 'Unknown crop',
      disease: disease['label']?.toString() ?? 'Unknown condition',
      confidence: (disease['confidence'] as num?)?.toDouble() ?? 0,
      severity: (severity['percent'] as num?)?.round() ?? 0,
      recommendation: recText,
      imagePath: (json['image'] as Map?)?['raw_path']?.toString(),
    );
  }
}
