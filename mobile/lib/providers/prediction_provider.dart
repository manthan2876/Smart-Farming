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
    try {
      items
        ..clear()
        ..addAll(await api.history());
      notifyListeners();
    } catch (_) {}
  }

  Future<Prediction?> submitBytes(Uint8List bytes, String fileName, {String location = 'North plot', String language = 'English'}) async {
    isBusy = true;
    notifyListeners();
    try {
      final result = await api.predictBytes(bytes, fileName, location: location, language: language);
      final pid = (result['prediction_id'] as num?)?.toInt() ?? (result['id'] as num?)?.toInt() ?? 0;
      final pred = pid > 0 ? await api.getPrediction(pid) : Prediction.fromJson(result);
      items.insert(0, pred);
      return pred;
    } catch (_) {
      await sync.enqueueBytes(bytes, fileName, location: location, language: language);
      pending = await sync.pendingCount();
      return null;
    } finally {
      isBusy = false;
      notifyListeners();
    }
  }
}
