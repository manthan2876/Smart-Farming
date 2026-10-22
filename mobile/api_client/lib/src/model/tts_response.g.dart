// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'tts_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$TTSResponseCWProxy {
  TTSResponse audioContent(String audioContent);

  TTSResponse format(String format);

  TTSResponse cached(bool cached);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TTSResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TTSResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  TTSResponse call({String audioContent, String format, bool cached});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfTTSResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfTTSResponse.copyWith.fieldName(...)`
class _$TTSResponseCWProxyImpl implements _$TTSResponseCWProxy {
  const _$TTSResponseCWProxyImpl(this._value);

  final TTSResponse _value;

  @override
  TTSResponse audioContent(String audioContent) =>
      this(audioContent: audioContent);

  @override
  TTSResponse format(String format) => this(format: format);

  @override
  TTSResponse cached(bool cached) => this(cached: cached);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TTSResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TTSResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  TTSResponse call({
    Object? audioContent = const $CopyWithPlaceholder(),
    Object? format = const $CopyWithPlaceholder(),
    Object? cached = const $CopyWithPlaceholder(),
  }) {
    return TTSResponse(
      audioContent: audioContent == const $CopyWithPlaceholder()
          ? _value.audioContent
          // ignore: cast_nullable_to_non_nullable
          : audioContent as String,
      format: format == const $CopyWithPlaceholder()
          ? _value.format
          // ignore: cast_nullable_to_non_nullable
          : format as String,
      cached: cached == const $CopyWithPlaceholder()
          ? _value.cached
          // ignore: cast_nullable_to_non_nullable
          : cached as bool,
    );
  }
}

extension $TTSResponseCopyWith on TTSResponse {
  /// Returns a callable class that can be used as follows: `instanceOfTTSResponse.copyWith(...)` or like so:`instanceOfTTSResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$TTSResponseCWProxy get copyWith => _$TTSResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TTSResponse _$TTSResponseFromJson(Map<String, dynamic> json) => $checkedCreate(
  'TTSResponse',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['audioContent', 'format', 'cached']);
    final val = TTSResponse(
      audioContent: $checkedConvert('audioContent', (v) => v as String),
      format: $checkedConvert('format', (v) => v as String),
      cached: $checkedConvert('cached', (v) => v as bool),
    );
    return val;
  },
);

Map<String, dynamic> _$TTSResponseToJson(TTSResponse instance) =>
    <String, dynamic>{
      'audioContent': instance.audioContent,
      'format': instance.format,
      'cached': instance.cached,
    };
