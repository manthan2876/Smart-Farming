import 'package:flutter_test/flutter_test.dart';
import 'package:smart_farming_api/smart_farming_api.dart';

void main() {
  test('generated alert response preserves the API JSON field names', () {
    final alert = AlertResponse.fromJson({
      'id': 11,
      'prediction_id': 22,
      'kind': 'weather',
      'severity': 'high',
      'title': 'Heavy rain',
      'body': 'Check the field.',
      'is_read': false,
      'created_at': '2026-10-22T12:00:00Z',
    });

    expect(alert.id, 11);
    expect(alert.predictionId, 22);
    expect(alert.isRead, isFalse);
    expect(alert.toJson()['created_at'], '2026-10-22T12:00:00.000Z');
  });

  test('generated crop response requires a string crop list', () {
    final response = CropListResponse.fromJson({
      'crops': ['Tomato', 'Cotton'],
    });

    expect(response.crops, ['Tomato', 'Cotton']);
  });

  test('generated prediction and status responses preserve typed API fields', () {
    final prediction = PredictionResponse.fromJson({
      'prediction_id': 37,
      'crop': {'label': 'Cotton', 'confidence': 0.98},
      'status': {
        'pipeline': 'completed',
        'expert_review': 'not_requested',
      },
      'historical_images': [
        {
          'id': 9,
          'disease': 'Leaf blight',
          'severity_pct': 42.5,
          'severity_bucket': 'Moderate',
        },
      ],
    });

    expect(prediction.predictionId, 37);
    expect(prediction.crop?.label, 'Cotton');
    expect(prediction.status?.pipeline, 'completed');
    expect(prediction.status?.expertReview, 'not_requested');
    expect(prediction.historicalImages?.single.severityPct, 42.5);
  });

  test('generated auth, weather, and TTS schemas retain wire keys', () {
    final token = TokenResponse.fromJson({
      'access_token': 'access',
      'refresh_token': 'refresh',
      'token_type': 'bearer',
      'expires_in': 1800,
    });
    final weather = WeatherResponse.fromJson({
      'temperature_celsius': 31.5,
      'humidity_percent': 72,
      'condition': 'Cloudy',
    });
    final speech = TTSResponse.fromJson({
      'audioContent': 'base64-audio',
      'format': 'wav',
      'cached': false,
    });

    expect(token.accessToken, 'access');
    expect(token.expiresIn, 1800);
    expect(weather.temperatureCelsius, 31.5);
    expect(weather.humidityPercent, 72);
    expect(speech.audioContent, 'base64-audio');
    expect(speech.toJson()['audioContent'], 'base64-audio');
  });
}
