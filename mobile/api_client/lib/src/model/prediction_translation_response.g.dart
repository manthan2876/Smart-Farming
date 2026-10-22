// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prediction_translation_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PredictionTranslationResponseCWProxy {
  PredictionTranslationResponse predictionId(int predictionId);

  PredictionTranslationResponse language(String language);

  PredictionTranslationResponse cached(bool cached);

  PredictionTranslationResponse recommendation(
    Map<String, String> recommendation,
  );

  PredictionTranslationResponse expertGuidance(String? expertGuidance);

  PredictionTranslationResponse translations(
    Map<String, Map<String, String>>? translations,
  );

  PredictionTranslationResponse translationStatus(String? translationStatus);

  PredictionTranslationResponse warning(String? warning);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionTranslationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionTranslationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionTranslationResponse call({
    int predictionId,
    String language,
    bool cached,
    Map<String, String> recommendation,
    String? expertGuidance,
    Map<String, Map<String, String>>? translations,
    String? translationStatus,
    String? warning,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPredictionTranslationResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPredictionTranslationResponse.copyWith.fieldName(...)`
class _$PredictionTranslationResponseCWProxyImpl
    implements _$PredictionTranslationResponseCWProxy {
  const _$PredictionTranslationResponseCWProxyImpl(this._value);

  final PredictionTranslationResponse _value;

  @override
  PredictionTranslationResponse predictionId(int predictionId) =>
      this(predictionId: predictionId);

  @override
  PredictionTranslationResponse language(String language) =>
      this(language: language);

  @override
  PredictionTranslationResponse cached(bool cached) => this(cached: cached);

  @override
  PredictionTranslationResponse recommendation(
    Map<String, String> recommendation,
  ) => this(recommendation: recommendation);

  @override
  PredictionTranslationResponse expertGuidance(String? expertGuidance) =>
      this(expertGuidance: expertGuidance);

  @override
  PredictionTranslationResponse translations(
    Map<String, Map<String, String>>? translations,
  ) => this(translations: translations);

  @override
  PredictionTranslationResponse translationStatus(String? translationStatus) =>
      this(translationStatus: translationStatus);

  @override
  PredictionTranslationResponse warning(String? warning) =>
      this(warning: warning);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionTranslationResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionTranslationResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionTranslationResponse call({
    Object? predictionId = const $CopyWithPlaceholder(),
    Object? language = const $CopyWithPlaceholder(),
    Object? cached = const $CopyWithPlaceholder(),
    Object? recommendation = const $CopyWithPlaceholder(),
    Object? expertGuidance = const $CopyWithPlaceholder(),
    Object? translations = const $CopyWithPlaceholder(),
    Object? translationStatus = const $CopyWithPlaceholder(),
    Object? warning = const $CopyWithPlaceholder(),
  }) {
    return PredictionTranslationResponse(
      predictionId: predictionId == const $CopyWithPlaceholder()
          ? _value.predictionId
          // ignore: cast_nullable_to_non_nullable
          : predictionId as int,
      language: language == const $CopyWithPlaceholder()
          ? _value.language
          // ignore: cast_nullable_to_non_nullable
          : language as String,
      cached: cached == const $CopyWithPlaceholder()
          ? _value.cached
          // ignore: cast_nullable_to_non_nullable
          : cached as bool,
      recommendation: recommendation == const $CopyWithPlaceholder()
          ? _value.recommendation
          // ignore: cast_nullable_to_non_nullable
          : recommendation as Map<String, String>,
      expertGuidance: expertGuidance == const $CopyWithPlaceholder()
          ? _value.expertGuidance
          // ignore: cast_nullable_to_non_nullable
          : expertGuidance as String?,
      translations: translations == const $CopyWithPlaceholder()
          ? _value.translations
          // ignore: cast_nullable_to_non_nullable
          : translations as Map<String, Map<String, String>>?,
      translationStatus: translationStatus == const $CopyWithPlaceholder()
          ? _value.translationStatus
          // ignore: cast_nullable_to_non_nullable
          : translationStatus as String?,
      warning: warning == const $CopyWithPlaceholder()
          ? _value.warning
          // ignore: cast_nullable_to_non_nullable
          : warning as String?,
    );
  }
}

extension $PredictionTranslationResponseCopyWith
    on PredictionTranslationResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPredictionTranslationResponse.copyWith(...)` or like so:`instanceOfPredictionTranslationResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PredictionTranslationResponseCWProxy get copyWith =>
      _$PredictionTranslationResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PredictionTranslationResponse _$PredictionTranslationResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'PredictionTranslationResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const [
        'prediction_id',
        'language',
        'cached',
        'recommendation',
      ],
    );
    final val = PredictionTranslationResponse(
      predictionId: $checkedConvert('prediction_id', (v) => (v as num).toInt()),
      language: $checkedConvert('language', (v) => v as String),
      cached: $checkedConvert('cached', (v) => v as bool),
      recommendation: $checkedConvert(
        'recommendation',
        (v) => Map<String, String>.from(v as Map),
      ),
      expertGuidance: $checkedConvert('expert_guidance', (v) => v as String?),
      translations: $checkedConvert(
        'translations',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, Map<String, String>.from(e as Map)),
        ),
      ),
      translationStatus: $checkedConvert(
        'translation_status',
        (v) => v as String?,
      ),
      warning: $checkedConvert('warning', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'predictionId': 'prediction_id',
    'expertGuidance': 'expert_guidance',
    'translationStatus': 'translation_status',
  },
);

Map<String, dynamic> _$PredictionTranslationResponseToJson(
  PredictionTranslationResponse instance,
) => <String, dynamic>{
  'prediction_id': instance.predictionId,
  'language': instance.language,
  'cached': instance.cached,
  'recommendation': instance.recommendation,
  'expert_guidance': ?instance.expertGuidance,
  'translations': ?instance.translations,
  'translation_status': ?instance.translationStatus,
  'warning': ?instance.warning,
};
