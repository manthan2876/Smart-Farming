import 'dart:convert';
import 'package:audioplayers/audioplayers.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../i18n/domain_translations.dart';
import 'api_service.dart';

/// Centralized Text-to-Speech manager for the mobile application.
/// Uses Google Cloud Studio Neural Voices via the backend TTS API as the primary high-fidelity engine,
/// with automatic offline fallback to native on-device speech synthesis.
class TtsService with ChangeNotifier {
  TtsService._internal() {
    _initAudioPlayer();
    _initOnDeviceTts();
  }

  static final TtsService instance = TtsService._internal();
  factory TtsService() => instance;

  final AudioPlayer _player = AudioPlayer();
  final FlutterTts _onDeviceTts = FlutterTts();

  bool _isPlaying = false;
  bool _isLoading = false;
  String? _currentId;

  bool get isPlaying => _isPlaying;
  bool get isLoadingState => _isLoading;
  String? get currentId => _currentId;

  bool isItemPlaying(String id) => _isPlaying && _currentId == id;
  bool isItemLoading(String id) => _isLoading && _currentId == id;

  void _initAudioPlayer() {
    _player.onPlayerStateChanged.listen((state) {
      if (state == PlayerState.playing) {
        _isPlaying = true;
        _isLoading = false;
        notifyListeners();
      } else if (state == PlayerState.completed || state == PlayerState.stopped) {
        _isPlaying = false;
        _isLoading = false;
        _currentId = null;
        notifyListeners();
      }
    });
  }

  void _initOnDeviceTts() {
    _onDeviceTts.setStartHandler(() {
      _isPlaying = true;
      _isLoading = false;
      notifyListeners();
    });

    _onDeviceTts.setCompletionHandler(() {
      _isPlaying = false;
      _isLoading = false;
      _currentId = null;
      notifyListeners();
    });

    _onDeviceTts.setErrorHandler((msg) {
      debugPrint('[TtsService] On-device TTS error: $msg');
      _isPlaying = false;
      _isLoading = false;
      _currentId = null;
      notifyListeners();
    });

    _onDeviceTts.setCancelHandler(() {
      _isPlaying = false;
      _isLoading = false;
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

  /// Plays synthesized audio via on-device TTS engine (fallback path).
  Future<void> _speakWithOnDeviceTts(String sanitized, String langCode) async {
    final norm = DomainTranslations.normalizeLang(langCode);
    final targetLang = norm == 'hi'
        ? 'hi-IN'
        : (norm == 'gu' ? 'gu-IN' : 'en-US');

    try {
      final dynamic avail = await _onDeviceTts.isLanguageAvailable(targetLang);
      final isSupported = avail == true || avail == 1;

      if (isSupported) {
        await _onDeviceTts.setLanguage(targetLang);
      } else if (norm == 'gu') {
        final dynamic hiAvail = await _onDeviceTts.isLanguageAvailable('hi-IN');
        if (hiAvail == true || hiAvail == 1) {
          await _onDeviceTts.setLanguage('hi-IN');
        } else {
          await _onDeviceTts.setLanguage('en-US');
        }
      } else {
        await _onDeviceTts.setLanguage('en-US');
      }

      await _onDeviceTts.setSpeechRate(0.48);
      await _onDeviceTts.setPitch(1.0);
      await _onDeviceTts.setVolume(1.0);
      await _onDeviceTts.awaitSpeakCompletion(true);

      final dynamic res = await _onDeviceTts.speak(sanitized);
      if (res != null && res == 0) {
        _isPlaying = false;
        _isLoading = false;
        _currentId = null;
        notifyListeners();
      }
    } catch (e) {
      debugPrint('[TtsService] On-device speech error: $e');
      _isPlaying = false;
      _isLoading = false;
      _currentId = null;
      notifyListeners();
    }
  }

  /// Toggles playback for a specific item identifier.
  /// If the current item is playing or loading, it stops.
  /// If another item or none is playing, it synthesizes and starts Google Cloud audio.
  Future<void> toggle({
    required String id,
    required String text,
    required String langCode,
    ApiService? api,
  }) async {
    if ((_isPlaying || _isLoading) && _currentId == id) {
      await stop();
      return;
    }

    // Stop any existing stream before starting a new one
    await stop();

    final sanitized = cleanText(text);
    if (sanitized.isEmpty) return;

    _currentId = id;
    _isLoading = true;
    _isPlaying = false;
    notifyListeners();

    final norm = DomainTranslations.normalizeLang(langCode);

    // 1. Primary: Google Cloud Studio Text-to-Speech via backend API
    if (api != null) {
      try {
        final b64Audio = await api.generateTTS(sanitized, language: norm);
        if (b64Audio != null && b64Audio.isNotEmpty) {
          final audioBytes = base64Decode(b64Audio);
          await _player.play(BytesSource(audioBytes));
          return;
        }
      } catch (e) {
        debugPrint('[TtsService] Google Cloud TTS failed: $e. Falling back to on-device.');
      }
    }

    // 2. Fallback: On-Device TTS engine
    await _speakWithOnDeviceTts(sanitized, langCode);
  }

  /// Stops current speech output from both cloud player and on-device engine.
  Future<void> stop() async {
    try {
      await _player.stop();
    } catch (_) {}
    try {
      await _onDeviceTts.stop();
    } catch (_) {}

    _isPlaying = false;
    _isLoading = false;
    _currentId = null;
    notifyListeners();
  }

  @override
  void dispose() {
    _player.dispose();
    super.dispose();
  }
}
