// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prediction_recommendation_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PredictionRecommendationResponseCWProxy {
  PredictionRecommendationResponse immediateAction(String? immediateAction);

  PredictionRecommendationResponse treatment(String? treatment);

  PredictionRecommendationResponse prevention(String? prevention);

  PredictionRecommendationResponse monitoring(String? monitoring);

  PredictionRecommendationResponse safetyDisclaimer(String? safetyDisclaimer);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionRecommendationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionRecommendationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionRecommendationResponse call({
    String? immediateAction,
    String? treatment,
    String? prevention,
    String? monitoring,
    String? safetyDisclaimer,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPredictionRecommendationResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPredictionRecommendationResponse.copyWith.fieldName(...)`
class _$PredictionRecommendationResponseCWProxyImpl
    implements _$PredictionRecommendationResponseCWProxy {
  const _$PredictionRecommendationResponseCWProxyImpl(this._value);

  final PredictionRecommendationResponse _value;

  @override
  PredictionRecommendationResponse immediateAction(String? immediateAction) =>
      this(immediateAction: immediateAction);

  @override
  PredictionRecommendationResponse treatment(String? treatment) =>
      this(treatment: treatment);

  @override
  PredictionRecommendationResponse prevention(String? prevention) =>
      this(prevention: prevention);

  @override
  PredictionRecommendationResponse monitoring(String? monitoring) =>
      this(monitoring: monitoring);

  @override
  PredictionRecommendationResponse safetyDisclaimer(String? safetyDisclaimer) =>
      this(safetyDisclaimer: safetyDisclaimer);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionRecommendationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionRecommendationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionRecommendationResponse call({
    Object? immediateAction = const $CopyWithPlaceholder(),
    Object? treatment = const $CopyWithPlaceholder(),
    Object? prevention = const $CopyWithPlaceholder(),
    Object? monitoring = const $CopyWithPlaceholder(),
    Object? safetyDisclaimer = const $CopyWithPlaceholder(),
  }) {
    return PredictionRecommendationResponse(
      immediateAction: immediateAction == const $CopyWithPlaceholder()
          ? _value.immediateAction
          // ignore: cast_nullable_to_non_nullable
          : immediateAction as String?,
      treatment: treatment == const $CopyWithPlaceholder()
          ? _value.treatment
          // ignore: cast_nullable_to_non_nullable
          : treatment as String?,
      prevention: prevention == const $CopyWithPlaceholder()
          ? _value.prevention
          // ignore: cast_nullable_to_non_nullable
          : prevention as String?,
      monitoring: monitoring == const $CopyWithPlaceholder()
          ? _value.monitoring
          // ignore: cast_nullable_to_non_nullable
          : monitoring as String?,
      safetyDisclaimer: safetyDisclaimer == const $CopyWithPlaceholder()
          ? _value.safetyDisclaimer
          // ignore: cast_nullable_to_non_nullable
          : safetyDisclaimer as String?,
    );
  }
}

extension $PredictionRecommendationResponseCopyWith
    on PredictionRecommendationResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPredictionRecommendationResponse.copyWith(...)` or like so:`instanceOfPredictionRecommendationResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PredictionRecommendationResponseCWProxy get copyWith =>
      _$PredictionRecommendationResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PredictionRecommendationResponse _$PredictionRecommendationResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'PredictionRecommendationResponse',
  json,
  ($checkedConvert) {
    final val = PredictionRecommendationResponse(
      immediateAction: $checkedConvert('immediate_action', (v) => v as String?),
      treatment: $checkedConvert('treatment', (v) => v as String?),
      prevention: $checkedConvert('prevention', (v) => v as String?),
      monitoring: $checkedConvert('monitoring', (v) => v as String?),
      safetyDisclaimer: $checkedConvert(
        'safety_disclaimer',
        (v) => v as String?,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'immediateAction': 'immediate_action',
    'safetyDisclaimer': 'safety_disclaimer',
  },
);

Map<String, dynamic> _$PredictionRecommendationResponseToJson(
  PredictionRecommendationResponse instance,
) => <String, dynamic>{
  'immediate_action': ?instance.immediateAction,
  'treatment': ?instance.treatment,
  'prevention': ?instance.prevention,
  'monitoring': ?instance.monitoring,
  'safety_disclaimer': ?instance.safetyDisclaimer,
};
