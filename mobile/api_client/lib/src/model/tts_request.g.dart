// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'tts_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$TTSRequestCWProxy {
  TTSRequest text(String text);

  TTSRequest language(String? language);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TTSRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TTSRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  TTSRequest call({String text, String? language});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfTTSRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfTTSRequest.copyWith.fieldName(...)`
class _$TTSRequestCWProxyImpl implements _$TTSRequestCWProxy {
  const _$TTSRequestCWProxyImpl(this._value);

  final TTSRequest _value;

  @override
  TTSRequest text(String text) => this(text: text);

  @override
  TTSRequest language(String? language) => this(language: language);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TTSRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TTSRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  TTSRequest call({
    Object? text = const $CopyWithPlaceholder(),
    Object? language = const $CopyWithPlaceholder(),
  }) {
    return TTSRequest(
      text: text == const $CopyWithPlaceholder()
          ? _value.text
          // ignore: cast_nullable_to_non_nullable
          : text as String,
      language: language == const $CopyWithPlaceholder()
          ? _value.language
          // ignore: cast_nullable_to_non_nullable
          : language as String?,
    );
  }
}

extension $TTSRequestCopyWith on TTSRequest {
  /// Returns a callable class that can be used as follows: `instanceOfTTSRequest.copyWith(...)` or like so:`instanceOfTTSRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$TTSRequestCWProxy get copyWith => _$TTSRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TTSRequest _$TTSRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate('TTSRequest', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['text']);
      final val = TTSRequest(
        text: $checkedConvert('text', (v) => v as String),
        language: $checkedConvert('language', (v) => v as String?),
      );
      return val;
    });

Map<String, dynamic> _$TTSRequestToJson(TTSRequest instance) =>
    <String, dynamic>{'text': instance.text, 'language': ?instance.language};
