import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smart_farming_mobile/models/prediction.dart';
import 'package:smart_farming_mobile/providers/locale_provider.dart';
import 'package:smart_farming_mobile/screens/alerts/alerts_screen.dart';
import 'package:smart_farming_mobile/screens/auth/login_screen.dart';
import 'package:smart_farming_mobile/screens/camera_screen.dart';
import 'package:smart_farming_mobile/screens/farm/farm_screen.dart';
import 'package:smart_farming_mobile/screens/history/history_screen.dart';
import 'package:smart_farming_mobile/screens/scan/create_prediction_sheet.dart';
import 'package:smart_farming_mobile/screens/scan/result_detail_sheet.dart';
import 'package:smart_farming_mobile/screens/settings/settings_screen.dart';
import 'package:smart_farming_mobile/screens/splash/language_splash_screen.dart';
import 'package:smart_farming_mobile/screens/today/today_screen.dart';
import 'package:smart_farming_mobile/screens/weather/weather_screen.dart';
import 'package:smart_farming_mobile/services/api_service.dart';
import 'package:smart_farming_mobile/services/offline_queue_db.dart';
import 'package:smart_farming_mobile/services/sync_service.dart';
import 'package:smart_farming_mobile/theme/app_theme.dart';

class _MockApiService extends ApiService {
  _MockApiService() : super(baseUrl: 'https://smart-farming-backend-kkty.onrender.com', accessToken: 'test-token');

  @override
  Future<List<String>> getSupportedCrops() async => ['Cotton', 'Groundnut', 'Pepper_Bell', 'Potato', 'Tomato'];

  @override
  Future<Prediction> getPrediction(int id) async => _samplePrediction();

  @override
  Future<Map<String, dynamic>> translatePrediction(int id, String language) async => {
        'prediction_id': id,
        'language': language,
        'cached': true,
        'recommendation': {'immediate_action': 'Inspect affected leaves.', 'treatment': 'Follow KVK advice.'},
      };

  @override
  Future<String?> translateWeatherAdvisory(String text, String targetLanguage) async => text;
}

Prediction _samplePrediction() => Prediction.fromJson({
      'prediction_id': 91,
      'created_at': '2026-11-26T20:03:00Z',
      'crop': {'label': 'Tomato', 'confidence': 0.96},
      'disease': {'label': 'Bacterial Spot', 'confidence': 0.89},
      'severity': {'percent': 24.5, 'bucket': 'Mild'},
      'pests': [
        {'label': 'Leaf Miner', 'confidence': 0.78},
      ],
      'pest_classification': {'status': 'pest_detected', 'available': true},
      'weather': {
        'temperature_celsius': 21.04,
        'humidity_percent': 43,
        'condition': 'broken clouds',
      },
      'recommendation': {
        'immediate_action': 'Isolate severely infected leaves.',
        'treatment': 'Apply copper-based spray after local KVK confirmation.',
        'prevention': 'Avoid overhead irrigation.',
        'monitoring': 'Re-inspect every 48 hours.',
        'is_fallback': false,
        'farm_aware': true,
        'sources': ['ICAR Integrated Pest Management Guidelines'],
      },
      'translations': {
        'gu': {
          'immediate_action': 'ગંભીર રીતે સંક્રમિત પાંદડા દૂર કરો.',
          'treatment': 'સ્થાનિક KVK ની પુષ્ટિ પછી કોપર-આધારિત છંટકાવ કરો.',
          'prevention': 'ઓવરહેડ સિંચાઈ ટાળો.',
          'monitoring': 'દર 48 કલાકે ફરી તપાસ કરો.',
        },
      },
      'status': {'pipeline': 'completed', 'expert_review': 'not_requested'},
      'plot': {'id': 5, 'name': 'Plot #1', 'crop': 'Tomato', 'area_acres': 10.46},
      'farm': {'id': 12, 'name': 'Rajasthali Farm', 'location': 'Bhavnagar, Gujarat', 'area_acres': 22.92},
    });

