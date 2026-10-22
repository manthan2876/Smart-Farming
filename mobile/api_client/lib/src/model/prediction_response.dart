//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:smart_farming_api/src/model/prediction_image_response.dart';
import 'package:smart_farming_api/src/model/prediction_recommendation_response.dart';
import 'package:smart_farming_api/src/model/prediction_severity_response.dart';
import 'package:smart_farming_api/src/model/prediction_historical_image_response.dart';
import 'package:smart_farming_api/src/model/recommendation.dart';
import 'package:smart_farming_api/src/model/prediction_weather_response.dart';
import 'package:smart_farming_api/src/model/prediction_status_response.dart';
import 'package:smart_farming_api/src/model/prediction_expert_review_response.dart';
import 'package:smart_farming_api/src/model/prediction_label_response.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'prediction_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PredictionResponse {
  /// Returns a new [PredictionResponse] instance.
  PredictionResponse({
    this.predictionId,

    this.id,

    this.createdAt,

    this.jobId,

    this.requestId,

    this.user,

    this.image,

    this.crop,

    this.disease,

    this.severity,

    this.pests,

    this.pestClassification,

    this.weather,

    this.recommendation,

    this.notes,

    this.status,

    this.error,

    this.stages,

    this.schemaVersion,

    this.provenance,

    this.totalDurationMs,

    this.expertReviewData,

    this.historicalImages,

    this.followUp,

    this.translations,

    this.treatmentProgress,

    this.farm,

    this.plot,
  });

  @JsonKey(name: r'prediction_id', required: false, includeIfNull: false)
  final int? predictionId;

  @JsonKey(name: r'id', required: false, includeIfNull: false)
  final int? id;

  @JsonKey(name: r'created_at', required: false, includeIfNull: false)
  final String? createdAt;

  @JsonKey(name: r'job_id', required: false, includeIfNull: false)
  final String? jobId;

  @JsonKey(name: r'request_id', required: false, includeIfNull: false)
  final String? requestId;

  @JsonKey(name: r'user', required: false, includeIfNull: false)
  final Map<String, Object>? user;

  @JsonKey(name: r'image', required: false, includeIfNull: false)
  final PredictionImageResponse? image;

  @JsonKey(name: r'crop', required: false, includeIfNull: false)
  final PredictionLabelResponse? crop;

  @JsonKey(name: r'disease', required: false, includeIfNull: false)
  final PredictionLabelResponse? disease;

  @JsonKey(name: r'severity', required: false, includeIfNull: false)
  final PredictionSeverityResponse? severity;

  @JsonKey(name: r'pests', required: false, includeIfNull: false)
  final List<PredictionLabelResponse>? pests;

  @JsonKey(name: r'pest_classification', required: false, includeIfNull: false)
  final Map<String, Object>? pestClassification;

  @JsonKey(name: r'weather', required: false, includeIfNull: false)
  final PredictionWeatherResponse? weather;

  @JsonKey(name: r'recommendation', required: false, includeIfNull: false)
  final Recommendation? recommendation;

  @JsonKey(name: r'notes', required: false, includeIfNull: false)
  final List<String>? notes;

  @JsonKey(name: r'status', required: false, includeIfNull: false)
  final PredictionStatusResponse? status;

  @JsonKey(name: r'error', required: false, includeIfNull: false)
  final String? error;

  @JsonKey(name: r'stages', required: false, includeIfNull: false)
  final Map<String, Object>? stages;

  @JsonKey(name: r'schema_version', required: false, includeIfNull: false)
  final String? schemaVersion;

  @JsonKey(name: r'provenance', required: false, includeIfNull: false)
  final Map<String, Object>? provenance;

  @JsonKey(name: r'total_duration_ms', required: false, includeIfNull: false)
  final int? totalDurationMs;

  @JsonKey(name: r'expert_review_data', required: false, includeIfNull: false)
  final PredictionExpertReviewResponse? expertReviewData;

  @JsonKey(name: r'historical_images', required: false, includeIfNull: false)
  final List<PredictionHistoricalImageResponse>? historicalImages;

  @JsonKey(name: r'follow_up', required: false, includeIfNull: false)
  final PredictionResponse? followUp;

  @JsonKey(name: r'translations', required: false, includeIfNull: false)
  final Map<String, PredictionRecommendationResponse>? translations;

  @JsonKey(name: r'treatment_progress', required: false, includeIfNull: false)
  final Map<String, Object>? treatmentProgress;

  @JsonKey(name: r'farm', required: false, includeIfNull: false)
  final Map<String, Object>? farm;

  @JsonKey(name: r'plot', required: false, includeIfNull: false)
  final Map<String, Object>? plot;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PredictionResponse &&
          other.predictionId == predictionId &&
          other.id == id &&
          other.createdAt == createdAt &&
          other.jobId == jobId &&
          other.requestId == requestId &&
          other.user == user &&
          other.image == image &&
          other.crop == crop &&
          other.disease == disease &&
          other.severity == severity &&
          other.pests == pests &&
          other.pestClassification == pestClassification &&
          other.weather == weather &&
          other.recommendation == recommendation &&
          other.notes == notes &&
          other.status == status &&
          other.error == error &&
          other.stages == stages &&
          other.schemaVersion == schemaVersion &&
          other.provenance == provenance &&
          other.totalDurationMs == totalDurationMs &&
          other.expertReviewData == expertReviewData &&
          other.historicalImages == historicalImages &&
          other.followUp == followUp &&
          other.translations == translations &&
          other.treatmentProgress == treatmentProgress &&
          other.farm == farm &&
          other.plot == plot;

  @override
  int get hashCode =>
      (predictionId == null ? 0 : predictionId.hashCode) +
      (id == null ? 0 : id.hashCode) +
      (createdAt == null ? 0 : createdAt.hashCode) +
      (jobId == null ? 0 : jobId.hashCode) +
      (requestId == null ? 0 : requestId.hashCode) +
      (user == null ? 0 : user.hashCode) +
      (image == null ? 0 : image.hashCode) +
      (crop == null ? 0 : crop.hashCode) +
      (disease == null ? 0 : disease.hashCode) +
      (severity == null ? 0 : severity.hashCode) +
      (pests == null ? 0 : pests.hashCode) +
      (pestClassification == null ? 0 : pestClassification.hashCode) +
      (weather == null ? 0 : weather.hashCode) +
      (recommendation == null ? 0 : recommendation.hashCode) +
      (notes == null ? 0 : notes.hashCode) +
      (status == null ? 0 : status.hashCode) +
      (error == null ? 0 : error.hashCode) +
      (stages == null ? 0 : stages.hashCode) +
      (schemaVersion == null ? 0 : schemaVersion.hashCode) +
      (provenance == null ? 0 : provenance.hashCode) +
      (totalDurationMs == null ? 0 : totalDurationMs.hashCode) +
      (expertReviewData == null ? 0 : expertReviewData.hashCode) +
      (historicalImages == null ? 0 : historicalImages.hashCode) +
      (followUp == null ? 0 : followUp.hashCode) +
      (translations == null ? 0 : translations.hashCode) +
      (treatmentProgress == null ? 0 : treatmentProgress.hashCode) +
      (farm == null ? 0 : farm.hashCode) +
      (plot == null ? 0 : plot.hashCode);

  factory PredictionResponse.fromJson(Map<String, dynamic> json) =>
      _$PredictionResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PredictionResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
