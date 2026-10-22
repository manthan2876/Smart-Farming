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
}
