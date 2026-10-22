// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'weather_translation_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WeatherTranslationRequestCWProxy {
  WeatherTranslationRequest text(String text);

  WeatherTranslationRequest targetLanguage(String targetLanguage);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WeatherTranslationRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WeatherTranslationRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  WeatherTranslationRequest call({String text, String targetLanguage});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWeatherTranslationRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWeatherTranslationRequest.copyWith.fieldName(...)`
class _$WeatherTranslationRequestCWProxyImpl
    implements _$WeatherTranslationRequestCWProxy {
  const _$WeatherTranslationRequestCWProxyImpl(this._value);

  final WeatherTranslationRequest _value;

  @override
  WeatherTranslationRequest text(String text) => this(text: text);

  @override
  WeatherTranslationRequest targetLanguage(String targetLanguage) =>
      this(targetLanguage: targetLanguage);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WeatherTranslationRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WeatherTranslationRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  WeatherTranslationRequest call({
    Object? text = const $CopyWithPlaceholder(),
    Object? targetLanguage = const $CopyWithPlaceholder(),
  }) {
    return WeatherTranslationRequest(
      text: text == const $CopyWithPlaceholder()
          ? _value.text
          // ignore: cast_nullable_to_non_nullable
          : text as String,
      targetLanguage: targetLanguage == const $CopyWithPlaceholder()
          ? _value.targetLanguage
          // ignore: cast_nullable_to_non_nullable
          : targetLanguage as String,
    );
  }
}

extension $WeatherTranslationRequestCopyWith on WeatherTranslationRequest {
  /// Returns a callable class that can be used as follows: `instanceOfWeatherTranslationRequest.copyWith(...)` or like so:`instanceOfWeatherTranslationRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WeatherTranslationRequestCWProxy get copyWith =>
      _$WeatherTranslationRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WeatherTranslationRequest _$WeatherTranslationRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('WeatherTranslationRequest', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['text', 'target_language']);
  final val = WeatherTranslationRequest(
    text: $checkedConvert('text', (v) => v as String),
    targetLanguage: $checkedConvert('target_language', (v) => v as String),
  );
  return val;
}, fieldKeyMap: const {'targetLanguage': 'target_language'});

Map<String, dynamic> _$WeatherTranslationRequestToJson(
  WeatherTranslationRequest instance,
) => <String, dynamic>{
  'text': instance.text,
  'target_language': instance.targetLanguage,
};
