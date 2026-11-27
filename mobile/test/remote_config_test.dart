import 'dart:io';
import 'package:flutter_test/flutter_test.dart';
import 'package:smart_farming_mobile/services/remote_config_service.dart';
import 'package:smart_farming_mobile/services/api_service.dart';

class _RealHttpOverrides extends HttpOverrides {}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  HttpOverrides.global = _RealHttpOverrides();

  test('RemoteConfigService fetches latest Render backend URL from Supabase', () async {
    final url = await RemoteConfigService.fetchBackendUrl();
    expect(url, isNotNull);
    expect(url, equals('https://smart-farming-backend-kkty.onrender.com'));
  });

  test('RemoteConfigService fallback constant points to latest Render backend URL', () {
    expect(RemoteConfigService.defaultBackendUrl, equals('https://smart-farming-backend-kkty.onrender.com'));
    expect(RemoteConfigService.defaultBackendUrl, isNot(contains('run.app')));
  });

  test('ApiService initializes backend URL from Supabase Remote Config', () async {
    await ApiService.initBaseUrl();
    expect(ApiService.customBaseUrl, equals('https://smart-farming-backend-kkty.onrender.com'));

    final api = ApiService();
    expect(api.baseUrl, equals(ApiService.customBaseUrl));
    expect(api.baseUrl, isNot(contains('127.0.0.1')));
    expect(api.baseUrl, isNot(contains('localhost')));
  });
}
