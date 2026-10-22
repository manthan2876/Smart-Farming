// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prediction_severity_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PredictionSeverityResponseCWProxy {
  PredictionSeverityResponse percent(num? percent);

  PredictionSeverityResponse bucket(String? bucket);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionSeverityResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionSeverityResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionSeverityResponse call({num? percent, String? bucket});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPredictionSeverityResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPredictionSeverityResponse.copyWith.fieldName(...)`
class _$PredictionSeverityResponseCWProxyImpl
    implements _$PredictionSeverityResponseCWProxy {
  const _$PredictionSeverityResponseCWProxyImpl(this._value);

  final PredictionSeverityResponse _value;

  @override
  PredictionSeverityResponse percent(num? percent) => this(percent: percent);

  @override
  PredictionSeverityResponse bucket(String? bucket) => this(bucket: bucket);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionSeverityResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionSeverityResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionSeverityResponse call({
    Object? percent = const $CopyWithPlaceholder(),
    Object? bucket = const $CopyWithPlaceholder(),
  }) {
    return PredictionSeverityResponse(
      percent: percent == const $CopyWithPlaceholder()
          ? _value.percent
          // ignore: cast_nullable_to_non_nullable
          : percent as num?,
      bucket: bucket == const $CopyWithPlaceholder()
          ? _value.bucket
          // ignore: cast_nullable_to_non_nullable
          : bucket as String?,
    );
  }
}

extension $PredictionSeverityResponseCopyWith on PredictionSeverityResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPredictionSeverityResponse.copyWith(...)` or like so:`instanceOfPredictionSeverityResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PredictionSeverityResponseCWProxy get copyWith =>
      _$PredictionSeverityResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PredictionSeverityResponse _$PredictionSeverityResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('PredictionSeverityResponse', json, ($checkedConvert) {
  final val = PredictionSeverityResponse(
    percent: $checkedConvert('percent', (v) => v as num?),
    bucket: $checkedConvert('bucket', (v) => v as String?),
  );
  return val;
});

Map<String, dynamic> _$PredictionSeverityResponseToJson(
  PredictionSeverityResponse instance,
) => <String, dynamic>{
  'percent': ?instance.percent,
  'bucket': ?instance.bucket,
};
