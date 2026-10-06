import 'dart:async';
import 'dart:typed_data';
import 'package:connectivity_plus/connectivity_plus.dart';
import '../models/sync_queue_item.dart';
import 'api_service.dart';
import 'offline_queue_db.dart';

class SyncService {
  SyncService(this.api, {OfflineQueueDb? queueDb, Connectivity? connectivity})
      : _queueDb = queueDb ?? OfflineQueueDb(),
        _connectivity = connectivity ?? Connectivity();

  final ApiService api;
  final OfflineQueueDb _queueDb;
  final Connectivity _connectivity;

  Future<void> enqueueBytes(
    Uint8List bytes,
    String fileName, {
    String location = 'North plot',
    String language = 'English',
    int? plotId,
    double? lat,
    double? lon,
  }) async {
    await _queueDb.enqueue(
      bytes,
      fileName,
      location: location,
      language: language,
      plotId: plotId,
      lat: lat,
      lon: lon,
    );
  }

  Future<int> pendingCount() async => await _queueDb.pendingCount();

  Future<List<SyncQueueItem>> getPendingItems() async => await _queueDb.getAllItems();

  Future<int> drain() async {
    try {
      final connectivity = await _connectivity.checkConnectivity();
      if (connectivity.contains(ConnectivityResult.none)) return 0;
    } catch (_) {
      // If connectivity check fails or in test/headless runner, proceed to attempt drain
    }

    final itemsToSync = await _queueDb.getItemsToSync();
    if (itemsToSync.isEmpty) return 0;

    int syncedCount = 0;

    for (final item in itemsToSync) {
      if (item.id == null) continue;

      // Mark syncing to guard against concurrent drain loops
      await _queueDb.markSyncing(item.id!);

      final bytes = await _queueDb.readItemImageBytes(item);
      if (bytes == null || bytes.isEmpty) {
        // Unreadable or corrupt image file, delete from queue
        await _queueDb.deleteItem(item.id!, imageFilePath: item.imageFilePath);
        continue;
      }

      try {
        await api.predictBytes(
          bytes,
          item.fileName,
          location: item.location,
          language: item.language,
          plotId: item.plotId,
          lat: item.lat ?? 21.7645,
          lon: item.lon ?? 72.1519,
        );
        // Successfully uploaded, delete row and local image file
        await _queueDb.deleteItem(item.id!, imageFilePath: item.imageFilePath);
        syncedCount++;
      } catch (err) {
        // Increment retry count and apply exponential backoff
        await _queueDb.markFailed(item.id!, item.retryCount + 1);
      }
    }

    return syncedCount;
  }
}

