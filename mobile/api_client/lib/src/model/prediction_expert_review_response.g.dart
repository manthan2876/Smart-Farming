// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prediction_expert_review_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PredictionExpertReviewResponseCWProxy {
  PredictionExpertReviewResponse decision(String? decision);

  PredictionExpertReviewResponse correctedDisease(String? correctedDisease);

  PredictionExpertReviewResponse correctedSeverity(num? correctedSeverity);

  PredictionExpertReviewResponse farmerGuidance(String? farmerGuidance);

  PredictionExpertReviewResponse status(String? status);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionExpertReviewResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionExpertReviewResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionExpertReviewResponse call({
    String? decision,
    String? correctedDisease,
    num? correctedSeverity,
    String? farmerGuidance,
    String? status,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPredictionExpertReviewResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPredictionExpertReviewResponse.copyWith.fieldName(...)`
class _$PredictionExpertReviewResponseCWProxyImpl
    implements _$PredictionExpertReviewResponseCWProxy {
  const _$PredictionExpertReviewResponseCWProxyImpl(this._value);

  final PredictionExpertReviewResponse _value;

  @override
  PredictionExpertReviewResponse decision(String? decision) =>
      this(decision: decision);

  @override
  PredictionExpertReviewResponse correctedDisease(String? correctedDisease) =>
      this(correctedDisease: correctedDisease);

  @override
  PredictionExpertReviewResponse correctedSeverity(num? correctedSeverity) =>
      this(correctedSeverity: correctedSeverity);

  @override
  PredictionExpertReviewResponse farmerGuidance(String? farmerGuidance) =>
      this(farmerGuidance: farmerGuidance);

  @override
  PredictionExpertReviewResponse status(String? status) => this(status: status);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionExpertReviewResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionExpertReviewResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionExpertReviewResponse call({
    Object? decision = const $CopyWithPlaceholder(),
    Object? correctedDisease = const $CopyWithPlaceholder(),
    Object? correctedSeverity = const $CopyWithPlaceholder(),
    Object? farmerGuidance = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
  }) {
    return PredictionExpertReviewResponse(
      decision: decision == const $CopyWithPlaceholder()
          ? _value.decision
          // ignore: cast_nullable_to_non_nullable
          : decision as String?,
      correctedDisease: correctedDisease == const $CopyWithPlaceholder()
          ? _value.correctedDisease
          // ignore: cast_nullable_to_non_nullable
          : correctedDisease as String?,
      correctedSeverity: correctedSeverity == const $CopyWithPlaceholder()
          ? _value.correctedSeverity
          // ignore: cast_nullable_to_non_nullable
          : correctedSeverity as num?,
      farmerGuidance: farmerGuidance == const $CopyWithPlaceholder()
          ? _value.farmerGuidance
          // ignore: cast_nullable_to_non_nullable
          : farmerGuidance as String?,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String?,
    );
  }
}

extension $PredictionExpertReviewResponseCopyWith
    on PredictionExpertReviewResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPredictionExpertReviewResponse.copyWith(...)` or like so:`instanceOfPredictionExpertReviewResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PredictionExpertReviewResponseCWProxy get copyWith =>
      _$PredictionExpertReviewResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PredictionExpertReviewResponse _$PredictionExpertReviewResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'PredictionExpertReviewResponse',
  json,
  ($checkedConvert) {
    final val = PredictionExpertReviewResponse(
      decision: $checkedConvert('decision', (v) => v as String?),
      correctedDisease: $checkedConvert(
        'corrected_disease',
        (v) => v as String?,
      ),
      correctedSeverity: $checkedConvert(
        'corrected_severity',
        (v) => v as num?,
      ),
      farmerGuidance: $checkedConvert('farmer_guidance', (v) => v as String?),
      status: $checkedConvert('status', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'correctedDisease': 'corrected_disease',
    'correctedSeverity': 'corrected_severity',
    'farmerGuidance': 'farmer_guidance',
  },
);

Map<String, dynamic> _$PredictionExpertReviewResponseToJson(
  PredictionExpertReviewResponse instance,
) => <String, dynamic>{
  'decision': ?instance.decision,
  'corrected_disease': ?instance.correctedDisease,
  'corrected_severity': ?instance.correctedSeverity,
  'farmer_guidance': ?instance.farmerGuidance,
  'status': ?instance.status,
};
