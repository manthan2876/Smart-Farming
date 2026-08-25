import 'dart:io';
import 'package:flutter/foundation.dart';
import '../models/prediction.dart';
import '../services/api_service.dart';
import '../services/sync_service.dart';

class PredictionProvider extends ChangeNotifier {
  PredictionProvider(this.api, this.sync);
  final ApiService api;
  final SyncService sync;
  final List<Prediction> items = [];
  bool isBusy = false;
  int pending = 0;

  Future<void> loadHistory() async {
    try { items..clear()..addAll(await api.history()); notifyListeners(); } catch (_) {}
  }
  Future<Prediction?> submit(File photo) async {
    isBusy = true; notifyListeners();
    try { final result = await api.predict(photo); items.insert(0, result); return result; }
    catch (_) { await sync.enqueue(photo); pending = await sync.pendingCount(); return null; }
    finally { isBusy = false; notifyListeners(); }
  }
}
