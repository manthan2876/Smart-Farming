import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smart_farming_mobile/models/sync_queue_item.dart';
import 'package:smart_farming_mobile/services/api_service.dart';
import 'package:smart_farming_mobile/services/offline_queue_db.dart';
import 'package:smart_farming_mobile/services/sync_service.dart';

class MockApiService extends ApiService {
  final List<Map<String, dynamic>> uploadedScans = [];
  bool shouldFail = false;

  @override
  Future<Map<String, dynamic>> predictBytes(
    Uint8List bytes,
    String filename, {
    String location = 'North plot',
    String language = 'English',
    int? plotId,
    double lat = 21.7645,
    double lon = 72.1519,
  }) async {
    if (shouldFail) {
      throw Exception('Simulated network drop');
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
    uploadedScans.add(record);
    return {
      'prediction_id': 99,
      'crop': {'label': 'Cotton', 'confidence': 0.95},
      'disease': {'label': 'Bacterial Blight', 'confidence': 0.92},
      'status': 'completed',
    };
  }
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('Offline Queue & SyncService Tests', () {
    test('Enqueues scan with plot_id, lat, lon and drains successfully', () async {
      final mockApi = MockApiService();
      final queueDb = OfflineQueueDb();
      final syncService = SyncService(mockApi, queueDb: queueDb);

      final dummyBytes = Uint8List.fromList([1, 2, 3, 4, 5]);
      await syncService.enqueueBytes(
        dummyBytes,
        'test_leaf.jpg',
        location: 'Field B',
        language: 'Hindi',
        plotId: 42,
        lat: 22.3000,
        lon: 70.8000,
      );

      final pending = await syncService.pendingCount();
      expect(pending, 1);

      final items = await syncService.getPendingItems();
      expect(items.length, 1);
      expect(items.first.plotId, 42);
      expect(items.first.lat, 22.3000);
      expect(items.first.lon, 70.8000);
      expect(items.first.language, 'Hindi');

      // Drain queue
      final drainedCount = await syncService.drain();
      expect(drainedCount, 1);
      expect(mockApi.uploadedScans.length, 1);
      expect(mockApi.uploadedScans.first['plot_id'], 42);
      expect(mockApi.uploadedScans.first['lat'], 22.3000);
      expect(mockApi.uploadedScans.first['lon'], 70.8000);
      expect(mockApi.uploadedScans.first['language'], 'Hindi');

      // After drain, pending count should be 0
      final remaining = await syncService.pendingCount();
      expect(remaining, 0);
    });

    test('Exponential backoff increments on failure without dropping scan', () async {
      final mockApi = MockApiService()..shouldFail = true;
      final queueDb = OfflineQueueDb();
      final syncService = SyncService(mockApi, queueDb: queueDb);

      final dummyBytes = Uint8List.fromList([10, 20, 30]);
      await syncService.enqueueBytes(
        dummyBytes,
        'failing_leaf.jpg',
        plotId: 7,
      );

      expect(await syncService.pendingCount(), 1);

      // Attempt drain with network failure
      final drainedCount = await syncService.drain();
      expect(drainedCount, 0);

      // Check item retry metadata
      final items = await syncService.getPendingItems();
      expect(items.length, 1);
      expect(items.first.retryCount, 1);
      expect(items.first.status, 'retry_pending');
      expect(items.first.lastAttemptAt, isNotNull);

      // Subsequent immediate drain skips item due to backoff cooldown
      final drainedSecondTime = await syncService.drain();
      expect(drainedSecondTime, 0);
    });

    test('SyncQueueItem serialization to/from database map', () {
      final now = DateTime.now();
      final item = SyncQueueItem(
        id: 1,
        clientUuid: 'uuid_12345',
        imageFilePath: '/tmp/leaf.jpg',
        fileName: 'leaf.jpg',
        location: 'Plot 3',
        language: 'Gujarati',
        plotId: 15,
        lat: 21.7645,
        lon: 72.1519,
        status: 'pending',
        retryCount: 2,
        createdAt: now,
      );

      final map = item.toDbMap();
      expect(map['client_uuid'], 'uuid_12345');
      expect(map['plot_id'], 15);
      expect(map['retry_count'], 2);

      final restored = SyncQueueItem.fromDbMap(map);
      expect(restored.clientUuid, 'uuid_12345');
      expect(restored.plotId, 15);
      expect(restored.lat, 21.7645);
      expect(restored.language, 'Gujarati');
      expect(restored.retryCount, 2);
    });
  });
}
