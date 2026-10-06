import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'dart:math';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite/sqflite.dart';
import '../models/sync_queue_item.dart';

class OfflineQueueDb {
  OfflineQueueDb({Database? database}) : _database = database;

  static const String tableName = 'offline_scans';
  static const String _legacyQueueKey = 'pending_leaf_scans';
  static const int maxRetries = 10;

  Database? _database;
  bool _initialized = false;
  bool _useInMemoryFallback = false;
  final List<SyncQueueItem> _fallbackQueue = [];

  Future<void> init() async {
    if (_initialized) return;

    try {
      if (_database == null) {
        final dbDir = await getDatabasesPath();
        final dbPath = p.join(dbDir, 'offline_scans.db');
        _database = await openDatabase(
          dbPath,
          version: 1,
          onCreate: (db, version) async {
            await db.execute('''
              CREATE TABLE IF NOT EXISTS $tableName (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_uuid TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                image_file_path TEXT NOT NULL,
                location TEXT NOT NULL,
                language TEXT NOT NULL,
                plot_id INTEGER,
                lat REAL,
                lon REAL,
                status TEXT NOT NULL DEFAULT 'pending',
                retry_count INTEGER NOT NULL DEFAULT 0,
                last_attempt_at TEXT,
                created_at TEXT NOT NULL
              )
            ''');
          },
        );
      }

      // Reset any stuck 'syncing' scans from a previous crash/app restart back to 'pending'
      await _database?.execute(
        "UPDATE $tableName SET status = 'pending' WHERE status = 'syncing'",
      );
    } catch (e) {
      debugPrint('[OfflineQueueDb] SQLite initialization notice (using memory fallback): $e');
      _useInMemoryFallback = true;
    }

    _initialized = true;

    // Migrate any legacy scans from SharedPreferences into durable storage
    await _migrateLegacyPreferences();
  }

  Future<Directory> _getStorageDirectory() async {
    Directory baseDir;
    try {
      baseDir = await getApplicationDocumentsDirectory();
    } catch (_) {
      baseDir = Directory.systemTemp;
    }
    final dir = Directory(p.join(baseDir.path, 'offline_scans'));
    if (!await dir.exists()) {
      await dir.create(recursive: true);
    }
    return dir;
  }

  Future<void> _migrateLegacyPreferences() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final legacyList = prefs.getStringList(_legacyQueueKey);
      if (legacyList == null || legacyList.isEmpty) return;

      for (final raw in legacyList) {
        try {
          final json = jsonDecode(raw) as Map<String, dynamic>;
          final base64Str = json['base64_data']?.toString();
          if (base64Str == null || base64Str.isEmpty) continue;

          final bytes = base64Decode(base64Str);
          final fileName = json['file_name']?.toString() ?? 'migrated_leaf.jpg';
          final location = json['location']?.toString() ?? 'North plot';
          final language = json['language']?.toString() ?? 'English';
          final plotId = json['plot_id'] != null ? int.tryParse(json['plot_id'].toString()) : null;
          final lat = json['lat'] != null ? double.tryParse(json['lat'].toString()) : null;
          final lon = json['lon'] != null ? double.tryParse(json['lon'].toString()) : null;

          await enqueue(
            bytes,
            fileName,
            location: location,
            language: language,
            plotId: plotId,
            lat: lat,
            lon: lon,
          );
        } catch (e) {
          debugPrint('[OfflineQueueDb] Legacy item migration failed: $e');
        }
      }

