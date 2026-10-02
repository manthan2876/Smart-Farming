import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';

/// Service responsible for fetching dynamic runtime configuration from Supabase Remote Config.
class RemoteConfigService {
  RemoteConfigService._();

  static const String defaultSupabaseUrl = 'https://ntqevjzjhntkilmknrfh.supabase.co';
  static const String defaultSupabaseAnonKey =
      'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im50cWV2anpqaG50a2lsbWtucmZoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTAzMjA5MTgsImV4cCI6MjEwNTg5NjkxOH0._WysQ1LtUunC7TQwt2LfqP_X0e_-ug9Z0ioi1fWSMZ0';

  /// Supabase project URL (configurable via compile-time --dart-define or .env)
  static const String supabaseUrl = String.fromEnvironment(
    'SUPABASE_URL',
    defaultValue: defaultSupabaseUrl,
  );

  /// Supabase anon public API key (configurable via compile-time --dart-define or .env)
  static const String supabaseAnonKey = String.fromEnvironment(
    'SUPABASE_ANON_KEY',
    defaultValue: defaultSupabaseAnonKey,
  );

  static const String _cachedBackendUrlKey = 'remote_config_api_base_url';

  /// Fetches the backend base URL exclusively from Supabase `app_config` table.
  /// Falls back gracefully to locally cached Supabase value if device is offline.
  static Future<String?> fetchBackendUrl() async {
    final keyToUse = supabaseAnonKey.isNotEmpty ? supabaseAnonKey : defaultSupabaseAnonKey;
    final urlToUse = supabaseUrl.isNotEmpty ? supabaseUrl : defaultSupabaseUrl;

    try {
      final cleanUrl = urlToUse.trim().replaceAll(RegExp(r'/+$'), '');
      final uri = Uri.parse('$cleanUrl/rest/v1/app_config?key=eq.api_base_url&select=value');

      AppLogger.info('RemoteConfig', 'Fetching dynamic backend URL from Supabase: $uri');

      final response = await http.get(
        uri,
        headers: {
          'apikey': keyToUse,
          'Authorization': 'Bearer $keyToUse',
          'Content-Type': 'application/json',
        },
      ).timeout(const Duration(seconds: 8));

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
