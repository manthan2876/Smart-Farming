//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

import 'dart:async';

// ignore: unused_import
import 'dart:convert';
import 'package:smart_farming_api/src/deserialize.dart';
import 'package:dio/dio.dart';

import 'package:smart_farming_api/src/model/prediction_translation_response.dart';

class TranslationApi {
  final Dio _dio;

  const TranslationApi(this._dio);

  /// Translate Prediction Recommendation
  /// Translate the recommendation and expert guidance for a prediction on-demand.  - If requested in English, returns the canonical English recommendation. - If already translated and cached in prediction.result[\&quot;translations\&quot;][lang_code], returns from cache (0 ms). - Otherwise, translates using IndicTrans2 on Colab/GPU server, caches in the database, and returns.
  ///
  /// Parameters:
  /// * [predictionId]
  /// * [targetLanguage] - Target language: 'Hindi', 'Gujarati', 'English', or code 'hi', 'gu', 'en'
  /// * [xUserId]
  /// * [cancelToken] - A [CancelToken] that can be used to cancel the operation
  /// * [headers] - Can be used to add additional headers to the request
  /// * [extras] - Can be used to add flags to the request
  /// * [validateStatus] - A [ValidateStatus] callback that can be used to determine request success based on the HTTP status of the response
  /// * [onSendProgress] - A [ProgressCallback] that can be used to get the send progress
  /// * [onReceiveProgress] - A [ProgressCallback] that can be used to get the receive progress
  ///
  /// Returns a [Future] containing a [Response] with a [PredictionTranslationResponse] as data
  /// Throws [DioException] if API call or serialization fails
  Future<Response<PredictionTranslationResponse>>
  translatePredictionRecommendationApiV1PredictionsPredictionIdTranslatePost({
    required int predictionId,
    required String targetLanguage,
    String? xUserId,
    CancelToken? cancelToken,
    Map<String, dynamic>? headers,
    Map<String, dynamic>? extra,
    ValidateStatus? validateStatus,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    final _path = r'/api/v1/predictions/{prediction_id}/translate'.replaceAll(
      '{'
      r'prediction_id'
      '}',
      predictionId.toString(),
    );
    final _options = Options(
      method: r'POST',
      headers: <String, dynamic>{r'x-user-id': xUserId, ...?headers},
      extra: <String, dynamic>{
        'secure': <Map<String, String>>[
          {'type': 'http', 'scheme': 'bearer', 'name': 'HTTPBearer'},
        ],
        ...?extra,
      },
      validateStatus: validateStatus,
    );

    final _queryParameters = <String, dynamic>{
      r'target_language': targetLanguage,
    };

    final _response = await _dio.request<Object>(
      _path,
      options: _options,
      queryParameters: _queryParameters,
      cancelToken: cancelToken,
      onSendProgress: onSendProgress,
      onReceiveProgress: onReceiveProgress,
    );

    PredictionTranslationResponse? _responseData;

    try {
      final rawData = _response.data;
      _responseData = rawData == null
          ? null
          : deserialize<
              PredictionTranslationResponse,
              PredictionTranslationResponse
            >(rawData, 'PredictionTranslationResponse', growable: true);
    } catch (error, stackTrace) {
      throw DioException(
        requestOptions: _response.requestOptions,
        response: _response,
        type: DioExceptionType.unknown,
        error: error,
        stackTrace: stackTrace,
      );
    }

    return Response<PredictionTranslationResponse>(
      data: _responseData,
      headers: _response.headers,
      isRedirect: _response.isRedirect,
      requestOptions: _response.requestOptions,
      redirects: _response.redirects,
      statusCode: _response.statusCode,
      statusMessage: _response.statusMessage,
      extra: _response.extra,
    );
  }
}
