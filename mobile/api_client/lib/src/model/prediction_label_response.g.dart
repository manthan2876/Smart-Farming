// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prediction_label_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PredictionLabelResponseCWProxy {
  PredictionLabelResponse label(String? label);

  PredictionLabelResponse confidence(num? confidence);

  PredictionLabelResponse modelUsed(String? modelUsed);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionLabelResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionLabelResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionLabelResponse call({
    String? label,
    num? confidence,
    String? modelUsed,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPredictionLabelResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPredictionLabelResponse.copyWith.fieldName(...)`
class _$PredictionLabelResponseCWProxyImpl
    implements _$PredictionLabelResponseCWProxy {
  const _$PredictionLabelResponseCWProxyImpl(this._value);

  final PredictionLabelResponse _value;

  @override
  PredictionLabelResponse label(String? label) => this(label: label);

  @override
  PredictionLabelResponse confidence(num? confidence) =>
      this(confidence: confidence);

  @override
  PredictionLabelResponse modelUsed(String? modelUsed) =>
      this(modelUsed: modelUsed);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionLabelResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionLabelResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionLabelResponse call({
    Object? label = const $CopyWithPlaceholder(),
    Object? confidence = const $CopyWithPlaceholder(),
    Object? modelUsed = const $CopyWithPlaceholder(),
  }) {
    return PredictionLabelResponse(
      label: label == const $CopyWithPlaceholder()
          ? _value.label
          // ignore: cast_nullable_to_non_nullable
          : label as String?,
      confidence: confidence == const $CopyWithPlaceholder()
          ? _value.confidence
          // ignore: cast_nullable_to_non_nullable
          : confidence as num?,
      modelUsed: modelUsed == const $CopyWithPlaceholder()
          ? _value.modelUsed
          // ignore: cast_nullable_to_non_nullable
          : modelUsed as String?,
    );
  }
}

extension $PredictionLabelResponseCopyWith on PredictionLabelResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPredictionLabelResponse.copyWith(...)` or like so:`instanceOfPredictionLabelResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PredictionLabelResponseCWProxy get copyWith =>
      _$PredictionLabelResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PredictionLabelResponse _$PredictionLabelResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('PredictionLabelResponse', json, ($checkedConvert) {
  final val = PredictionLabelResponse(
    label: $checkedConvert('label', (v) => v as String?),
    confidence: $checkedConvert('confidence', (v) => v as num?),
    modelUsed: $checkedConvert('model_used', (v) => v as String?),
  );
  return val;
}, fieldKeyMap: const {'modelUsed': 'model_used'});

Map<String, dynamic> _$PredictionLabelResponseToJson(
  PredictionLabelResponse instance,
) => <String, dynamic>{
  'label': ?instance.label,
  'confidence': ?instance.confidence,
  'model_used': ?instance.modelUsed,
};
