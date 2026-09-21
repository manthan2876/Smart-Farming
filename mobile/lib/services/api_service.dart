import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/prediction.dart';

class ApiService {
  ApiService({String? baseUrl, this.accessToken})
      : baseUrl = baseUrl ?? _resolveDefaultBaseUrl();

  final String baseUrl;
  final String? accessToken;

  static String _resolveDefaultBaseUrl() {
    // Configurable via environment declaration or defaults to Android emulator / local loopback
    const envUrl = String.fromEnvironment('API_BASE_URL', defaultValue: '');
    if (envUrl.isNotEmpty) return envUrl;
    if (Platform.isAndroid) return 'http://10.0.2.2:8000';
    return 'http://127.0.0.1:8000';
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
  }) async {
    final response = await http.post(
      Uri.parse('$baseUrl/auth/register'),
      headers: {'Content-Type': 'application/json', 'Accept': 'application/json'},
      body: jsonEncode({
        'name': name,
        'password': password,
        if (email != null) 'email': email,
        if (phone != null) 'phone': phone,
        'location': location,
        'language': language,
        'crop_history': cropHistory,
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

  Future<Prediction> predict(
    File image, {
    String location = 'North plot',
    String language = 'English',
  }) async {
    final request = http.MultipartRequest('POST', Uri.parse('$baseUrl/predict'));
    request.headers.addAll(_headers);
    request.files.add(await http.MultipartFile.fromPath('file', image.path));
    request.fields.addAll({'location': location, 'language': language});
    final response = await request.send();
    final body = jsonDecode(await response.stream.bytesToString()) as Map<String, dynamic>;
    if (response.statusCode >= 400) throw Exception(body['detail'] ?? 'Prediction failed');
    return Prediction.fromJson(body);
  }

  Future<List<Prediction>> history() async {
    final response = await http.get(Uri.parse('$baseUrl/history?limit=20'), headers: _headers);
    if (response.statusCode >= 400) throw Exception('History unavailable');
    return (jsonDecode(response.body) as List).map((item) => Prediction.fromJson(item)).toList();
  }
}
