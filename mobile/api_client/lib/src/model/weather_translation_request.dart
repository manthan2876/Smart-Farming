//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'weather_translation_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WeatherTranslationRequest {
  /// Returns a new [WeatherTranslationRequest] instance.
  WeatherTranslationRequest({required this.text, required this.targetLanguage});

  @JsonKey(name: r'text', required: true, includeIfNull: false)
  final String text;

  @JsonKey(name: r'target_language', required: true, includeIfNull: false)
  final String targetLanguage;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WeatherTranslationRequest &&
          other.text == text &&
          other.targetLanguage == targetLanguage;

  @override
  int get hashCode => text.hashCode + targetLanguage.hashCode;

  factory WeatherTranslationRequest.fromJson(Map<String, dynamic> json) =>
      _$WeatherTranslationRequestFromJson(json);

  Map<String, dynamic> toJson() => _$WeatherTranslationRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
