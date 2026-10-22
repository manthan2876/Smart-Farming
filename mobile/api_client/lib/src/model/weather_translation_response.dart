//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'weather_translation_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WeatherTranslationResponse {
  /// Returns a new [WeatherTranslationResponse] instance.
  WeatherTranslationResponse({
    required this.translatedText,

    required this.language,
  });

  @JsonKey(name: r'translated_text', required: true, includeIfNull: false)
  final String translatedText;

  @JsonKey(name: r'language', required: true, includeIfNull: false)
  final String language;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WeatherTranslationResponse &&
          other.translatedText == translatedText &&
          other.language == language;

  @override
  int get hashCode => translatedText.hashCode + language.hashCode;

  factory WeatherTranslationResponse.fromJson(Map<String, dynamic> json) =>
      _$WeatherTranslationResponseFromJson(json);

  Map<String, dynamic> toJson() => _$WeatherTranslationResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
