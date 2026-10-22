//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'prediction_translation_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PredictionTranslationResponse {
  /// Returns a new [PredictionTranslationResponse] instance.
  PredictionTranslationResponse({
    required this.predictionId,

    required this.language,

    required this.cached,

    required this.recommendation,

    this.expertGuidance,

    this.translations,

    this.translationStatus,

    this.warning,
  });

  @JsonKey(name: r'prediction_id', required: true, includeIfNull: false)
  final int predictionId;

  @JsonKey(name: r'language', required: true, includeIfNull: false)
  final String language;

  @JsonKey(name: r'cached', required: true, includeIfNull: false)
  final bool cached;

  @JsonKey(name: r'recommendation', required: true, includeIfNull: false)
  final Map<String, String> recommendation;

  @JsonKey(name: r'expert_guidance', required: false, includeIfNull: false)
  final String? expertGuidance;

  @JsonKey(name: r'translations', required: false, includeIfNull: false)
  final Map<String, Map<String, String>>? translations;

  @JsonKey(name: r'translation_status', required: false, includeIfNull: false)
  final String? translationStatus;

  @JsonKey(name: r'warning', required: false, includeIfNull: false)
  final String? warning;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PredictionTranslationResponse &&
          other.predictionId == predictionId &&
          other.language == language &&
          other.cached == cached &&
          other.recommendation == recommendation &&
          other.expertGuidance == expertGuidance &&
          other.translations == translations &&
          other.translationStatus == translationStatus &&
          other.warning == warning;

  @override
  int get hashCode =>
      predictionId.hashCode +
      language.hashCode +
      cached.hashCode +
      recommendation.hashCode +
      (expertGuidance == null ? 0 : expertGuidance.hashCode) +
      (translations == null ? 0 : translations.hashCode) +
      (translationStatus == null ? 0 : translationStatus.hashCode) +
      (warning == null ? 0 : warning.hashCode);

  factory PredictionTranslationResponse.fromJson(Map<String, dynamic> json) =>
      _$PredictionTranslationResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PredictionTranslationResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
