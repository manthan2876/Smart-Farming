import 'dart:convert';
import 'dart:math';
import 'dart:typed_data';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/sync_queue_item.dart';
import 'api_service.dart';

class SyncService {
  SyncService(this.api);
  final ApiService api;
  static const _queueKey = 'pending_leaf_scans';

  Future<void> enqueueBytes(
    Uint8List bytes,
    String fileName, {
    String location = 'North plot',
    String language = 'English',
    int? plotId,
    double? lat,
    double? lon,
  }) async {
    final preferences = await SharedPreferences.getInstance();
    final queue = preferences.getStringList(_queueKey) ?? [];
    final item = SyncQueueItem(
      createdAt: DateTime.now(),
      location: location,
      language: language,
      fileName: fileName,
      base64Data: base64Encode(bytes),
      plotId: plotId,
      lat: lat,
      lon: lon,
      retryCount: 0,
    );
    queue.add(jsonEncode(item.toJson()));
    await preferences.setStringList(_queueKey, queue);
  }

  Future<int> pendingCount() async =>
      (await SharedPreferences.getInstance()).getStringList(_queueKey)?.length ?? 0;

  Future<List<SyncQueueItem>> getPendingItems() async {
    final preferences = await SharedPreferences.getInstance();
    final raw = preferences.getStringList(_queueKey) ?? [];
    return raw
        .map((s) => SyncQueueItem.fromJson(jsonDecode(s) as Map<String, dynamic>))
        .toList();
  }

  Future<int> drain() async {
    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity.contains(ConnectivityResult.none)) return 0;
    
    final preferences = await SharedPreferences.getInstance();
    final queue = preferences.getStringList(_queueKey) ?? [];
    if (queue.isEmpty) return 0;

    final remaining = <String>[];
    int syncedCount = 0;
    final now = DateTime.now();

    for (final raw in queue) {
      SyncQueueItem item;
      try {
        item = SyncQueueItem.fromJson(jsonDecode(raw) as Map<String, dynamic>);
      } catch (_) {
        continue;
      }

      if (item.base64Data == null || item.base64Data!.isEmpty) {
        continue;
      }

      // Exponential backoff check: delay = min(300, (2 ^ retryCount) * 5) seconds
      if (item.retryCount > 0 && item.lastAttemptAt != null) {
        final backoffSec = min(300, pow(2, item.retryCount).toInt() * 5);
        if (now.difference(item.lastAttemptAt!).inSeconds < backoffSec) {
          // Still in backoff cooldown, preserve in queue for next drain cycle
          remaining.add(raw);
          continue;
        }
      }

      try {
        final bytes = base64Decode(item.base64Data!);
        await api.predictBytes(
          bytes,
          item.fileName,
          location: item.location,
          language: item.language,
          plotId: item.plotId,
          lat: item.lat ?? 21.7645,
          lon: item.lon ?? 72.1519,
        );
        syncedCount++;
      } catch (err) {
        // Record failed attempt with updated retry count and backoff timestamp
        final updated = item.copyWith(
          retryCount: item.retryCount + 1,
          lastAttemptAt: DateTime.now(),
          status: 'retry_pending',
        );
        remaining.add(jsonEncode(updated.toJson()));
      }
    }

    await preferences.setStringList(_queueKey, remaining);
    return syncedCount;
  }
}

