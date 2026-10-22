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
