import 'package:smart_farming_api/src/model/alert_read_response.dart';
import 'package:smart_farming_api/src/model/alert_response.dart';
import 'package:smart_farming_api/src/model/auth_response.dart';
import 'package:smart_farming_api/src/model/change_password_request.dart';
import 'package:smart_farming_api/src/model/crop_list_response.dart';
import 'package:smart_farming_api/src/model/error_response.dart';
import 'package:smart_farming_api/src/model/farm_request.dart';
import 'package:smart_farming_api/src/model/farm_response.dart';
import 'package:smart_farming_api/src/model/feedback_request.dart';
import 'package:smart_farming_api/src/model/feedback_response.dart';
import 'package:smart_farming_api/src/model/forgot_password_request.dart';
import 'package:smart_farming_api/src/model/login_request.dart';
import 'package:smart_farming_api/src/model/message_response.dart';
import 'package:smart_farming_api/src/model/plot_request.dart';
import 'package:smart_farming_api/src/model/plot_response.dart';
import 'package:smart_farming_api/src/model/prediction_expert_review_response.dart';
import 'package:smart_farming_api/src/model/prediction_historical_image_response.dart';
import 'package:smart_farming_api/src/model/prediction_image_response.dart';
import 'package:smart_farming_api/src/model/prediction_label_response.dart';
import 'package:smart_farming_api/src/model/prediction_recommendation_response.dart';
import 'package:smart_farming_api/src/model/prediction_response.dart';
import 'package:smart_farming_api/src/model/prediction_severity_response.dart';
import 'package:smart_farming_api/src/model/prediction_status_response.dart';
import 'package:smart_farming_api/src/model/prediction_translation_response.dart';
import 'package:smart_farming_api/src/model/prediction_weather_response.dart';
import 'package:smart_farming_api/src/model/profile_response.dart';
import 'package:smart_farming_api/src/model/profile_update_request.dart';
import 'package:smart_farming_api/src/model/recommendation.dart';
import 'package:smart_farming_api/src/model/refresh_request.dart';
import 'package:smart_farming_api/src/model/register_request.dart';
import 'package:smart_farming_api/src/model/reset_password_request.dart';
import 'package:smart_farming_api/src/model/tts_request.dart';
import 'package:smart_farming_api/src/model/tts_response.dart';
import 'package:smart_farming_api/src/model/token_response.dart';
import 'package:smart_farming_api/src/model/weather_response.dart';
import 'package:smart_farming_api/src/model/weather_translation_request.dart';
import 'package:smart_farming_api/src/model/weather_translation_response.dart';

final _regList = RegExp(r'^List<(.*)>$');
final _regSet = RegExp(r'^Set<(.*)>$');
final _regMap = RegExp(r'^Map<String,(.*)>$');

ReturnType deserialize<ReturnType, BaseType>(
  dynamic value,
  String targetType, {
  bool growable = true,
}) {
  switch (targetType) {
    case 'String':
      return '$value' as ReturnType;
    case 'int':
      return (value is int ? value : int.parse('$value')) as ReturnType;
    case 'bool':
      if (value is bool) {
        return value as ReturnType;
      }
      final valueString = '$value'.toLowerCase();
      return (valueString == 'true' || valueString == '1') as ReturnType;
    case 'double':
      return (value is double ? value : double.parse('$value')) as ReturnType;
    case 'AlertReadResponse':
      return AlertReadResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'AlertResponse':
      return AlertResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'AuthResponse':
      return AuthResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
    case 'ChangePasswordRequest':
      return ChangePasswordRequest.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'CropListResponse':
      return CropListResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'ErrorResponse':
      return ErrorResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'FarmRequest':
      return FarmRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
    case 'FarmResponse':
      return FarmResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
    case 'FeedbackRequest':
      return FeedbackRequest.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'FeedbackResponse':
      return FeedbackResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'ForgotPasswordRequest':
      return ForgotPasswordRequest.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'LoginRequest':
      return LoginRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
    case 'MessageResponse':
      return MessageResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'PlotRequest':
      return PlotRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
    case 'PlotResponse':
      return PlotResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
    case 'PredictionExpertReviewResponse':
      return PredictionExpertReviewResponse.fromJson(
            value as Map<String, dynamic>,
          )
          as ReturnType;
    case 'PredictionHistoricalImageResponse':
      return PredictionHistoricalImageResponse.fromJson(
            value as Map<String, dynamic>,
          )
          as ReturnType;
    case 'PredictionImageResponse':
      return PredictionImageResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'PredictionLabelResponse':
      return PredictionLabelResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'PredictionRecommendationResponse':
      return PredictionRecommendationResponse.fromJson(
            value as Map<String, dynamic>,
          )
          as ReturnType;
    case 'PredictionResponse':
      return PredictionResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'PredictionSeverityResponse':
      return PredictionSeverityResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'PredictionStatusResponse':
      return PredictionStatusResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'PredictionTranslationResponse':
      return PredictionTranslationResponse.fromJson(
            value as Map<String, dynamic>,
          )
          as ReturnType;
    case 'PredictionWeatherResponse':
      return PredictionWeatherResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'ProfileResponse':
      return ProfileResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'ProfileUpdateRequest':
      return ProfileUpdateRequest.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'Recommendation':
      return Recommendation.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'RefreshRequest':
      return RefreshRequest.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'RegisterRequest':
      return RegisterRequest.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'ResetPasswordRequest':
      return ResetPasswordRequest.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'TTSRequest':
      return TTSRequest.fromJson(value as Map<String, dynamic>) as ReturnType;
    case 'TTSResponse':
      return TTSResponse.fromJson(value as Map<String, dynamic>) as ReturnType;
    case 'TokenResponse':
      return TokenResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'WeatherResponse':
      return WeatherResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'WeatherTranslationRequest':
      return WeatherTranslationRequest.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    case 'WeatherTranslationResponse':
      return WeatherTranslationResponse.fromJson(value as Map<String, dynamic>)
          as ReturnType;
    default:
      RegExpMatch? match;

      if (value is List && (match = _regList.firstMatch(targetType)) != null) {
        targetType = match![1]!; // ignore: parameter_assignments
        return value
                .map<BaseType>(
                  (dynamic v) => deserialize<BaseType, BaseType>(
                    v,
                    targetType,
                    growable: growable,
                  ),
                )
                .toList(growable: growable)
            as ReturnType;
      }
      if (value is Set && (match = _regSet.firstMatch(targetType)) != null) {
        targetType = match![1]!; // ignore: parameter_assignments
        return value
                .map<BaseType>(
                  (dynamic v) => deserialize<BaseType, BaseType>(
                    v,
                    targetType,
                    growable: growable,
                  ),
                )
                .toSet()
            as ReturnType;
      }
      if (value is Map && (match = _regMap.firstMatch(targetType)) != null) {
        targetType = match![1]!.trim(); // ignore: parameter_assignments
        return Map<String, BaseType>.fromIterables(
              value.keys as Iterable<String>,
              value.values.map(
                (dynamic v) => deserialize<BaseType, BaseType>(
                  v,
                  targetType,
                  growable: growable,
                ),
              ),
            )
            as ReturnType;
      }
      break;
  }
  throw Exception('Cannot deserialize');
}
