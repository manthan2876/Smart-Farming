import 'dart:convert';
import 'dart:io';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'api_service.dart';

class SyncService {
  SyncService(this.api);
  final ApiService api;
  static const _queueKey = 'pending_leaf_scans';

  Future<void> enqueue(File image) async {
    final preferences = await SharedPreferences.getInstance();
    final queue = preferences.getStringList(_queueKey) ?? [];
    queue.add(jsonEncode({'path': image.path, 'created': DateTime.now().toIso8601String()}));
    await preferences.setStringList(_queueKey, queue);
  }

  Future<int> pendingCount() async => (await SharedPreferences.getInstance()).getStringList(_queueKey)?.length ?? 0;

  Future<void> drain() async {
    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity.contains(ConnectivityResult.none)) return;
    final preferences = await SharedPreferences.getInstance();
    final queue = preferences.getStringList(_queueKey) ?? [];
    final remaining = <String>[];
    for (final item in queue) {
      final path = (jsonDecode(item) as Map)['path']?.toString();
      if (path == null || !await File(path).exists()) continue;
      try {
        await api.predict(File(path));
      } catch (_) {
        remaining.add(item);
      }
    }
    await preferences.setStringList(_queueKey, remaining);
  }
}
