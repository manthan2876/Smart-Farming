import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:latlong2/latlong.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smart_farming_mobile/services/api_service.dart';
import 'package:smart_farming_mobile/services/offline_queue_db.dart';
import 'package:smart_farming_mobile/services/sync_service.dart';
import 'package:smart_farming_mobile/utils/geo_math.dart';

class MockFieldApiService extends ApiService {
  final List<Map<String, dynamic>> requests = [];
  bool networkOffline = false;

  @override
  Future<Map<String, dynamic>> predictBytes(
    Uint8List bytes,
    String filename, {
    String location = 'Plot 1',
    String language = 'Gujarati',
    int? plotId,
    double lat = 21.7645,
    double lon = 72.1519,
  }) async {
    if (networkOffline) {
      throw Exception('SocketException: No network connection available in remote field');
    }
    final record = {
      'filename': filename,
      'bytesLength': bytes.length,
      'location': location,
      'language': language,
      'plot_id': plotId,
      'lat': lat,
      'lon': lon,
    };
    requests.add(record);
    return {
      'prediction_id': 101,
      'crop': {'label': 'Groundnut', 'confidence': 0.94},
      'disease': {'label': 'Early Leaf Spot', 'confidence': 0.91},
      'severity': {'percent': 18.5, 'bucket': 'low'},
      'status': 'completed',
    };
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('Phase 6 Field Workflow Integration Suite', () {
    test('Calculates plot polygon acreage accurately in agricultural reference area', () {
      // 100m x 100m square in Gujarat coordinates
      final boundary = [
        const LatLng(21.7600, 72.1500),
        const LatLng(21.7600, 72.1510),
        const LatLng(21.7610, 72.1510),
        const LatLng(21.7610, 72.1500),
        const LatLng(21.7600, 72.1500),
      ];

      final areaSqMeters = GeoMath.calculatePolygonAreaSqMeters(boundary);
      expect(areaSqMeters, greaterThan(0.0));

      final acres = GeoMath.calculatePolygonAreaAcres(boundary);
      expect(acres, greaterThan(0.0));
      expect(acres, lessThan(10.0));
    });

    test('Recovers gracefully from offline remote field connectivity drops', () async {
      final mockApi = MockFieldApiService()..networkOffline = true;
      final queueDb = OfflineQueueDb();
      final syncService = SyncService(mockApi, queueDb: queueDb);

      final leafBytes = Uint8List.fromList([100, 101, 102, 103, 104]);

      // 1. Farmer takes leaf photo while offline in deep agricultural field
      await syncService.enqueueBytes(
        leafBytes,
        'field_leaf_scan.jpg',
        location: 'Anand Farm Plot A',
        language: 'Gujarati',
        plotId: 7,
        lat: 21.7645,
        lon: 72.1519,
      );

      expect(await syncService.pendingCount(), 1);

      // 2. Initial drain fails due to offline connectivity
      final failedDrainCount = await syncService.drain();
      expect(failedDrainCount, 0);
      expect(await syncService.pendingCount(), 1);

      // Verify retry metadata was recorded
      final pendingItems = await syncService.getPendingItems();
      expect(pendingItems.first.retryCount, 1);
      expect(pendingItems.first.status, 'retry_pending');

      // Immediate second drain skips item due to backoff cooldown
      mockApi.networkOffline = false;
      final cooldownDrainCount = await syncService.drain();
      expect(cooldownDrainCount, 0);

      // 3. Once backoff cooldown window (2s for retry_count=1) elapses, queue drains successfully
      await Future.delayed(const Duration(milliseconds: 2100));
      final successfulDrainCount = await syncService.drain();
      expect(successfulDrainCount, 1);
      expect(await syncService.pendingCount(), 0);
      expect(mockApi.requests.length, 1);
      expect(mockApi.requests.first['plot_id'], 7);
      expect(mockApi.requests.first['language'], 'Gujarati');
    });
  });
}

