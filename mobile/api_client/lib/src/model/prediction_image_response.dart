//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'prediction_image_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PredictionImageResponse {
  /// Returns a new [PredictionImageResponse] instance.
  PredictionImageResponse({
    this.rawPath,

    this.processedPath,

    this.rawUrl,

    this.processedUrl,

    this.qualityScore,

    this.leafDetected,
  });

  @JsonKey(name: r'raw_path', required: false, includeIfNull: false)
  final String? rawPath;

  @JsonKey(name: r'processed_path', required: false, includeIfNull: false)
  final String? processedPath;

  @JsonKey(name: r'raw_url', required: false, includeIfNull: false)
  final String? rawUrl;

  @JsonKey(name: r'processed_url', required: false, includeIfNull: false)
  final String? processedUrl;

  @JsonKey(name: r'quality_score', required: false, includeIfNull: false)
  final num? qualityScore;

  @JsonKey(name: r'leaf_detected', required: false, includeIfNull: false)
  final bool? leafDetected;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PredictionImageResponse &&
          other.rawPath == rawPath &&
          other.processedPath == processedPath &&
          other.rawUrl == rawUrl &&
          other.processedUrl == processedUrl &&
          other.qualityScore == qualityScore &&
          other.leafDetected == leafDetected;

  @override
  int get hashCode =>
      (rawPath == null ? 0 : rawPath.hashCode) +
      (processedPath == null ? 0 : processedPath.hashCode) +
      (rawUrl == null ? 0 : rawUrl.hashCode) +
      (processedUrl == null ? 0 : processedUrl.hashCode) +
      (qualityScore == null ? 0 : qualityScore.hashCode) +
      (leafDetected == null ? 0 : leafDetected.hashCode);

  factory PredictionImageResponse.fromJson(Map<String, dynamic> json) =>
      _$PredictionImageResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PredictionImageResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
