// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'weather_translation_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WeatherTranslationResponseCWProxy {
  WeatherTranslationResponse translatedText(String translatedText);

  WeatherTranslationResponse language(String language);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WeatherTranslationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WeatherTranslationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  WeatherTranslationResponse call({String translatedText, String language});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWeatherTranslationResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWeatherTranslationResponse.copyWith.fieldName(...)`
class _$WeatherTranslationResponseCWProxyImpl
    implements _$WeatherTranslationResponseCWProxy {
  const _$WeatherTranslationResponseCWProxyImpl(this._value);

  final WeatherTranslationResponse _value;

  @override
  WeatherTranslationResponse translatedText(String translatedText) =>
      this(translatedText: translatedText);

  @override
  WeatherTranslationResponse language(String language) =>
      this(language: language);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WeatherTranslationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WeatherTranslationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  WeatherTranslationResponse call({
    Object? translatedText = const $CopyWithPlaceholder(),
    Object? language = const $CopyWithPlaceholder(),
  }) {
    return WeatherTranslationResponse(
      translatedText: translatedText == const $CopyWithPlaceholder()
          ? _value.translatedText
          // ignore: cast_nullable_to_non_nullable
          : translatedText as String,
      language: language == const $CopyWithPlaceholder()
          ? _value.language
          // ignore: cast_nullable_to_non_nullable
          : language as String,
    );
  }
}

extension $WeatherTranslationResponseCopyWith on WeatherTranslationResponse {
  /// Returns a callable class that can be used as follows: `instanceOfWeatherTranslationResponse.copyWith(...)` or like so:`instanceOfWeatherTranslationResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WeatherTranslationResponseCWProxy get copyWith =>
      _$WeatherTranslationResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WeatherTranslationResponse _$WeatherTranslationResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('WeatherTranslationResponse', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['translated_text', 'language']);
  final val = WeatherTranslationResponse(
    translatedText: $checkedConvert('translated_text', (v) => v as String),
    language: $checkedConvert('language', (v) => v as String),
  );
  return val;
}, fieldKeyMap: const {'translatedText': 'translated_text'});

Map<String, dynamic> _$WeatherTranslationResponseToJson(
  WeatherTranslationResponse instance,
) => <String, dynamic>{
  'translated_text': instance.translatedText,
  'language': instance.language,
};
