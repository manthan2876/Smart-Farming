import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';

/// Service responsible for fetching dynamic runtime configuration from Supabase Remote Config.
class RemoteConfigService {
  RemoteConfigService._();

  static const String defaultSupabaseUrl = 'https://ntqevjzjhntkilmknrfh.supabase.co';

  /// Supabase project URL (configurable via compile-time --dart-define or .env)
  static const String supabaseUrl = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: defaultSupabaseUrl,
  );

  /// Supabase anon public API key (configurable via compile-time --dart-define or .env)
  static const String supabaseAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
    defaultValue: '',
  );

  static const String _cachedBackendUrlKey = 'remote_config_api_base_url';

  /// Fetches the current backend base URL from Supabase `app_config` table.
  /// Falls back gracefully to locally cached value if offline or error occurs.
  static Future<String?> fetchBackendUrl() async {
    // 1. Check if anon key is configured
    if (supabaseAnonKey.isEmpty) {
      AppLogger.warn(
        'RemoteConfig',
        'SUPABASE_ANON_KEY is not set. Using cached or fallback backend URL.',
      );
      return getCachedBackendUrl();
    }

    try {
      final cleanUrl = supabaseUrl.trim().replaceAll(RegExp(r'/+$'), '');
      final uri = Uri.parse('$cleanUrl/rest/v1/app_config?key=eq.api_base_url&select=value');

      AppLogger.info('RemoteConfig', 'Fetching dynamic backend URL from Supabase: $uri');

      final response = await http.get(
        uri,
        headers: {
          'apikey': supabaseAnonKey,
          'Authorization': 'Bearer $supabaseAnonKey',
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 4));

      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        if (data.isNotEmpty && data[0]['value'] != null) {
          final remoteUrl = data[0]['value'].toString().trim().replaceAll(RegExp(r'/+$'), '');
          if (remoteUrl.isNotEmpty) {
            AppLogger.info('RemoteConfig', '✓ Received backend URL from Supabase: $remoteUrl');
            await _cacheBackendUrl(remoteUrl);
            return remoteUrl;
          }
        }
      } else {
        AppLogger.warn(
          'RemoteConfig',
          'Supabase responded with status ${response.statusCode}: ${response.body}',
        );
      }
    } catch (e) {
      AppLogger.warn('RemoteConfig', 'Failed to fetch config from Supabase ($e). Using cached value.');
    }

    // 2. Offline fallback to previously cached value
    return getCachedBackendUrl();
  }

  /// Returns the cached backend URL from previous successful remote fetch.
  static Future<String?> getCachedBackendUrl() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      return prefs.getString(_cachedBackendUrlKey);
    } catch (_) {
      return null;
    }
  }

  /// Caches the remote backend URL locally in SharedPreferences for offline resilience.
  static Future<void> _cacheBackendUrl(String url) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_cachedBackendUrlKey, url);
    } catch (_) {}
  }
}
