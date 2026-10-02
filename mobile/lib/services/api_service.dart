import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../models/prediction.dart';
import '../utils/app_logger.dart';
import 'remote_config_service.dart';

class ApiService {
  static String? customBaseUrl;

  /// Initializes the backend base URL dynamically and exclusively from Supabase Remote Config.
  /// The mobile app strictly uses the URL defined in Supabase public.app_config (key: api_base_url).
  static Future<void> initBaseUrl() async {
    final remoteUrl = await RemoteConfigService.fetchBackendUrl();
    if (remoteUrl != null && remoteUrl.isNotEmpty) {
      customBaseUrl = remoteUrl;
      AppLogger.info('ApiService', 'Backend URL initialized exclusively from Supabase: $customBaseUrl');
    } else {
      AppLogger.error('ApiService', 'Failed to retrieve backend URL from Supabase Remote Config.');
    }
  }

  static Future<bool> testConnection(String url) async {
    try {
      final clean = url.trim().replaceAll(RegExp(r'/+$'), '');
      final uri = Uri.parse('$clean/health');
      final res = await http.get(uri).timeout(const Duration(seconds: 5));
      return res.statusCode < 500;
    } catch (_) {
      return false;
    }
  }

  ApiService({String? baseUrl, this.accessToken, this.languageCode})
      : baseUrl = baseUrl ?? customBaseUrl ?? '';

  final String baseUrl;
  final String? accessToken;
  String? languageCode;

  String getAssetUrl(String? path) {
    if (path == null || path.isEmpty) return '';
    if (path.startsWith('http://') || path.startsWith('https://')) return path;
    final normalized = path.startsWith('/') ? path : '/$path';
    return '$baseUrl$normalized';
  }

  Map<String, String> get _headers => {
        if (accessToken != null) 'Authorization': 'Bearer $accessToken',
        if (languageCode != null && languageCode!.isNotEmpty) 'Accept-Language': languageCode!,
        'Accept': 'application/json',
      };

  Future<http.Response> _sendWithRetry(
    Future<http.Response> Function() requestFn, {
    int maxRetries = 1,
    Duration timeout = const Duration(seconds: 30),
  }) async {
    int attempts = 0;
    while (true) {
      attempts++;
      try {
        final response = await requestFn().timeout(timeout);
        final status = response.statusCode;
        final bodyLower = response.body.toLowerCase();
        final isColdStartTimeout = status == 504 ||
            status == 502 ||
            bodyLower.contains('upstream request timeout') ||
            bodyLower.contains('upstream connect error');

        if (isColdStartTimeout && attempts <= maxRetries) {
          AppLogger.warn('ApiService', 'Server cold start / timeout ($status). Retrying in 1.5s (attempt $attempts)...');
          await Future.delayed(const Duration(milliseconds: 1500));
          continue;
        }
        return response;
      } on TimeoutException {
        if (attempts <= maxRetries) {
          AppLogger.warn('ApiService', 'Request timed out on attempt $attempts. Retrying in 1.5s...');
          await Future.delayed(const Duration(milliseconds: 1500));
          continue;
        }
        throw Exception('Server is taking too long to respond. Please try again.');
      } catch (e) {
        if (e is SocketException && attempts <= maxRetries) {
          AppLogger.warn('ApiService', 'SocketException on attempt $attempts. Retrying in 1.5s...');
          await Future.delayed(const Duration(milliseconds: 1500));
          continue;
        }
        rethrow;
      }
    }
  }

  Map<String, dynamic> _parseJsonResponse(
    http.Response response, {
    String fallbackError = 'Request failed',
  }) {
    final status = response.statusCode;
    final bodyText = response.body.trim();

    if (status >= 500) {
      final lower = bodyText.toLowerCase();
      if (lower.contains('upstream') || lower.contains('timeout') || status == 504 || status == 502) {
        throw Exception('Server is starting up or temporarily busy. Please try again in a few moments.');
      }
      throw Exception('Server error ($status). Please try again shortly.');
    }

    if (bodyText.isEmpty) {
      if (status >= 400) {
        throw Exception('$fallbackError (HTTP $status)');
      }
      return {};
    }

    try {
      final decoded = jsonDecode(bodyText);
      if (decoded is Map<String, dynamic>) {
        if (status >= 400) {
          final detail = decoded['detail'];
          if (detail is String && detail.isNotEmpty) {
            throw Exception(detail);
          } else if (detail is List && detail.isNotEmpty) {
            final msg = detail.map((e) => e is Map ? (e['msg'] ?? e.toString()) : e.toString()).join(', ');
            throw Exception(msg);
          }
          throw Exception('$fallbackError (HTTP $status)');
        }
        return decoded;
      }
      if (status >= 400) {
        throw Exception('$fallbackError (HTTP $status)');
      }
      return {'data': decoded};
    } on FormatException {
      if (status >= 400) {
        if (bodyText.toLowerCase().contains('timeout') || bodyText.toLowerCase().contains('upstream')) {
          throw Exception('Server request timed out. Please try again.');
        }
        throw Exception('$fallbackError ($status)');
      }
      throw Exception('Unexpected server response ($status)');
    }
  }

