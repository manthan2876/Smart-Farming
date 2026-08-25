import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/prediction.dart';

class ApiService {
  ApiService({this.baseUrl = 'http://10.0.2.2:8000', this.accessToken});
  final String baseUrl;
  final String? accessToken;

  Map<String, String> get _headers => {
        if (accessToken != null) 'Authorization': 'Bearer $accessToken',
        'Accept': 'application/json',
      };

  Future<Prediction> predict(File image, {String location = 'North plot', String language = 'English'}) async {
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
