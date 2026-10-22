//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'prediction_historical_image_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PredictionHistoricalImageResponse {
  /// Returns a new [PredictionHistoricalImageResponse] instance.
  PredictionHistoricalImageResponse({
    this.id,

    this.createdAt,

    this.disease,

    this.severityPct,

    this.severityBucket,

    this.rawPath,

    this.processedPath,

    this.rawUrl,

    this.processedUrl,
  });

  @JsonKey(name: r'id', required: false, includeIfNull: false)
  final int? id;

  @JsonKey(name: r'created_at', required: false, includeIfNull: false)
  final String? createdAt;

  @JsonKey(name: r'disease', required: false, includeIfNull: false)
  final String? disease;

  @JsonKey(name: r'severity_pct', required: false, includeIfNull: false)
  final num? severityPct;

  @JsonKey(name: r'severity_bucket', required: false, includeIfNull: false)
  final String? severityBucket;

  @JsonKey(name: r'raw_path', required: false, includeIfNull: false)
  final String? rawPath;

  @JsonKey(name: r'processed_path', required: false, includeIfNull: false)
  final String? processedPath;

  @JsonKey(name: r'raw_url', required: false, includeIfNull: false)
  final String? rawUrl;

  @JsonKey(name: r'processed_url', required: false, includeIfNull: false)
  final String? processedUrl;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PredictionHistoricalImageResponse &&
          other.id == id &&
          other.createdAt == createdAt &&
          other.disease == disease &&
          other.severityPct == severityPct &&
          other.severityBucket == severityBucket &&
          other.rawPath == rawPath &&
          other.processedPath == processedPath &&
          other.rawUrl == rawUrl &&
          other.processedUrl == processedUrl;

  @override
  int get hashCode =>
      (id == null ? 0 : id.hashCode) +
      (createdAt == null ? 0 : createdAt.hashCode) +
      (disease == null ? 0 : disease.hashCode) +
      (severityPct == null ? 0 : severityPct.hashCode) +
      (severityBucket == null ? 0 : severityBucket.hashCode) +
      (rawPath == null ? 0 : rawPath.hashCode) +
      (processedPath == null ? 0 : processedPath.hashCode) +
      (rawUrl == null ? 0 : rawUrl.hashCode) +
      (processedUrl == null ? 0 : processedUrl.hashCode);

  factory PredictionHistoricalImageResponse.fromJson(
    Map<String, dynamic> json,
  ) => _$PredictionHistoricalImageResponseFromJson(json);

  Map<String, dynamic> toJson() =>
      _$PredictionHistoricalImageResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
