// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prediction_status_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PredictionStatusResponseCWProxy {
  PredictionStatusResponse pipeline(String? pipeline);

  PredictionStatusResponse preprocessing(String? preprocessing);

  PredictionStatusResponse expertReview(String? expertReview);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionStatusResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionStatusResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionStatusResponse call({
    String? pipeline,
    String? preprocessing,
    String? expertReview,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPredictionStatusResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPredictionStatusResponse.copyWith.fieldName(...)`
class _$PredictionStatusResponseCWProxyImpl
    implements _$PredictionStatusResponseCWProxy {
  const _$PredictionStatusResponseCWProxyImpl(this._value);

  final PredictionStatusResponse _value;

  @override
  PredictionStatusResponse pipeline(String? pipeline) =>
      this(pipeline: pipeline);

  @override
  PredictionStatusResponse preprocessing(String? preprocessing) =>
      this(preprocessing: preprocessing);

  @override
  PredictionStatusResponse expertReview(String? expertReview) =>
      this(expertReview: expertReview);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionStatusResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionStatusResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionStatusResponse call({
    Object? pipeline = const $CopyWithPlaceholder(),
    Object? preprocessing = const $CopyWithPlaceholder(),
    Object? expertReview = const $CopyWithPlaceholder(),
  }) {
    return PredictionStatusResponse(
      pipeline: pipeline == const $CopyWithPlaceholder()
          ? _value.pipeline
          // ignore: cast_nullable_to_non_nullable
          : pipeline as String?,
      preprocessing: preprocessing == const $CopyWithPlaceholder()
          ? _value.preprocessing
          // ignore: cast_nullable_to_non_nullable
          : preprocessing as String?,
      expertReview: expertReview == const $CopyWithPlaceholder()
          ? _value.expertReview
          // ignore: cast_nullable_to_non_nullable
          : expertReview as String?,
    );
  }
}

extension $PredictionStatusResponseCopyWith on PredictionStatusResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPredictionStatusResponse.copyWith(...)` or like so:`instanceOfPredictionStatusResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PredictionStatusResponseCWProxy get copyWith =>
      _$PredictionStatusResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PredictionStatusResponse _$PredictionStatusResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('PredictionStatusResponse', json, ($checkedConvert) {
  final val = PredictionStatusResponse(
    pipeline: $checkedConvert('pipeline', (v) => v as String?),
    preprocessing: $checkedConvert('preprocessing', (v) => v as String?),
    expertReview: $checkedConvert('expert_review', (v) => v as String?),
  );
  return val;
}, fieldKeyMap: const {'expertReview': 'expert_review'});

Map<String, dynamic> _$PredictionStatusResponseToJson(
  PredictionStatusResponse instance,
) => <String, dynamic>{
  'pipeline': ?instance.pipeline,
  'preprocessing': ?instance.preprocessing,
  'expert_review': ?instance.expertReview,
};
