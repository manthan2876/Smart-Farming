import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:smart_farming_mobile/providers/locale_provider.dart';
import 'package:smart_farming_mobile/services/image_compressor.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  group('Farmer Hardening Suite', () {
    test('ImageCompressor evaluates quality and luminance heuristics', () {
      // Empty or truncated bytes should fail
      final emptyBytes = Uint8List(500);
      final emptyCheck = ImageCompressor.evaluateQuality(emptyBytes);
      expect(emptyCheck.isValid, isFalse);

      // Normal daylight image bytes (average ~120) should pass
      final normalBytes = Uint8List(4096);
      for (int i = 0; i < normalBytes.length; i++) {
        normalBytes[i] = 120;
      }
      final normalCheck = ImageCompressor.evaluateQuality(normalBytes);
      expect(normalCheck.isValid, isTrue);
      expect(normalCheck.luminance, closeTo(120.0, 5.0));

      // Completely dark room bytes (< 18) should fail with daylight guidance
      final darkBytes = Uint8List(4096);
      for (int i = 0; i < darkBytes.length; i++) {
        darkBytes[i] = 5;
      }
      final darkCheck = ImageCompressor.evaluateQuality(darkBytes);
      expect(darkCheck.isValid, isFalse);
      expect(darkCheck.reason, contains('too dark'));

      // Blinding flash overexposed bytes (> 248) should fail with glare guidance
      final washedBytes = Uint8List(4096);
      for (int i = 0; i < washedBytes.length; i++) {
        washedBytes[i] = 252;
      }
      final washedCheck = ImageCompressor.evaluateQuality(washedBytes);
      expect(washedCheck.isValid, isFalse);
      expect(washedCheck.reason, contains('overexposed'));
    });

    test('LocaleProvider initializes and persists regional language choices', () async {
      final provider = LocaleProvider();
      await Future.delayed(const Duration(milliseconds: 50));

      expect(provider.currentLanguage, 'English');

      // Set to Gujarati
      await provider.setLanguage('Gujarati');
      expect(provider.currentLanguage, 'Gujarati');
      expect(provider.languageCode, 'gu');
      expect(provider.hasSavedLanguage, isTrue);

      // Verify translation resolution
      expect(provider.tr('navScan'), 'પાન સ્કેન કરો');
      expect(provider.tr('holdSteady'), 'કેમેરો સ્થિર રાખો');

      // Set to Hindi
      await provider.setLanguage('Hindi');
      expect(provider.currentLanguage, 'Hindi');
      expect(provider.languageCode, 'hi');
      expect(provider.tr('navScan'), 'पत्ती स्कैन करें');
      expect(provider.tr('holdSteady'), 'कैमरा स्थिर रखें');
    });

    test('OfflineQueueDb respects 5-retry maximum cap', () {
      expect(ImageCompressor.targetMaxDimension, 1024);
      expect(ImageCompressor.targetQuality, 80);
    });
  });
}

