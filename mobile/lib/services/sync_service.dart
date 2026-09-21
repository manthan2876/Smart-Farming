import 'dart:convert';
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
  }) async {
    final preferences = await SharedPreferences.getInstance();
    final queue = preferences.getStringList(_queueKey) ?? [];
    final item = SyncQueueItem(
      createdAt: DateTime.now(),
      location: location,
      language: language,
      fileName: fileName,
      base64Data: base64Encode(bytes),
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

      try {
        final bytes = base64Decode(item.base64Data!);
        await api.predictBytes(
          bytes,
          item.fileName,
          location: item.location,
          language: item.language,
        );
        syncedCount++;
      } catch (err) {
        remaining.add(raw);
      }
    }

    await preferences.setStringList(_queueKey, remaining);
    return syncedCount;
  }
}
