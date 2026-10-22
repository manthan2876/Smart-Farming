//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
// ignore: unused_import
import 'package:smart_farming_api/src/model/prediction_recommendation_response.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'recommendation.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class Recommendation {
  /// Returns a new [Recommendation] instance.
  Recommendation({
    this.immediateAction,

    this.treatment,

    this.prevention,

    this.monitoring,

    this.safetyDisclaimer,
  });

  @JsonKey(name: r'immediate_action', required: false, includeIfNull: false)
  final String? immediateAction;

  @JsonKey(name: r'treatment', required: false, includeIfNull: false)
  final String? treatment;

  @JsonKey(name: r'prevention', required: false, includeIfNull: false)
  final String? prevention;

  @JsonKey(name: r'monitoring', required: false, includeIfNull: false)
  final String? monitoring;

  @JsonKey(name: r'safety_disclaimer', required: false, includeIfNull: false)
  final String? safetyDisclaimer;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Recommendation &&
          other.immediateAction == immediateAction &&
          other.treatment == treatment &&
          other.prevention == prevention &&
          other.monitoring == monitoring &&
          other.safetyDisclaimer == safetyDisclaimer;

  @override
  int get hashCode =>
      (immediateAction == null ? 0 : immediateAction.hashCode) +
      (treatment == null ? 0 : treatment.hashCode) +
      (prevention == null ? 0 : prevention.hashCode) +
      (monitoring == null ? 0 : monitoring.hashCode) +
      (safetyDisclaimer == null ? 0 : safetyDisclaimer.hashCode);

  factory Recommendation.fromJson(Map<String, dynamic> json) =>
      _$RecommendationFromJson(json);

  Map<String, dynamic> toJson() => _$RecommendationToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