Widget _wrap(Widget child, LocaleProvider localeProvider) {
  return LocaleScope(
    notifier: localeProvider,
    child: MaterialApp(
      theme: AppTheme.lightTheme,
      home: MediaQuery(
        data: const MediaQueryData(size: Size(412, 915)),
        child: Scaffold(body: child),
      ),
    ),
  );
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  late LocaleProvider localeProvider;
  late _MockApiService api;
  late Map<String, dynamic> userProfile;
  late Map<String, dynamic> farm;
  late Map<String, dynamic> weather;
  late List<Map<String, dynamic>> alerts;
  late Prediction samplePred;

  setUp(() {
    SharedPreferences.setMockInitialValues({'smart_farm_lang': 'English'});
    localeProvider = LocaleProvider();
    api = _MockApiService();
    samplePred = _samplePrediction();
    userProfile = {
      'id': 'user-1',
      'name': 'Manthan Kuvadiya',
      'email': 'mgkuvadiya28@gmail.com',
      'role': 'farmer',
      'location': 'Bhavnagar, Gujarat',
      'language': 'English',
      'latitude': 21.8677,
      'longitude': 71.7904,
    };
    farm = {
      'id': 12,
      'name': 'Rajasthali Farm',
      'location': 'Bhavnagar, Gujarat',
      'area_acres': 22.92,
      'latitude': 21.8677,
      'longitude': 71.7904,
      'plots': [
        {'id': 5, 'name': 'Plot #1', 'crop': 'Cotton', 'area_acres': 10.46, 'status': 'Active'},
      ],
    };
    weather = {
      'temperature_celsius': 21.04,
      'humidity_percent': 43,
      'condition': 'broken clouds',
      'wind_speed_mps': 3.35,
      'advisory': 'Conditions favorable for scouting.',
    };
    alerts = [
      {
        'id': 1,
        'prediction_id': 91,
        'kind': 'disease',
        'title': 'High disease risk detected',
        'body': 'Inspect Tomato leaves in Plot #1.',
        'is_read': false,
        'created_at': '2026-11-26T20:05:00Z',
      },
    ];
  });

  group('All Mobile App Modules Smoke & Widget Tests', () {
    testWidgets('LanguageSplashScreen renders and switches language selection', (tester) async {
      bool confirmed = false;
      await tester.pumpWidget(_wrap(LanguageSplashScreen(onLanguageConfirmed: () => confirmed = true), localeProvider));
      await tester.pumpAndSettle();

      expect(find.text('Smart Farm AI'), findsOneWidget);
      await tester.tap(find.text('ગુજરાતી'));
      await tester.pumpAndSettle();
      expect(localeProvider.currentLanguage, 'Gujarati');

      await tester.tap(find.text('આગળ વધો (Continue)'));
      await tester.pump();
      expect(confirmed, isTrue);
    });

    testWidgets('LoginScreen renders auth fields, toggle to register, and guest mode button', (tester) async {
      await tester.pumpWidget(_wrap(LoginScreen(onLoggedIn: (_, _) {}), localeProvider));
      await tester.pumpAndSettle();

      expect(find.byType(TextField), findsNWidgets(2));
      // Toggle to Register mode adds Name & Location fields
      await tester.ensureVisible(find.text(localeProvider.tr('dontHaveAccount')));
      await tester.tap(find.text(localeProvider.tr('dontHaveAccount')));
      await tester.pumpAndSettle();
      expect(find.byType(TextField), findsNWidgets(4));
    });

    testWidgets('TodayScreen renders telemetry, scan CTA, and latest scan card', (tester) async {
      await tester.pumpWidget(_wrap(
        TodayScreen(
          userProfile: userProfile,
          weather: weather,
          pendingCount: 0,
          latestPrediction: samplePred,
          photoBytes: null,
          onScanLeaf: () {},
          onSelectPrediction: (_) {},
          onSeeTrail: () {},
          onLogout: () {},
          onOpenSettings: () {},
          onOpenWeather: () {},
        ),
        localeProvider,
      ));
      await tester.pumpAndSettle();

      expect(find.textContaining('21.04°C'), findsOneWidget);
      expect(find.textContaining('43%'), findsOneWidget);
      expect(find.text('Bacterial Spot'), findsOneWidget);
    });

    testWidgets('FarmScreen renders farm metrics and plot list', (tester) async {
      await tester.pumpWidget(_wrap(
        FarmScreen(
          farm: farm,
          userProfile: userProfile,
          api: api,
          onFarmUpdated: () async {},
        ),
        localeProvider,
      ));
      await tester.pumpAndSettle();

      expect(find.textContaining('Rajasthali Farm'), findsWidgets);
      expect(find.textContaining('Plot #1'), findsWidgets);
    });

    testWidgets('WeatherScreen renders metrics and calculated wind speed km/h', (tester) async {
      await tester.pumpWidget(_wrap(
        WeatherScreen(
          weather: weather,
          api: api,
          onRefresh: () async {},
        ),
        localeProvider,
      ));
      await tester.pumpAndSettle();

      expect(find.text('21.04°C'), findsOneWidget);
      // 3.35 m/s * 3.6 = 12.1 km/h
      expect(find.textContaining('12.1 km/h'), findsOneWidget);
      expect(find.textContaining('Conditions favorable'), findsOneWidget);
    });

    testWidgets('AlertsScreen renders alerts and filter tabs work', (tester) async {
      await tester.pumpWidget(_wrap(
        AlertsScreen(
          alerts: alerts,
          api: api,
          onRefresh: () async {},
        ),
        localeProvider,
      ));
      await tester.pumpAndSettle();

      expect(find.textContaining('Inspect Tomato leaves'), findsOneWidget);
      await tester.tap(find.textContaining(localeProvider.tr('weatherTab')));
      await tester.pumpAndSettle();
      expect(find.text(localeProvider.tr('noAlerts')), findsOneWidget);
    });

    testWidgets('HistoryScreen filters scans by crop and search query', (tester) async {
      await tester.pumpWidget(_wrap(
        HistoryScreen(
          history: [samplePred],
          onSelectPrediction: (_) {},
          onRefresh: () async {},
        ),
        localeProvider,
      ));
      await tester.pumpAndSettle();

      expect(find.text('Bacterial Spot'), findsOneWidget);
      await tester.enterText(find.byType(TextField), 'Nonexistent');
      await tester.pumpAndSettle();
      expect(find.text('Bacterial Spot'), findsNothing);
    });

    testWidgets('SettingsScreen loads supported crops and switches units/language', (tester) async {
      await tester.pumpWidget(_wrap(
        SettingsScreen(
          userProfile: userProfile,
          farm: farm,
          api: api,
          onLogout: () {},
        ),
        localeProvider,
      ));
      await tester.pumpAndSettle();

      expect(find.text('Manthan Kuvadiya'), findsOneWidget);
      await tester.scrollUntilVisible(find.text('Cotton'), 200);
      expect(find.text('Cotton'), findsOneWidget);
      expect(find.text('Tomato'), findsOneWidget);

      await tester.scrollUntilVisible(find.text('ગુજરાતી (Gujarati)'), -200);
      await tester.tap(find.text('ગુજરાતી (Gujarati)'));
      await tester.pumpAndSettle();
      expect(localeProvider.currentLanguage, 'Gujarati');
    });

    testWidgets('CameraScreen renders guidance overlay and camera controls', (tester) async {
      await tester.pumpWidget(_wrap(CameraScreen(onCaptured: (_, _) {}), localeProvider));
      await tester.pumpAndSettle();

      expect(find.byIcon(Icons.camera_alt), findsOneWidget);
      expect(find.byIcon(Icons.photo_library_outlined), findsOneWidget);
    });

    testWidgets('CreatePredictionSheet & ResultDetailSheet render diagnosis and advisory details', (tester) async {
      final sync = SyncService(api, queueDb: OfflineQueueDb());
      final validPng = Uint8List.fromList(base64Decode(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==',
      ));
      await tester.pumpWidget(_wrap(
        CreatePredictionSheet(
          api: api,
          sync: sync,
          user: userProfile,
          farm: farm,
          initialBytes: validPng,
          onStarted: (_, _, _) {},
        ),
        localeProvider,
      ));
      await tester.pumpAndSettle();
      expect(find.text(localeProvider.tr('diagnoseCropLeaf')), findsOneWidget);

      await tester.pumpWidget(_wrap(
        ResultDetailSheet(
          prediction: samplePred,
          api: api,
          onFeedbackSubmitted: () {},
        ),
        localeProvider,
      ));
      await tester.pumpAndSettle();

      expect(find.text('Bacterial Spot'), findsWidgets);
      expect(find.textContaining('Leaf Miner'), findsOneWidget);
      await tester.scrollUntilVisible(find.textContaining('Isolate severely infected leaves.'), 200);
      expect(find.textContaining('Isolate severely infected leaves.'), findsOneWidget);
    });
  });
}
