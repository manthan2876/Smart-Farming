import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:smart_farming_mobile/services/remote_config_service.dart';
import 'package:smart_farming_mobile/services/api_service.dart';

class _RealHttpOverrides extends HttpOverrides {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  HttpOverrides.global = _RealHttpOverrides();

  test('RemoteConfigService fetches backend URL from Supabase', () async {
    final url = await RemoteConfigService.fetchBackendUrl();
    expect(url, isNotNull);
    expect(url, startsWith('https://smart-farming-backend-'));
    expect(url, contains('run.app'));
  });

  test('ApiService initializes backend URL strictly from Supabase Remote Config', () async {
    await ApiService.initBaseUrl();
    expect(ApiService.customBaseUrl, isNotNull);
    expect(ApiService.customBaseUrl, startsWith('https://smart-farming-backend-'));

    final api = ApiService();
    expect(api.baseUrl, equals(ApiService.customBaseUrl));
    expect(api.baseUrl, isNot(contains('127.0.0.1')));
    expect(api.baseUrl, isNot(contains('localhost')));
  });
}