  Future<Map<String, dynamic>> login(String identifier, String password) async {
    final response = await _sendWithRetry(() => http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: jsonEncode({'identifier': identifier, 'password': password}),
    ));
    final body = _parseJsonResponse(response, fallbackError: 'Authentication failed');

    // Role check: ONLY allow farmers
    final user = body['user'] as Map<String, dynamic>?;
    final role = user?['role']?.toString().toLowerCase();
    if (role != null && role != 'farmer') {
      throw Exception('Access restricted: This mobile app is exclusively for farmers.');
    }

    return body;
  }

  Future<Map<String, dynamic>> register({
    required String name,
    required String password,
    String? email,
    String? phone,
    String location = 'North plot',
    String language = 'English',
    List<String> cropHistory = const [],
    String? farmName,
    double? farmAreaAcres,
  }) async {
    final response = await _sendWithRetry(() => http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: jsonEncode({
        'name': name,
        'password': password,
        if (email != null && email.isNotEmpty) 'email': email,
        if (phone != null && phone.isNotEmpty) 'phone': phone,
        'location': location,
        'language': language,
        'crop_history': cropHistory,
        if (farmName != null) 'farm_name': farmName,
        if (farmAreaAcres != null) 'farm_area_acres': farmAreaAcres,
      }),
    ));
    return _parseJsonResponse(response, fallbackError: 'Registration failed');
  }

  Future<Map<String, dynamic>> getProfile({String? lang}) async {
    final effectiveLang = lang ?? languageCode;
    final query = effectiveLang != null && effectiveLang.isNotEmpty ? '?lang=$effectiveLang' : '';
    final response = await _sendWithRetry(
      () => http.get(Uri.parse('$baseUrl/profile$query'), headers: _headers),
    );
    final body = _parseJsonResponse(response, fallbackError: 'Failed to retrieve profile');

    // Ensure farmer role
    final role = body['role']?.toString().toLowerCase();
    if (role != null && role != 'farmer') {
      throw Exception('Access restricted: This mobile app is exclusively for farmers.');
    }

    return body;
  }

  Future<Map<String, dynamic>> updateProfile({
    String? name,
    String? language,
    String? location,
    List<String>? cropHistory,
    String? farmName,
    double? farmAreaAcres,
  }) async {
    final response = await _sendWithRetry(() => http.patch(
      Uri.parse('$baseUrl/profile'),
      headers: {'Content-Type': 'application/json', ..._headers},
      body: jsonEncode({
        if (name != null) 'name': name,
        if (language != null) 'language': language,
        if (location != null) 'location': location,
        if (cropHistory != null) 'crop_history': cropHistory,
        if (farmName != null) 'farm_name': farmName,
        if (farmAreaAcres != null) 'farm_area_acres': farmAreaAcres,
      }),
    ));
    return _parseJsonResponse(response, fallbackError: 'Failed to update profile');
  }

  Future<Map<String, dynamic>> getFarm({String? lang}) async {
    final effectiveLang = lang ?? languageCode;
    final query = effectiveLang != null && effectiveLang.isNotEmpty ? '?lang=$effectiveLang' : '';
    final response = await _sendWithRetry(
      () => http.get(Uri.parse('$baseUrl/farm$query'), headers: _headers),
    );
    if (response.statusCode == 404) return {};
    return _parseJsonResponse(response, fallbackError: 'Failed to retrieve farm details');
  }

  Future<Map<String, dynamic>> saveFarm({
    required String name,
    required String location,
    required double areaAcres,
    double? latitude,
    double? longitude,
    List<String>? cropHistory,
    Map<String, dynamic>? boundary,
    bool resetBoundary = false,
  }) async {
    final payload = <String, dynamic>{
      'name': name,
      'location': location,
      'area_acres': areaAcres,
      if (latitude != null) 'latitude': latitude,
      if (longitude != null) 'longitude': longitude,
      'crop_history': cropHistory ?? [],
    };
    if (resetBoundary) {
      payload['boundary'] = null;
    } else if (boundary != null) {
      payload['boundary'] = boundary;
    }

    final response = await _sendWithRetry(() => http.put(
      Uri.parse('$baseUrl/farm'),
      headers: {'Content-Type': 'application/json', ..._headers},
      body: jsonEncode(payload),
    ));
    return _parseJsonResponse(response, fallbackError: 'Failed to save farm details');
  }

  Future<Map<String, dynamic>> createPlot({
    required String name,
    required String crop,
    required double areaAcres,
    String status = 'Active',
    Map<String, dynamic>? geometry,
  }) async {
    final payload = <String, dynamic>{
      'name': name,
      'crop': crop,
      'area_acres': areaAcres,
      'status': status,
      if (geometry != null) 'geometry': geometry,
    };

    final response = await _sendWithRetry(() => http.post(
      Uri.parse('$baseUrl/farm/plots'),
      headers: {'Content-Type': 'application/json', ..._headers},
      body: jsonEncode(payload),
    ));
    return _parseJsonResponse(response, fallbackError: 'Failed to create plot');
  }

  Future<Map<String, dynamic>> updatePlot(
    int plotId, {
    required String name,
    required String crop,
    required double areaAcres,
    String status = 'Active',
    Map<String, dynamic>? geometry,
    bool resetGeometry = false,
  }) async {
    final payload = <String, dynamic>{
      'name': name,
      'crop': crop,
      'area_acres': areaAcres,
      'status': status,
    };
    if (resetGeometry) {
      payload['geometry'] = null;
    } else if (geometry != null) {
      payload['geometry'] = geometry;
    }

    final response = await _sendWithRetry(() => http.put(
      Uri.parse('$baseUrl/farm/plots/$plotId'),
      headers: {'Content-Type': 'application/json', ..._headers},
      body: jsonEncode(payload),
    ));
    return _parseJsonResponse(response, fallbackError: 'Failed to update plot');
  }

  Future<Map<String, dynamic>> getWeather({double lat = 22.2587, double lon = 71.1924, String? language}) async {
    final langParam = language != null && language.isNotEmpty ? '&language=${Uri.encodeComponent(language)}' : '';
    final response = await _sendWithRetry(
      () => http.get(
        Uri.parse('$baseUrl/weather?lat=$lat&lon=$lon$langParam'),
        headers: _headers,
      ),
      timeout: const Duration(seconds: 15),
    );
    return _parseJsonResponse(response, fallbackError: 'Failed to retrieve weather');
  }

  Future<String?> translateWeatherAdvisory(String text, String targetLanguage) async {
    if (text.trim().isEmpty || targetLanguage == 'en') return text;
    try {
      final response = await _sendWithRetry(
        () => http.post(
          Uri.parse('$baseUrl/weather/translate'),
          headers: {'Content-Type': 'application/json', ..._headers},
          body: jsonEncode({'text': text, 'target_language': targetLanguage}),
        ),
        timeout: const Duration(seconds: 15),
      );
      if (response.statusCode >= 400) return null;
      final body = _parseJsonResponse(response);
      return body['translated_text']?.toString();
    } catch (_) {
      return null;
    }
  }

  Future<List<Map<String, dynamic>>> getAlerts({String? lang}) async {
    final effectiveLang = lang ?? languageCode;
    final query = effectiveLang != null && effectiveLang.isNotEmpty ? '?lang=$effectiveLang' : '';
    final response = await _sendWithRetry(
      () => http.get(Uri.parse('$baseUrl/alerts$query'), headers: _headers),
    );
    if (response.statusCode >= 400) {
      throw Exception('Failed to retrieve alerts (${response.statusCode})');
    }
    final bodyText = response.body.trim();
    if (bodyText.isEmpty) return [];
    try {
      final decoded = jsonDecode(bodyText);
      if (decoded is List) {
        return decoded.cast<Map<String, dynamic>>();
      }
      return [];
    } catch (_) {
      return [];
    }
  }

  Future<void> deletePlot(int plotId) async {
    final response = await http.delete(
      Uri.parse('$baseUrl/farm/plots/$plotId'),
      headers: _headers,
    );
    if (response.statusCode >= 400) {
      throw Exception('Failed to delete plot');
    }
  }

  Future<List<String>> getSupportedCrops() async {
    final response = await http.get(Uri.parse('$baseUrl/crops'), headers: _headers);
    if (response.statusCode >= 400) {
      throw Exception('Failed to retrieve supported crops');
    }
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    final list = body['crops'] as List?;
    return list?.map((e) => e.toString()).toList() ?? [];
  }

  Future<void> markAlertRead(int alertId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/alerts/$alertId/read'),
      headers: _headers,
    );
    if (response.statusCode >= 400) {
      throw Exception('Failed to mark alert as read');
    }
  }

  Future<void> markAllAlertsRead(List<int> alertIds) async {
    for (final id in alertIds) {
      try {
        await markAlertRead(id);
      } catch (_) {}
    }
  }

  String getWebSocketUrl(String path) {
    final uri = Uri.parse(baseUrl);
    final scheme = uri.scheme == 'https' ? 'wss' : 'ws';
    final host = uri.host;
    final port = uri.hasPort ? ':${uri.port}' : '';
    final normalizedPath = path.startsWith('/') ? path : '/$path';
    return '$scheme://$host$port$normalizedPath';
  }

  Future<Map<String, dynamic>> predictBytes(
    Uint8List bytes,
    String filename, {
    String location = 'North plot',
    String language = 'English',
    int? plotId,
    double lat = 21.7645,
    double lon = 72.1519,
  }) async {
    final cleanFilename = filename.isNotEmpty ? filename : 'leaf_scan.jpg';
    final lower = cleanFilename.toLowerCase();
    final mediaType = lower.endsWith('.png')
        ? MediaType('image', 'png')
        : lower.endsWith('.webp')
            ? MediaType('image', 'webp')
            : MediaType('image', 'jpeg');

    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/predict'));
    request.headers.addAll(_headers);
    request.files.add(
      http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: cleanFilename,
        contentType: mediaType,
      ),
    );
    request.fields.addAll({
      'location': location,
      'language': language,
      'lat': lat.toString(),
      'lon': lon.toString(),
      if (plotId != null) 'plot_id': plotId.toString(),
    });
    final response = await request.send();
    final resString = await response.stream.bytesToString();
    final body = jsonDecode(resString) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Prediction failed (${response.statusCode})');
    }
    return body;
  }

  Future<Prediction> getPrediction(int id) async {
    final response = await http.get(Uri.parse('$baseUrl/predictions/$id'), headers: _headers);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) throw Exception(body['detail'] ?? 'Prediction not found');
    return Prediction.fromJson(body);
  }

  Future<Map<String, dynamic>> getPredictionRaw(int id) async {
    final response = await http.get(Uri.parse('$baseUrl/predictions/$id'), headers: _headers);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) throw Exception(body['detail'] ?? 'Prediction not found');
    return body;
  }

  Future<void> submitFeedback(int predictionId, bool isCorrect, String note) async {
    final response = await http.post(
      Uri.parse('$baseUrl/feedback'),
      headers: {'Content-Type': 'application/json', ..._headers},
      body: jsonEncode({
        'prediction_id': predictionId,
        'is_correct': isCorrect,
        'farmer_note': note,
      }),
    );
    if (response.statusCode >= 400) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      throw Exception(body['detail'] ?? 'Failed to submit feedback');
    }
  }

  Future<void> requestExpertReview(int predictionId) async {
    final response = await http.post(
      Uri.parse('$baseUrl/predictions/$predictionId/request-expert'),
      headers: _headers,
    );
    if (response.statusCode >= 400) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      throw Exception(body['detail'] ?? 'Failed to request expert review');
    }
  }

  Future<Map<String, dynamic>> rescanBytes(
    int predictionId,
    Uint8List bytes,
    String filename, {
    int? plotId,
  }) async {
    final cleanFilename = filename.isNotEmpty ? filename : 'rescan_leaf.jpg';
    final lower = cleanFilename.toLowerCase();
    final mediaType = lower.endsWith('.png')
        ? MediaType('image', 'png')
        : lower.endsWith('.webp')
            ? MediaType('image', 'webp')
            : MediaType('image', 'jpeg');

    final request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/predictions/$predictionId/rescan'),
    );
    request.headers.addAll(_headers);
    request.files.add(
      http.MultipartFile.fromBytes(
        'file',
        bytes,
        filename: cleanFilename,
        contentType: mediaType,
      ),
    );
    if (plotId != null) {
      request.fields['plot_id'] = plotId.toString();
    }
    final streamedResponse = await request.send();
    final resString = await streamedResponse.stream.bytesToString();
    final body = jsonDecode(resString) as Map<String, dynamic>;
    if (streamedResponse.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Rescan failed (${streamedResponse.statusCode})');
    }
    return body;
  }

  Future<void> changePassword({
    required String oldPassword,
    required String newPassword,
  }) async {
    final response = await _sendWithRetry(() => http.post(
      Uri.parse('$baseUrl/auth/change-password'),
      headers: {'Content-Type': 'application/json', ..._headers},
      body: jsonEncode({
        'old_password': oldPassword,
        'new_password': newPassword,
      }),
    ));
    _parseJsonResponse(response, fallbackError: 'Failed to change password');
  }

  Future<String> forgotPassword(String email) async {
    final response = await _sendWithRetry(() => http.post(
      Uri.parse('$baseUrl/auth/forgot-password'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: jsonEncode({'email': email.trim()}),
    ));
    final body = _parseJsonResponse(response, fallbackError: 'Failed to send reset link');
    return body['message']?.toString() ?? 'Password reset link sent to your email.';
  }

  Future<String> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    final response = await _sendWithRetry(() => http.post(
      Uri.parse('$baseUrl/auth/reset-password'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: jsonEncode({
        'token': token.trim(),
        'new_password': newPassword,
      }),
    ));
    final body = _parseJsonResponse(response, fallbackError: 'Failed to reset password');
    return body['message']?.toString() ?? 'Password has been reset successfully.';
  }

  Future<Map<String, dynamic>> translatePrediction(int id, String language) async {
    final response = await _sendWithRetry(() => http.post(
      Uri.parse('$baseUrl/predictions/$id/translate?target_language=$language'),
      headers: _headers,
    ));
    return _parseJsonResponse(response, fallbackError: 'Failed to translate prediction');
  }

  Future<String?> generateTTS(String text, {String language = 'en'}) async {
    final cleanText = text.trim();
    if (cleanText.isEmpty) return null;
    try {
      final response = await http
          .post(
            Uri.parse('$baseUrl/tts'),
            headers: {'Content-Type': 'application/json', ..._headers},
            body: jsonEncode({'text': cleanText, 'language': language}),
          )
          .timeout(const Duration(seconds: 15));
      if (response.statusCode >= 400) return null;
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      return body['audioContent']?.toString();
    } catch (_) {
      return null;
    }
  }

  Future<List<Prediction>> history({int limit = 30}) async {
    final url = '$baseUrl/history?limit=$limit';
    AppLogger.network('GET', url, detail: 'Fetching historical crop scans');
    try {
      final response = await http.get(Uri.parse(url), headers: _headers);
      AppLogger.network(
        'GET',
        url,
        statusCode: response.statusCode,
        detail: 'Response payload: ${response.body.length} bytes',
      );

      if (response.statusCode >= 400) {
        AppLogger.error(
          'ApiService',
          'Failed to retrieve scan history (HTTP ${response.statusCode}): ${response.body}',
        );
        throw Exception('History unavailable (${response.statusCode})');
      }

      final decoded = jsonDecode(response.body);
      if (decoded is! List) {
        AppLogger.warn('ApiService', 'Expected List from /history but received: ${decoded.runtimeType}');
        return [];
      }

      final List<Prediction> items = [];
      for (final raw in decoded) {
        if (raw is Map<String, dynamic>) {
          try {
            final pred = Prediction.fromJson(raw);
            items.add(pred);
          } catch (e, stack) {
            AppLogger.error('ApiService', 'Error parsing prediction record #${raw['prediction_id'] ?? raw['id']}: $e', e, stack);
          }
        } else if (raw is Map) {
          try {
            final pred = Prediction.fromJson(raw.cast<String, dynamic>());
            items.add(pred);
          } catch (e, stack) {
            AppLogger.error('ApiService', 'Error parsing prediction record: $e', e, stack);
          }
        }
      }

      AppLogger.info('ApiService', 'Successfully parsed ${items.length} of ${decoded.length} scan history items:');
      for (final p in items) {
        AppLogger.info('ApiService', '  • Scan #${p.id}: ${p.crop} | ${p.disease} (${p.severity}% severity, ${(p.confidence * 100).round()}% conf) [${p.status}]');
      }

      return items;
    } catch (e, stack) {
      AppLogger.error('ApiService', 'Exception during history() call', e, stack);
      rethrow;
    }
  }
}
