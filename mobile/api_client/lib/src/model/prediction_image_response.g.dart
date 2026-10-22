// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prediction_image_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PredictionImageResponseCWProxy {
  PredictionImageResponse rawPath(String? rawPath);

  PredictionImageResponse processedPath(String? processedPath);

  PredictionImageResponse rawUrl(String? rawUrl);

  PredictionImageResponse processedUrl(String? processedUrl);

  PredictionImageResponse qualityScore(num? qualityScore);

  PredictionImageResponse leafDetected(bool? leafDetected);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionImageResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionImageResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionImageResponse call({
    String? rawPath,
    String? processedPath,
    String? rawUrl,
    String? processedUrl,
    num? qualityScore,
    bool? leafDetected,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPredictionImageResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPredictionImageResponse.copyWith.fieldName(...)`
class _$PredictionImageResponseCWProxyImpl
    implements _$PredictionImageResponseCWProxy {
  const _$PredictionImageResponseCWProxyImpl(this._value);

  final PredictionImageResponse _value;

  @override
  PredictionImageResponse rawPath(String? rawPath) => this(rawPath: rawPath);

  @override
  PredictionImageResponse processedPath(String? processedPath) =>
      this(processedPath: processedPath);

  @override
  PredictionImageResponse rawUrl(String? rawUrl) => this(rawUrl: rawUrl);

  @override
  PredictionImageResponse processedUrl(String? processedUrl) =>
      this(processedUrl: processedUrl);

  @override
  PredictionImageResponse qualityScore(num? qualityScore) =>
      this(qualityScore: qualityScore);

  @override
  PredictionImageResponse leafDetected(bool? leafDetected) =>
      this(leafDetected: leafDetected);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionImageResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionImageResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionImageResponse call({
    Object? rawPath = const $CopyWithPlaceholder(),
    Object? processedPath = const $CopyWithPlaceholder(),
    Object? rawUrl = const $CopyWithPlaceholder(),
    Object? processedUrl = const $CopyWithPlaceholder(),
    Object? qualityScore = const $CopyWithPlaceholder(),
    Object? leafDetected = const $CopyWithPlaceholder(),
  }) {
    return PredictionImageResponse(
      rawPath: rawPath == const $CopyWithPlaceholder()
          ? _value.rawPath
          // ignore: cast_nullable_to_non_nullable
          : rawPath as String?,
      processedPath: processedPath == const $CopyWithPlaceholder()
          ? _value.processedPath
          // ignore: cast_nullable_to_non_nullable
          : processedPath as String?,
      rawUrl: rawUrl == const $CopyWithPlaceholder()
          ? _value.rawUrl
          // ignore: cast_nullable_to_non_nullable
          : rawUrl as String?,
      processedUrl: processedUrl == const $CopyWithPlaceholder()
          ? _value.processedUrl
          // ignore: cast_nullable_to_non_nullable
          : processedUrl as String?,
      qualityScore: qualityScore == const $CopyWithPlaceholder()
          ? _value.qualityScore
          // ignore: cast_nullable_to_non_nullable
          : qualityScore as num?,
      leafDetected: leafDetected == const $CopyWithPlaceholder()
          ? _value.leafDetected
          // ignore: cast_nullable_to_non_nullable
          : leafDetected as bool?,
    );
  }
}

extension $PredictionImageResponseCopyWith on PredictionImageResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPredictionImageResponse.copyWith(...)` or like so:`instanceOfPredictionImageResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PredictionImageResponseCWProxy get copyWith =>
      _$PredictionImageResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PredictionImageResponse _$PredictionImageResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'PredictionImageResponse',
  json,
  ($checkedConvert) {
    final val = PredictionImageResponse(
      rawPath: $checkedConvert('raw_path', (v) => v as String?),
      processedPath: $checkedConvert('processed_path', (v) => v as String?),
      rawUrl: $checkedConvert('raw_url', (v) => v as String?),
      processedUrl: $checkedConvert('processed_url', (v) => v as String?),
      qualityScore: $checkedConvert('quality_score', (v) => v as num?),
      leafDetected: $checkedConvert('leaf_detected', (v) => v as bool?),
    );
    return val;
  },
  fieldKeyMap: const {
    'rawPath': 'raw_path',
    'processedPath': 'processed_path',
    'rawUrl': 'raw_url',
    'processedUrl': 'processed_url',
    'qualityScore': 'quality_score',
    'leafDetected': 'leaf_detected',
  },
);

Map<String, dynamic> _$PredictionImageResponseToJson(
  PredictionImageResponse instance,
) => <String, dynamic>{
  'raw_path': ?instance.rawPath,
  'processed_path': ?instance.processedPath,
  'raw_url': ?instance.rawUrl,
  'processed_url': ?instance.processedUrl,
  'quality_score': ?instance.qualityScore,
  'leaf_detected': ?instance.leafDetected,
};
