// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'recommendation.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$RecommendationCWProxy {
  Recommendation immediateAction(String? immediateAction);

  Recommendation treatment(String? treatment);

  Recommendation prevention(String? prevention);

  Recommendation monitoring(String? monitoring);

  Recommendation safetyDisclaimer(String? safetyDisclaimer);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `Recommendation(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// Recommendation(...).copyWith(id: 12, name: "My name")
  /// ````
  Recommendation call({
    String? immediateAction,
    String? treatment,
    String? prevention,
    String? monitoring,
    String? safetyDisclaimer,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfRecommendation.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfRecommendation.copyWith.fieldName(...)`
class _$RecommendationCWProxyImpl implements _$RecommendationCWProxy {
  const _$RecommendationCWProxyImpl(this._value);

  final Recommendation _value;

  @override
  Recommendation immediateAction(String? immediateAction) =>
      this(immediateAction: immediateAction);

  @override
  Recommendation treatment(String? treatment) => this(treatment: treatment);

  @override
  Recommendation prevention(String? prevention) => this(prevention: prevention);

  @override
  Recommendation monitoring(String? monitoring) => this(monitoring: monitoring);

  @override
  Recommendation safetyDisclaimer(String? safetyDisclaimer) =>
      this(safetyDisclaimer: safetyDisclaimer);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `Recommendation(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// Recommendation(...).copyWith(id: 12, name: "My name")
  /// ````
  Recommendation call({
    Object? immediateAction = const $CopyWithPlaceholder(),
    Object? treatment = const $CopyWithPlaceholder(),
    Object? prevention = const $CopyWithPlaceholder(),
    Object? monitoring = const $CopyWithPlaceholder(),
    Object? safetyDisclaimer = const $CopyWithPlaceholder(),
  }) {
    return Recommendation(
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

extension $RecommendationCopyWith on Recommendation {
  /// Returns a callable class that can be used as follows: `instanceOfRecommendation.copyWith(...)` or like so:`instanceOfRecommendation.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$RecommendationCWProxy get copyWith => _$RecommendationCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Recommendation _$RecommendationFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'Recommendation',
      json,
      ($checkedConvert) {
        final val = Recommendation(
          immediateAction: $checkedConvert(
            'immediate_action',
            (v) => v as String?,
          ),
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

Map<String, dynamic> _$RecommendationToJson(Recommendation instance) =>
    <String, dynamic>{
      'immediate_action': ?instance.immediateAction,
      'treatment': ?instance.treatment,
      'prevention': ?instance.prevention,
      'monitoring': ?instance.monitoring,
      'safety_disclaimer': ?instance.safetyDisclaimer,
    };
