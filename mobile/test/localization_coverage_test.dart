import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smart_farming_mobile/i18n/app_translations.dart';
import 'package:smart_farming_mobile/models/prediction.dart';
import 'package:smart_farming_mobile/providers/locale_provider.dart';
import 'package:smart_farming_mobile/screens/history/history_screen.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  test('all mobile UI catalog entries exist for supported languages', () {
    for (final language in ['English', 'Hindi', 'Gujarati']) {
      expect(AppTranslations.missingKeysForLanguage(language), isEmpty,
          reason: language);
    }
  });

  test('unknown and unsupported translations fall back to English or the key', () {
    expect(AppTranslations.get('scanHistoryTitle', 'French'), 'Diagnosis History');
    expect(
      AppTranslations.get('missingLocalizationKey', 'Hindi'),
      'missingLocalizationKey',
    );
  });

  test('domain fallback labels follow the selected language', () async {
    final locale = LocaleProvider();
    await locale.setLanguage('Gujarati');
    expect(locale.crop(null), 'અજ્ઞાત પાક');
    expect(locale.crop('Unknown crop'), 'અજ્ઞાત પાક');
    expect(locale.disease(null), 'અનિર્ધારિત સ્થિતિ');
    expect(locale.disease('Unidentified Condition'), 'અજ્ઞાત સ્થિતિ');
    expect(locale.pest(null), 'જીવાત');
    expect(locale.severity(null), 'લાગુ પડતું નથી');
    expect(locale.weather(null), 'વર્તમાન પરિસ્થિતિઓ');
    expect(locale.alertTitle(null), 'ચેતવણી');

    await locale.setLanguage('Hindi');
    expect(locale.crop(null), 'अज्ञात फसल');
    expect(locale.disease(null), 'अनिर्धारित स्थिति');
    expect(locale.pest(null), 'कीट');
    expect(locale.severity(null), 'लागू नहीं');
    expect(locale.weather(null), 'वर्तमान स्थितियाँ');
    expect(locale.alertTitle(null), 'चेतावनी');
  });

  testWidgets('history screen updates when the selected language changes',
      (tester) async {
    final locale = LocaleProvider();
    await locale.setLanguage('English');

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: LocaleScope(
            notifier: locale,
            child: const HistoryScreen(
              history: [],
              onSelectPrediction: _ignorePrediction,
            ),
          ),
        ),
      ),
    );
    expect(find.text('Diagnosis History'), findsOneWidget);

    await locale.setLanguage('Gujarati');
    await tester.pumpAndSettle();
    expect(find.text('નિદાન ઇતિહાસ'), findsOneWidget);

    await locale.setLanguage('Hindi');
    await tester.pumpAndSettle();
    expect(find.text('निदान इतिहास'), findsOneWidget);
  });

  testWidgets('history filter feedback renders in the selected language',
      (tester) async {
    final locale = LocaleProvider();
    await locale.setLanguage('Hindi');
    final prediction = Prediction(
      id: 1,
      crop: 'Tomato',
      disease: 'Early Blight',
      confidence: 0.9,
      severity: 12,
      recommendation: '',
      createdAt: '2026-01-01',
    );

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: LocaleScope(
            notifier: locale,
            child: HistoryScreen(
              history: [prediction],
              onSelectPrediction: (_) {},
            ),
          ),
        ),
      ),
    );
    await tester.enterText(find.byType(TextField), 'cucumber');
    await tester.pumpAndSettle();

    expect(find.text('"cucumber" से कोई स्कैन मेल नहीं खाता'), findsOneWidget);
    expect(find.text('0 स्कैन'), findsOneWidget);
    expect(find.text('फ़िल्टर हटाएं'), findsOneWidget);
  });
}

void _ignorePrediction(Prediction _) {}
