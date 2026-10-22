// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prediction_historical_image_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PredictionHistoricalImageResponseCWProxy {
  PredictionHistoricalImageResponse id(int? id);

  PredictionHistoricalImageResponse createdAt(String? createdAt);

  PredictionHistoricalImageResponse disease(String? disease);

  PredictionHistoricalImageResponse severityPct(num? severityPct);

  PredictionHistoricalImageResponse severityBucket(String? severityBucket);

  PredictionHistoricalImageResponse rawPath(String? rawPath);

  PredictionHistoricalImageResponse processedPath(String? processedPath);

  PredictionHistoricalImageResponse rawUrl(String? rawUrl);

  PredictionHistoricalImageResponse processedUrl(String? processedUrl);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionHistoricalImageResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionHistoricalImageResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionHistoricalImageResponse call({
    int? id,
    String? createdAt,
    String? disease,
    num? severityPct,
    String? severityBucket,
    String? rawPath,
    String? processedPath,
    String? rawUrl,
    String? processedUrl,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPredictionHistoricalImageResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPredictionHistoricalImageResponse.copyWith.fieldName(...)`
class _$PredictionHistoricalImageResponseCWProxyImpl
    implements _$PredictionHistoricalImageResponseCWProxy {
  const _$PredictionHistoricalImageResponseCWProxyImpl(this._value);

  final PredictionHistoricalImageResponse _value;

  @override
  PredictionHistoricalImageResponse id(int? id) => this(id: id);

  @override
  PredictionHistoricalImageResponse createdAt(String? createdAt) =>
      this(createdAt: createdAt);

  @override
  PredictionHistoricalImageResponse disease(String? disease) =>
      this(disease: disease);

  @override
  PredictionHistoricalImageResponse severityPct(num? severityPct) =>
      this(severityPct: severityPct);

  @override
  PredictionHistoricalImageResponse severityBucket(String? severityBucket) =>
      this(severityBucket: severityBucket);

  @override
  PredictionHistoricalImageResponse rawPath(String? rawPath) =>
      this(rawPath: rawPath);

  @override
  PredictionHistoricalImageResponse processedPath(String? processedPath) =>
      this(processedPath: processedPath);

  @override
  PredictionHistoricalImageResponse rawUrl(String? rawUrl) =>
      this(rawUrl: rawUrl);

  @override
  PredictionHistoricalImageResponse processedUrl(String? processedUrl) =>
      this(processedUrl: processedUrl);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionHistoricalImageResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionHistoricalImageResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionHistoricalImageResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? createdAt = const $CopyWithPlaceholder(),
    Object? disease = const $CopyWithPlaceholder(),
    Object? severityPct = const $CopyWithPlaceholder(),
    Object? severityBucket = const $CopyWithPlaceholder(),
    Object? rawPath = const $CopyWithPlaceholder(),
    Object? processedPath = const $CopyWithPlaceholder(),
    Object? rawUrl = const $CopyWithPlaceholder(),
    Object? processedUrl = const $CopyWithPlaceholder(),
  }) {
    return PredictionHistoricalImageResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as int?,
      createdAt: createdAt == const $CopyWithPlaceholder()
          ? _value.createdAt
          // ignore: cast_nullable_to_non_nullable
          : createdAt as String?,
      disease: disease == const $CopyWithPlaceholder()
          ? _value.disease
          // ignore: cast_nullable_to_non_nullable
          : disease as String?,
      severityPct: severityPct == const $CopyWithPlaceholder()
          ? _value.severityPct
          // ignore: cast_nullable_to_non_nullable
          : severityPct as num?,
      severityBucket: severityBucket == const $CopyWithPlaceholder()
          ? _value.severityBucket
          // ignore: cast_nullable_to_non_nullable
          : severityBucket as String?,
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
    );
  }
}

extension $PredictionHistoricalImageResponseCopyWith
    on PredictionHistoricalImageResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPredictionHistoricalImageResponse.copyWith(...)` or like so:`instanceOfPredictionHistoricalImageResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PredictionHistoricalImageResponseCWProxy get copyWith =>
      _$PredictionHistoricalImageResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PredictionHistoricalImageResponse _$PredictionHistoricalImageResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'PredictionHistoricalImageResponse',
  json,
  ($checkedConvert) {
    final val = PredictionHistoricalImageResponse(
      id: $checkedConvert('id', (v) => (v as num?)?.toInt()),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
      disease: $checkedConvert('disease', (v) => v as String?),
      severityPct: $checkedConvert('severity_pct', (v) => v as num?),
      severityBucket: $checkedConvert('severity_bucket', (v) => v as String?),
      rawPath: $checkedConvert('raw_path', (v) => v as String?),
      processedPath: $checkedConvert('processed_path', (v) => v as String?),
      rawUrl: $checkedConvert('raw_url', (v) => v as String?),
      processedUrl: $checkedConvert('processed_url', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'createdAt': 'created_at',
    'severityPct': 'severity_pct',
    'severityBucket': 'severity_bucket',
    'rawPath': 'raw_path',
    'processedPath': 'processed_path',
    'rawUrl': 'raw_url',
    'processedUrl': 'processed_url',
  },
);

Map<String, dynamic> _$PredictionHistoricalImageResponseToJson(
  PredictionHistoricalImageResponse instance,
) => <String, dynamic>{
  'id': ?instance.id,
  'created_at': ?instance.createdAt,
  'disease': ?instance.disease,
  'severity_pct': ?instance.severityPct,
  'severity_bucket': ?instance.severityBucket,
  'raw_path': ?instance.rawPath,
  'processed_path': ?instance.processedPath,
  'raw_url': ?instance.rawUrl,
  'processed_url': ?instance.processedUrl,
};
