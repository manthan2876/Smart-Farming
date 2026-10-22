// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prediction_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PredictionResponseCWProxy {
  PredictionResponse predictionId(int? predictionId);

  PredictionResponse id(int? id);

  PredictionResponse createdAt(String? createdAt);

  PredictionResponse jobId(String? jobId);

  PredictionResponse requestId(String? requestId);

  PredictionResponse user(Map<String, Object>? user);

  PredictionResponse image(PredictionImageResponse? image);

  PredictionResponse crop(PredictionLabelResponse? crop);

  PredictionResponse disease(PredictionLabelResponse? disease);

  PredictionResponse severity(PredictionSeverityResponse? severity);

  PredictionResponse pests(List<PredictionLabelResponse>? pests);

  PredictionResponse pestClassification(
    Map<String, Object>? pestClassification,
  );

  PredictionResponse weather(PredictionWeatherResponse? weather);

  PredictionResponse recommendation(Recommendation? recommendation);

  PredictionResponse notes(List<String>? notes);

  PredictionResponse status(PredictionStatusResponse? status);

  PredictionResponse error(String? error);

  PredictionResponse stages(Map<String, Object>? stages);

  PredictionResponse schemaVersion(String? schemaVersion);

  PredictionResponse provenance(Map<String, Object>? provenance);

  PredictionResponse totalDurationMs(int? totalDurationMs);

  PredictionResponse expertReviewData(
    PredictionExpertReviewResponse? expertReviewData,
  );

  PredictionResponse historicalImages(
    List<PredictionHistoricalImageResponse>? historicalImages,
  );

  PredictionResponse followUp(PredictionResponse? followUp);

  PredictionResponse translations(
    Map<String, PredictionRecommendationResponse>? translations,
  );

  PredictionResponse treatmentProgress(Map<String, Object>? treatmentProgress);

  PredictionResponse farm(Map<String, Object>? farm);

  PredictionResponse plot(Map<String, Object>? plot);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionResponse call({
    int? predictionId,
    int? id,
    String? createdAt,
    String? jobId,
    String? requestId,
    Map<String, Object>? user,
    PredictionImageResponse? image,
    PredictionLabelResponse? crop,
    PredictionLabelResponse? disease,
    PredictionSeverityResponse? severity,
    List<PredictionLabelResponse>? pests,
    Map<String, Object>? pestClassification,
    PredictionWeatherResponse? weather,
    Recommendation? recommendation,
    List<String>? notes,
    PredictionStatusResponse? status,
    String? error,
    Map<String, Object>? stages,
    String? schemaVersion,
    Map<String, Object>? provenance,
    int? totalDurationMs,
    PredictionExpertReviewResponse? expertReviewData,
    List<PredictionHistoricalImageResponse>? historicalImages,
    PredictionResponse? followUp,
    Map<String, PredictionRecommendationResponse>? translations,
    Map<String, Object>? treatmentProgress,
    Map<String, Object>? farm,
    Map<String, Object>? plot,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPredictionResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPredictionResponse.copyWith.fieldName(...)`
class _$PredictionResponseCWProxyImpl implements _$PredictionResponseCWProxy {
  const _$PredictionResponseCWProxyImpl(this._value);

  final PredictionResponse _value;

  @override
  PredictionResponse predictionId(int? predictionId) =>
      this(predictionId: predictionId);

  @override
  PredictionResponse id(int? id) => this(id: id);

  @override
  PredictionResponse createdAt(String? createdAt) => this(createdAt: createdAt);

  @override
  PredictionResponse jobId(String? jobId) => this(jobId: jobId);

  @override
  PredictionResponse requestId(String? requestId) => this(requestId: requestId);

  @override
  PredictionResponse user(Map<String, Object>? user) => this(user: user);

  @override
  PredictionResponse image(PredictionImageResponse? image) =>
      this(image: image);

  @override
  PredictionResponse crop(PredictionLabelResponse? crop) => this(crop: crop);

  @override
  PredictionResponse disease(PredictionLabelResponse? disease) =>
      this(disease: disease);

  @override
  PredictionResponse severity(PredictionSeverityResponse? severity) =>
      this(severity: severity);

  @override
  PredictionResponse pests(List<PredictionLabelResponse>? pests) =>
      this(pests: pests);

  @override
  PredictionResponse pestClassification(
    Map<String, Object>? pestClassification,
  ) => this(pestClassification: pestClassification);

  @override
  PredictionResponse weather(PredictionWeatherResponse? weather) =>
      this(weather: weather);

  @override
  PredictionResponse recommendation(Recommendation? recommendation) =>
      this(recommendation: recommendation);

  @override
  PredictionResponse notes(List<String>? notes) => this(notes: notes);

  @override
  PredictionResponse status(PredictionStatusResponse? status) =>
      this(status: status);

  @override
  PredictionResponse error(String? error) => this(error: error);

  @override
  PredictionResponse stages(Map<String, Object>? stages) =>
      this(stages: stages);

  @override
  PredictionResponse schemaVersion(String? schemaVersion) =>
      this(schemaVersion: schemaVersion);

  @override
  PredictionResponse provenance(Map<String, Object>? provenance) =>
      this(provenance: provenance);

  @override
  PredictionResponse totalDurationMs(int? totalDurationMs) =>
      this(totalDurationMs: totalDurationMs);

  @override
  PredictionResponse expertReviewData(
    PredictionExpertReviewResponse? expertReviewData,
  ) => this(expertReviewData: expertReviewData);

  @override
  PredictionResponse historicalImages(
    List<PredictionHistoricalImageResponse>? historicalImages,
  ) => this(historicalImages: historicalImages);

  @override
  PredictionResponse followUp(PredictionResponse? followUp) =>
      this(followUp: followUp);

  @override
  PredictionResponse translations(
    Map<String, PredictionRecommendationResponse>? translations,
  ) => this(translations: translations);

  @override
  PredictionResponse treatmentProgress(
    Map<String, Object>? treatmentProgress,
  ) => this(treatmentProgress: treatmentProgress);

  @override
  PredictionResponse farm(Map<String, Object>? farm) => this(farm: farm);

  @override
  PredictionResponse plot(Map<String, Object>? plot) => this(plot: plot);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionResponse call({
    Object? predictionId = const $CopyWithPlaceholder(),
    Object? id = const $CopyWithPlaceholder(),
    Object? createdAt = const $CopyWithPlaceholder(),
    Object? jobId = const $CopyWithPlaceholder(),
    Object? requestId = const $CopyWithPlaceholder(),
    Object? user = const $CopyWithPlaceholder(),
    Object? image = const $CopyWithPlaceholder(),
    Object? crop = const $CopyWithPlaceholder(),
    Object? disease = const $CopyWithPlaceholder(),
    Object? severity = const $CopyWithPlaceholder(),
    Object? pests = const $CopyWithPlaceholder(),
    Object? pestClassification = const $CopyWithPlaceholder(),
    Object? weather = const $CopyWithPlaceholder(),
    Object? recommendation = const $CopyWithPlaceholder(),
    Object? notes = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? error = const $CopyWithPlaceholder(),
    Object? stages = const $CopyWithPlaceholder(),
    Object? schemaVersion = const $CopyWithPlaceholder(),
    Object? provenance = const $CopyWithPlaceholder(),
    Object? totalDurationMs = const $CopyWithPlaceholder(),
    Object? expertReviewData = const $CopyWithPlaceholder(),
    Object? historicalImages = const $CopyWithPlaceholder(),
    Object? followUp = const $CopyWithPlaceholder(),
    Object? translations = const $CopyWithPlaceholder(),
    Object? treatmentProgress = const $CopyWithPlaceholder(),
    Object? farm = const $CopyWithPlaceholder(),
    Object? plot = const $CopyWithPlaceholder(),
  }) {
    return PredictionResponse(
      predictionId: predictionId == const $CopyWithPlaceholder()
          ? _value.predictionId
          // ignore: cast_nullable_to_non_nullable
          : predictionId as int?,
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as int?,
      createdAt: createdAt == const $CopyWithPlaceholder()
          ? _value.createdAt
          // ignore: cast_nullable_to_non_nullable
          : createdAt as String?,
      jobId: jobId == const $CopyWithPlaceholder()
          ? _value.jobId
          // ignore: cast_nullable_to_non_nullable
          : jobId as String?,
      requestId: requestId == const $CopyWithPlaceholder()
          ? _value.requestId
          // ignore: cast_nullable_to_non_nullable
          : requestId as String?,
      user: user == const $CopyWithPlaceholder()
          ? _value.user
          // ignore: cast_nullable_to_non_nullable
          : user as Map<String, Object>?,
      image: image == const $CopyWithPlaceholder()
          ? _value.image
          // ignore: cast_nullable_to_non_nullable
          : image as PredictionImageResponse?,
      crop: crop == const $CopyWithPlaceholder()
          ? _value.crop
          // ignore: cast_nullable_to_non_nullable
          : crop as PredictionLabelResponse?,
      disease: disease == const $CopyWithPlaceholder()
          ? _value.disease
          // ignore: cast_nullable_to_non_nullable
          : disease as PredictionLabelResponse?,
      severity: severity == const $CopyWithPlaceholder()
          ? _value.severity
          // ignore: cast_nullable_to_non_nullable
          : severity as PredictionSeverityResponse?,
      pests: pests == const $CopyWithPlaceholder()
          ? _value.pests
          // ignore: cast_nullable_to_non_nullable
          : pests as List<PredictionLabelResponse>?,
      pestClassification: pestClassification == const $CopyWithPlaceholder()
          ? _value.pestClassification
          // ignore: cast_nullable_to_non_nullable
          : pestClassification as Map<String, Object>?,
      weather: weather == const $CopyWithPlaceholder()
          ? _value.weather
          // ignore: cast_nullable_to_non_nullable
          : weather as PredictionWeatherResponse?,
      recommendation: recommendation == const $CopyWithPlaceholder()
          ? _value.recommendation
          // ignore: cast_nullable_to_non_nullable
          : recommendation as Recommendation?,
      notes: notes == const $CopyWithPlaceholder()
          ? _value.notes
          // ignore: cast_nullable_to_non_nullable
          : notes as List<String>?,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as PredictionStatusResponse?,
      error: error == const $CopyWithPlaceholder()
          ? _value.error
          // ignore: cast_nullable_to_non_nullable
          : error as String?,
      stages: stages == const $CopyWithPlaceholder()
          ? _value.stages
          // ignore: cast_nullable_to_non_nullable
          : stages as Map<String, Object>?,
      schemaVersion: schemaVersion == const $CopyWithPlaceholder()
          ? _value.schemaVersion
          // ignore: cast_nullable_to_non_nullable
          : schemaVersion as String?,
      provenance: provenance == const $CopyWithPlaceholder()
          ? _value.provenance
          // ignore: cast_nullable_to_non_nullable
          : provenance as Map<String, Object>?,
      totalDurationMs: totalDurationMs == const $CopyWithPlaceholder()
          ? _value.totalDurationMs
          // ignore: cast_nullable_to_non_nullable
          : totalDurationMs as int?,
      expertReviewData: expertReviewData == const $CopyWithPlaceholder()
          ? _value.expertReviewData
          // ignore: cast_nullable_to_non_nullable
          : expertReviewData as PredictionExpertReviewResponse?,
      historicalImages: historicalImages == const $CopyWithPlaceholder()
          ? _value.historicalImages
          // ignore: cast_nullable_to_non_nullable
          : historicalImages as List<PredictionHistoricalImageResponse>?,
      followUp: followUp == const $CopyWithPlaceholder()
          ? _value.followUp
          // ignore: cast_nullable_to_non_nullable
          : followUp as PredictionResponse?,
      translations: translations == const $CopyWithPlaceholder()
          ? _value.translations
          // ignore: cast_nullable_to_non_nullable
          : translations as Map<String, PredictionRecommendationResponse>?,
      treatmentProgress: treatmentProgress == const $CopyWithPlaceholder()
          ? _value.treatmentProgress
          // ignore: cast_nullable_to_non_nullable
          : treatmentProgress as Map<String, Object>?,
      farm: farm == const $CopyWithPlaceholder()
          ? _value.farm
          // ignore: cast_nullable_to_non_nullable
          : farm as Map<String, Object>?,
      plot: plot == const $CopyWithPlaceholder()
          ? _value.plot
          // ignore: cast_nullable_to_non_nullable
          : plot as Map<String, Object>?,
    );
  }
}

extension $PredictionResponseCopyWith on PredictionResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPredictionResponse.copyWith(...)` or like so:`instanceOfPredictionResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PredictionResponseCWProxy get copyWith =>
      _$PredictionResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PredictionResponse _$PredictionResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'PredictionResponse',
  json,
  ($checkedConvert) {
    final val = PredictionResponse(
      predictionId: $checkedConvert(
        'prediction_id',
        (v) => (v as num?)?.toInt(),
      ),
      id: $checkedConvert('id', (v) => (v as num?)?.toInt()),
      createdAt: $checkedConvert('created_at', (v) => v as String?),
      jobId: $checkedConvert('job_id', (v) => v as String?),
      requestId: $checkedConvert('request_id', (v) => v as String?),
      user: $checkedConvert(
        'user',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      image: $checkedConvert(
        'image',
        (v) => v == null
            ? null
            : PredictionImageResponse.fromJson(v as Map<String, dynamic>),
      ),
      crop: $checkedConvert(
        'crop',
        (v) => v == null
            ? null
            : PredictionLabelResponse.fromJson(v as Map<String, dynamic>),
      ),
      disease: $checkedConvert(
        'disease',
        (v) => v == null
            ? null
            : PredictionLabelResponse.fromJson(v as Map<String, dynamic>),
      ),
      severity: $checkedConvert(
        'severity',
        (v) => v == null
            ? null
            : PredictionSeverityResponse.fromJson(v as Map<String, dynamic>),
      ),
      pests: $checkedConvert(
        'pests',
        (v) => (v as List<dynamic>?)
            ?.map(
              (e) =>
                  PredictionLabelResponse.fromJson(e as Map<String, dynamic>),
            )
            .toList(),
      ),
      pestClassification: $checkedConvert(
        'pest_classification',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      weather: $checkedConvert(
        'weather',
        (v) => v == null
            ? null
            : PredictionWeatherResponse.fromJson(v as Map<String, dynamic>),
      ),
      recommendation: $checkedConvert(
        'recommendation',
        (v) => v == null
            ? null
            : Recommendation.fromJson(v as Map<String, dynamic>),
      ),
      notes: $checkedConvert(
        'notes',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
      ),
      status: $checkedConvert(
        'status',
        (v) => v == null
            ? null
            : PredictionStatusResponse.fromJson(v as Map<String, dynamic>),
      ),
      error: $checkedConvert('error', (v) => v as String?),
      stages: $checkedConvert(
        'stages',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      schemaVersion: $checkedConvert('schema_version', (v) => v as String?),
      provenance: $checkedConvert(
        'provenance',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      totalDurationMs: $checkedConvert(
        'total_duration_ms',
        (v) => (v as num?)?.toInt(),
      ),
      expertReviewData: $checkedConvert(
        'expert_review_data',
        (v) => v == null
            ? null
            : PredictionExpertReviewResponse.fromJson(
                v as Map<String, dynamic>,
              ),
      ),
      historicalImages: $checkedConvert(
        'historical_images',
        (v) => (v as List<dynamic>?)
            ?.map(
              (e) => PredictionHistoricalImageResponse.fromJson(
                e as Map<String, dynamic>,
              ),
            )
            .toList(),
      ),
      followUp: $checkedConvert(
        'follow_up',
        (v) => v == null
            ? null
            : PredictionResponse.fromJson(v as Map<String, dynamic>),
      ),
      translations: $checkedConvert(
        'translations',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(
            k,
            PredictionRecommendationResponse.fromJson(
              e as Map<String, dynamic>,
            ),
          ),
        ),
      ),
      treatmentProgress: $checkedConvert(
        'treatment_progress',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      farm: $checkedConvert(
        'farm',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      plot: $checkedConvert(
        'plot',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'predictionId': 'prediction_id',
    'createdAt': 'created_at',
    'jobId': 'job_id',
    'requestId': 'request_id',
    'pestClassification': 'pest_classification',
    'schemaVersion': 'schema_version',
    'totalDurationMs': 'total_duration_ms',
    'expertReviewData': 'expert_review_data',
    'historicalImages': 'historical_images',
    'followUp': 'follow_up',
    'treatmentProgress': 'treatment_progress',
  },
);

Map<String, dynamic> _$PredictionResponseToJson(PredictionResponse instance) =>
    <String, dynamic>{
      'prediction_id': ?instance.predictionId,
      'id': ?instance.id,
      'created_at': ?instance.createdAt,
      'job_id': ?instance.jobId,
      'request_id': ?instance.requestId,
      'user': ?instance.user,
      'image': ?instance.image?.toJson(),
      'crop': ?instance.crop?.toJson(),
      'disease': ?instance.disease?.toJson(),
      'severity': ?instance.severity?.toJson(),
      'pests': ?instance.pests?.map((e) => e.toJson()).toList(),
      'pest_classification': ?instance.pestClassification,
      'weather': ?instance.weather?.toJson(),
      'recommendation': ?instance.recommendation?.toJson(),
      'notes': ?instance.notes,
      'status': ?instance.status?.toJson(),
      'error': ?instance.error,
      'stages': ?instance.stages,
      'schema_version': ?instance.schemaVersion,
      'provenance': ?instance.provenance,
      'total_duration_ms': ?instance.totalDurationMs,
      'expert_review_data': ?instance.expertReviewData?.toJson(),
      'historical_images': ?instance.historicalImages
          ?.map((e) => e.toJson())
          .toList(),
      'follow_up': ?instance.followUp?.toJson(),
      'translations': ?instance.translations?.map(
        (k, e) => MapEntry(k, e.toJson()),
      ),
      'treatment_progress': ?instance.treatmentProgress,
      'farm': ?instance.farm,
      'plot': ?instance.plot,
    };
