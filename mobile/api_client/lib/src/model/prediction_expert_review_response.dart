//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'prediction_expert_review_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PredictionExpertReviewResponse {
  /// Returns a new [PredictionExpertReviewResponse] instance.
  PredictionExpertReviewResponse({
    this.decision,

    this.correctedDisease,

    this.correctedSeverity,

    this.farmerGuidance,

    this.status,
  });

  @JsonKey(name: r'decision', required: false, includeIfNull: false)
  final String? decision;

  @JsonKey(name: r'corrected_disease', required: false, includeIfNull: false)
  final String? correctedDisease;

  @JsonKey(name: r'corrected_severity', required: false, includeIfNull: false)
  final num? correctedSeverity;

  @JsonKey(name: r'farmer_guidance', required: false, includeIfNull: false)
  final String? farmerGuidance;

  @JsonKey(name: r'status', required: false, includeIfNull: false)
  final String? status;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PredictionExpertReviewResponse &&
          other.decision == decision &&
          other.correctedDisease == correctedDisease &&
          other.correctedSeverity == correctedSeverity &&
          other.farmerGuidance == farmerGuidance &&
          other.status == status;

  @override
  int get hashCode =>
      (decision == null ? 0 : decision.hashCode) +
      (correctedDisease == null ? 0 : correctedDisease.hashCode) +
      (correctedSeverity == null ? 0 : correctedSeverity.hashCode) +
      (farmerGuidance == null ? 0 : farmerGuidance.hashCode) +
      (status == null ? 0 : status.hashCode);

  factory PredictionExpertReviewResponse.fromJson(Map<String, dynamic> json) =>
      _$PredictionExpertReviewResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PredictionExpertReviewResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