      await prefs.remove(_legacyQueueKey);
      debugPrint('[OfflineQueueDb] Successfully migrated legacy SharedPreferences offline queue to SQLite.');
    } catch (e) {
      debugPrint('[OfflineQueueDb] Migration error: $e');
    }
  }

  Future<String> _saveImageBytesLocally(Uint8List bytes, String clientUuid, String originalFileName) async {
    final storageDir = await _getStorageDirectory();
    final ext = p.extension(originalFileName).isNotEmpty ? p.extension(originalFileName) : '.jpg';
    final filePath = p.join(storageDir.path, 'scan_${clientUuid}$ext');
    final file = File(filePath);
    await file.writeAsBytes(bytes, flush: true);
    return filePath;
  }

  Future<SyncQueueItem> enqueue(
    Uint8List bytes,
    String fileName, {
    String location = 'North plot',
    String language = 'English',
    int? plotId,
    double? lat,
    double? lon,
  }) async {
    await init();

    final clientUuid = '${DateTime.now().microsecondsSinceEpoch}_${Random().nextInt(999999)}';
    final imagePath = await _saveImageBytesLocally(bytes, clientUuid, fileName);

    final item = SyncQueueItem(
      clientUuid: clientUuid,
      imageFilePath: imagePath,
      path: imagePath,
      fileName: fileName,
      location: location,
      language: language,
      plotId: plotId,
      lat: lat,
      lon: lon,
      status: 'pending',
      retryCount: 0,
      createdAt: DateTime.now(),
    );

    if (_useInMemoryFallback || _database == null) {
      final assignedId = _fallbackQueue.length + 1;
      final withId = item.copyWith(id: assignedId);
      _fallbackQueue.add(withId);
      return withId;
    }

    final dbMap = item.toDbMap();
    final id = await _database!.insert(
      tableName,
      dbMap,
      conflictAlgorithm: ConflictAlgorithm.replace,
    );

    return item.copyWith(id: id);
  }

  Future<int> pendingCount() async {
    await init();
    if (_useInMemoryFallback || _database == null) {
      return _fallbackQueue.where((i) => i.status != 'failed_permanent').length;
    }

    final result = await _database!.rawQuery(
      "SELECT COUNT(*) as cnt FROM $tableName WHERE status != 'failed_permanent'",
    );
    return Sqflite.firstIntValue(result) ?? 0;
  }

  Future<List<SyncQueueItem>> getItemsToSync() async {
    await init();
    final now = DateTime.now();

    if (_useInMemoryFallback || _database == null) {
      return _fallbackQueue.where((i) {
        if (i.status == 'syncing' || i.status == 'failed_permanent') return false;
        if (i.retryCount > 0 && i.lastAttemptAt != null) {
          final backoffSec = min(300, pow(2, i.retryCount).toInt() * 5);
          if (now.difference(i.lastAttemptAt!).inSeconds < backoffSec) {
            return false;
          }
        }
        return true;
      }).toList();
    }

    final rows = await _database!.query(
      tableName,
      where: "status != 'syncing' AND status != 'failed_permanent' AND retry_count < ?",
      whereArgs: [maxRetries],
      orderBy: 'created_at ASC',
    );

    final items = rows.map((r) => SyncQueueItem.fromDbMap(r)).toList();
    return items.where((i) {
      if (i.retryCount > 0 && i.lastAttemptAt != null) {
        final backoffSec = min(300, pow(2, i.retryCount).toInt() * 5);
        if (now.difference(i.lastAttemptAt!).inSeconds < backoffSec) {
          return false;
        }
      }
      return true;
    }).toList();
  }

  Future<List<SyncQueueItem>> getAllItems() async {
    await init();
    if (_useInMemoryFallback || _database == null) {
      return List.unmodifiable(_fallbackQueue);
    }
    final rows = await _database!.query(tableName, orderBy: 'created_at DESC');
    return rows.map((r) => SyncQueueItem.fromDbMap(r)).toList();
  }

  Future<void> markSyncing(int id) async {
    await init();
    if (_useInMemoryFallback || _database == null) {
      final idx = _fallbackQueue.indexWhere((i) => i.id == id);
      if (idx != -1) {
        _fallbackQueue[idx] = _fallbackQueue[idx].copyWith(status: 'syncing');
      }
      return;
    }
    await _database!.update(
      tableName,
      {'status': 'syncing'},
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> markFailed(int id, int newRetryCount) async {
    await init();
    final newStatus = newRetryCount >= maxRetries ? 'failed_permanent' : 'retry_pending';
    final nowIso = DateTime.now().toIso8601String();

    if (_useInMemoryFallback || _database == null) {
      final idx = _fallbackQueue.indexWhere((i) => i.id == id);
      if (idx != -1) {
        _fallbackQueue[idx] = _fallbackQueue[idx].copyWith(
          status: newStatus,
          retryCount: newRetryCount,
          lastAttemptAt: DateTime.now(),
        );
      }
      return;
    }

    await _database!.update(
      tableName,
      {
        'status': newStatus,
        'retry_count': newRetryCount,
        'last_attempt_at': nowIso,
      },
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<void> deleteItem(int id, {String? imageFilePath}) async {
    await init();

    // 1. Delete associated image file from disk
    if (imageFilePath != null && imageFilePath.isNotEmpty) {
      try {
        final file = File(imageFilePath);
        if (await file.exists()) {
          await file.delete();
        }
      } catch (e) {
        debugPrint('[OfflineQueueDb] Error deleting local scan file: $e');
      }
    }

    // 2. Delete DB record
    if (_useInMemoryFallback || _database == null) {
      _fallbackQueue.removeWhere((i) => i.id == id);
      return;
    }

    await _database!.delete(
      tableName,
      where: 'id = ?',
      whereArgs: [id],
    );
  }

  Future<Uint8List?> readItemImageBytes(SyncQueueItem item) async {
    if (item.imageFilePath != null && item.imageFilePath!.isNotEmpty) {
      final file = File(item.imageFilePath!);
      if (await file.exists()) {
        return await file.readAsBytes();
      }
    }
    if (item.base64Data != null && item.base64Data!.isNotEmpty) {
      return base64Decode(item.base64Data!);
    }
    return null;
  }
}
