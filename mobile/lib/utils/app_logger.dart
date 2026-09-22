import 'package:flutter/foundation.dart';

/// Centralized logger for Smart Farming Mobile App that outputs styled logs to terminal.
class AppLogger {
  static const bool enabled = true;

  static void info(String tag, String message) {
    if (!enabled) return;
    debugPrint('\x1B[32m[MOBILE INFO][$tag]\x1B[0m $message');
  }

  static void warn(String tag, String message) {
    if (!enabled) return;
    debugPrint('\x1B[33m[MOBILE WARN][$tag]\x1B[0m $message');
  }

  static void error(String tag, String message, [Object? error, StackTrace? stack]) {
    if (!enabled) return;
    debugPrint('\x1B[31m[MOBILE ERROR][$tag]\x1B[0m $message');
    if (error != null) {
      debugPrint('\x1B[31m  Error details:\x1B[0m $error');
    }
    if (stack != null) {
      debugPrint('\x1B[31m  Stack trace:\x1B[0m $stack');
    }
  }

  static void network(String method, String url, {int? statusCode, int? itemCount, String? detail}) {
    if (!enabled) return;
    final statusStr = statusCode != null ? ' → Status: $statusCode' : '';
    final countStr = itemCount != null ? ' ($itemCount items)' : '';
    final detailStr = detail != null ? ' | $detail' : '';
    debugPrint('\x1B[36m[MOBILE HTTP]\x1B[0m $method $url$statusStr$countStr$detailStr');
  }
}

