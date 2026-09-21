import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import '../models/prediction.dart';

class ApiService {
  ApiService({String? baseUrl, this.accessToken})
      : baseUrl = baseUrl ?? _resolveDefaultBaseUrl();

  final String baseUrl;
  final String? accessToken;

  static String _resolveDefaultBaseUrl() {
    const envUrl = String.fromEnvironment('API_BASE_URL', defaultValue: '');
    if (envUrl.isNotEmpty) return envUrl;
    if (kIsWeb) {
      return 'http://127.0.0.1:8000';
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return 'http://10.0.2.2:8000';
      default:
        return 'http://127.0.0.1:8000';
    }
  }

  String getAssetUrl(String? path) {
    if (path == null || path.isEmpty) return '';
    if (path.startsWith('http://') || path.startsWith('https://')) return path;
    final normalized = path.startsWith('/') ? path : '/$path';
    return '$baseUrl$normalized';
  }

  Map<String, String> get _headers => {
        if (accessToken != null) 'Authorization': 'Bearer $accessToken',
        'Accept': 'application/json',
      };

  Future<Map<String, dynamic>> login(String identifier, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: jsonEncode({'identifier': identifier, 'password': password}),
    );
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Authentication failed');
    }

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
    final response = await http.post(
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
    );
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Registration failed');
    }
    return body;
  }

  Future<Map<String, dynamic>> getProfile() async {
    final response = await http.get(Uri.parse('$baseUrl/profile'), headers: _headers);
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Failed to retrieve profile');
    }

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
    final response = await http.patch(
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
    );
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Failed to update profile');
    }
    return body;
  }

  Future<Map<String, dynamic>> getFarm() async {
    final response = await http.get(Uri.parse('$baseUrl/farm'), headers: _headers);
    if (response.statusCode == 404) return {};
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Failed to retrieve farm details');
    }
    return body;
  }

  Future<Map<String, dynamic>> saveFarm({
    required String name,
    required String location,
    required double areaAcres,
    double? latitude,
    double? longitude,
    List<String>? cropHistory,
  }) async {
    final response = await http.put(
      Uri.parse('$baseUrl/farm'),
      headers: {'Content-Type': 'application/json', ..._headers},
      body: jsonEncode({
        'name': name,
        'location': location,
        'area_acres': areaAcres,
        if (latitude != null) 'latitude': latitude,
        if (longitude != null) 'longitude': longitude,
        'crop_history': cropHistory ?? [],
      }),
    );
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Failed to save farm details');
    }
    return body;
  }

  Future<Map<String, dynamic>> createPlot({
    required String name,
    required String crop,
    required double areaAcres,
    String status = 'Active',
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/farm/plots'),
      headers: {'Content-Type': 'application/json', ..._headers},
      body: jsonEncode({
        'name': name,
        'crop': crop,
        'area_acres': areaAcres,
        'status': status,
      }),
    );
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Failed to create plot');
    }
    return body;
  }

  Future<Map<String, dynamic>> getWeather({double lat = 22.2587, double lon = 71.1924}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/weather?lat=$lat&lon=$lon'),
      headers: _headers,
    );
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Failed to retrieve weather');
    }
    return body;
  }

  Future<List<Map<String, dynamic>>> getAlerts() async {
    final response = await http.get(Uri.parse('$baseUrl/alerts'), headers: _headers);
    if (response.statusCode >= 400) {
      throw Exception('Failed to retrieve alerts');
    }
    return (jsonDecode(response.body) as List).cast<Map<String, dynamic>>();
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
      Uri.parse('$baseUrl/predict/$predictionId/expert-review'),
      headers: _headers,
    );
    if (response.statusCode >= 400) {
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      throw Exception(body['detail'] ?? 'Failed to request expert review');
    }
  }

  Future<Map<String, dynamic>> translatePrediction(int id, String language) async {
    final response = await http.post(
      Uri.parse('$baseUrl/predictions/$id/translate?target_language=$language'),
      headers: _headers,
    );
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['detail'] ?? 'Failed to translate prediction');
    }
    return body;
  }

  Future<String?> generateTTS(String text, {String language = 'en'}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/tts'),
        headers: {'Content-Type': 'application/json', ..._headers},
        body: jsonEncode({'text': text, 'language': language}),
      );
      if (response.statusCode >= 400) return null;
      final body = jsonDecode(response.body) as Map<String, dynamic>;
      return body['audioContent']?.toString();
    } catch (_) {
      return null;
    }
  }

  Future<List<Prediction>> history() async {
    final response = await http.get(Uri.parse('$baseUrl/history?limit=30'), headers: _headers);
    if (response.statusCode >= 400) throw Exception('History unavailable');
    return (jsonDecode(response.body) as List).map((item) => Prediction.fromJson(item)).toList();
  }
}
