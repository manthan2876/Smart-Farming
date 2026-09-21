import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../i18n/domain_translations.dart';

/// Centralized, high-reliability Text-to-Speech manager for the mobile application.
/// Ensures only one audio streams at a time and provides robust cross-platform Play/Stop toggling.
class TtsService with ChangeNotifier {
  TtsService._internal() {
    _initTts();
  }

  static final TtsService instance = TtsService._internal();
  factory TtsService() => instance;

  final FlutterTts _tts = FlutterTts();
  bool _isPlaying = false;
  String? _currentId;

  bool get isPlaying => _isPlaying;
  String? get currentId => _currentId;
  bool isItemPlaying(String id) => _isPlaying && _currentId == id;

  void _initTts() {
    _tts.setStartHandler(() {
      _isPlaying = true;
      notifyListeners();
    });

    _tts.setCompletionHandler(() {
      _isPlaying = false;
      _currentId = null;
      notifyListeners();
    });

    _tts.setErrorHandler((msg) {
      debugPrint('[TtsService] Error: $msg');
      _isPlaying = false;
      _currentId = null;
      notifyListeners();
    });

    _tts.setCancelHandler(() {
      _isPlaying = false;
      _currentId = null;
      notifyListeners();
    });
  }

  /// Sanitizes raw agronomic text by removing markdown artifacts and continuous newlines
  /// that can cause native Android/iOS speech engines to terminate prematurely.
  static String cleanText(String raw) {
    return raw
        .replaceAll(RegExp(r'[*#_~`]+'), ' ')
        .replaceAll(RegExp(r'[\r\n]+'), ' ')
        .replaceAll(RegExp(r'\s+'), ' ')
        .trim();
  }

  /// Sets voice with graceful fallback: Gujarati -> Hindi -> English.
  Future<void> _setVoiceWithFallback(String langCode) async {
    final norm = DomainTranslations.normalizeLang(langCode);
    final targetLang = norm == 'hi'
        ? 'hi-IN'
        : (norm == 'gu' ? 'gu-IN' : 'en-US');

    try {
      final dynamic avail = await _tts.isLanguageAvailable(targetLang);
      final isSupported = avail == true || avail == 1;

      if (isSupported) {
        await _tts.setLanguage(targetLang);
        return;
      }

      // If gu-IN is not installed on the Android device, fallback to Hindi (widely bundled Indic voice)
      if (norm == 'gu') {
        final dynamic hiAvail = await _tts.isLanguageAvailable('hi-IN');
        if (hiAvail == true || hiAvail == 1) {
          await _tts.setLanguage('hi-IN');
          return;
        }
      }

      // Fallback to English
      await _tts.setLanguage('en-US');
    } catch (e) {
      debugPrint('[TtsService] Language config fallback error: $e');
      try {
        await _tts.setLanguage(targetLang);
      } catch (_) {
        await _tts.setLanguage('en-US');
      }
    }
  }

  /// Toggles playback for a specific item identifier.
  /// If the current item is playing, it stops. If another item or none is playing, it starts.
  Future<void> toggle({
    required String id,
    required String text,
    required String langCode,
  }) async {
    if (_isPlaying && _currentId == id) {
      await stop();
      return;
    }

    // Stop any existing stream before starting a new one
    await stop();

    final sanitized = cleanText(text);
    if (sanitized.isEmpty) return;

    _currentId = id;
    _isPlaying = true;
    notifyListeners();

    try {
      await _setVoiceWithFallback(langCode);
      await _tts.setSpeechRate(0.48);
      await _tts.setPitch(1.0);
      await _tts.setVolume(1.0);
      await _tts.awaitSpeakCompletion(true);

      final dynamic res = await _tts.speak(sanitized);
      if (res != null && res == 0) {
        // Failed to speak
        _isPlaying = false;
        _currentId = null;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('[TtsService] speak error: $e');
      _isPlaying = false;
      _currentId = null;
      notifyListeners();
    }
  }

  /// Stops current speech output.
  Future<void> stop() async {
    try {
      await _tts.stop();
    } catch (_) {}
    _isPlaying = false;
    _currentId = null;
    notifyListeners();
  }
}
