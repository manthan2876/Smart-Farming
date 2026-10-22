//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'prediction_status_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PredictionStatusResponse {
  /// Returns a new [PredictionStatusResponse] instance.
  PredictionStatusResponse({
    this.pipeline,

    this.preprocessing,

    this.expertReview,
  });

  @JsonKey(name: r'pipeline', required: false, includeIfNull: false)
  final String? pipeline;

  @JsonKey(name: r'preprocessing', required: false, includeIfNull: false)
  final String? preprocessing;

  @JsonKey(name: r'expert_review', required: false, includeIfNull: false)
  final String? expertReview;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PredictionStatusResponse &&
          other.pipeline == pipeline &&
          other.preprocessing == preprocessing &&
          other.expertReview == expertReview;

  @override
  int get hashCode =>
      (pipeline == null ? 0 : pipeline.hashCode) +
      (preprocessing == null ? 0 : preprocessing.hashCode) +
      (expertReview == null ? 0 : expertReview.hashCode);

  factory PredictionStatusResponse.fromJson(Map<String, dynamic> json) =>
      _$PredictionStatusResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PredictionStatusResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
