import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../../providers/locale_provider.dart';
import '../../theme/app_theme.dart';

class WeatherScreen extends StatefulWidget {
  const WeatherScreen({
    super.key,
    required this.weather,
    this.onRefresh,
  });

  final Map<String, dynamic>? weather;
  final Future<void> Function()? onRefresh;

  @override
  State<WeatherScreen> createState() => _WeatherScreenState();
}

class _WeatherScreenState extends State<WeatherScreen> {
  final FlutterTts _tts = FlutterTts();
  bool _isPlaying = false;
  bool _isPaused = false;

  @override
  void initState() {
    super.initState();
    _tts.setStartHandler(() {
      if (mounted) setState(() { _isPlaying = true; _isPaused = false; });
    });
    _tts.setCompletionHandler(() {
      if (mounted) setState(() { _isPlaying = false; _isPaused = false; });
    });
    _tts.setPauseHandler(() {
      if (mounted) setState(() { _isPlaying = false; _isPaused = true; });
    });
    _tts.setContinueHandler(() {
      if (mounted) setState(() { _isPlaying = true; _isPaused = false; });
    });
    _tts.setErrorHandler((_) {
      if (mounted) setState(() { _isPlaying = false; _isPaused = false; });
    });
  }

  @override
  void dispose() {
    _tts.stop();
    super.dispose();
  }

  Future<void> _toggleTts(String text, String langCode) async {
    if (_isPlaying) {
      await _tts.pause();
      if (mounted) setState(() { _isPlaying = false; _isPaused = true; });
    } else if (_isPaused) {
      await _tts.speak(text);
      if (mounted) setState(() { _isPlaying = true; _isPaused = false; });
    } else {
      final ttsLang = langCode == 'hi' ? 'hi-IN' : (langCode == 'gu' ? 'gu-IN' : 'en-US');
      await _tts.setLanguage(ttsLang);
      await _tts.setSpeechRate(0.48);
      await _tts.speak(text);
      if (mounted) setState(() { _isPlaying = true; _isPaused = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    final weather = widget.weather;
    final temp = weather?['temperature_celsius'] != null ? '${weather!['temperature_celsius']}°C' : '--';
    final hum = weather?['humidity_percent'] != null ? '${weather!['humidity_percent']}%' : '--';
    final wind = weather?['wind_speed_mps'] != null ? '${weather!['wind_speed_mps']} km/h' : '--';
    final rawCond = weather?['condition']?.toString() ?? 'Clear Sky';
    final cond = context.loc.weather(rawCond);

    final langCode = context.localeCode;
    final translations = weather?['translations'] as Map<String, dynamic>?;
    final advisory = translations?[langCode]?.toString() ??
        weather?['translated_advisory']?.toString() ??
        weather?['advisory']?.toString() ??
        context.tr('weatherAdvisoryOptimal');

    final content = ListView(
      padding: const EdgeInsets.all(22),
      children: [
        Text(
          context.tr('appTitle').toUpperCase(),
          style: const TextStyle(
            letterSpacing: 2,
            color: AppColors.textSubtle,
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          context.tr('weatherTitle'),
          style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 22),
        Container(
          padding: const EdgeInsets.all(24),
          decoration: BoxDecoration(
            color: AppColors.primary,
            borderRadius: BorderRadius.circular(22),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                temp,
                style: const TextStyle(fontSize: 48, fontWeight: FontWeight.bold, color: Colors.white),
              ),
              Text(
                cond.toUpperCase(),
                style: const TextStyle(
                  color: AppColors.primaryBorder,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 1.2,
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('${context.tr('humidity')}: $hum', style: const TextStyle(color: Colors.white70)),
                  Text('${context.tr('windSpeed')}: $wind', style: const TextStyle(color: Colors.white70)),
                ],
              ),
            ],
          ),
        ),
        const SizedBox(height: 24),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.warningBg,
            borderRadius: BorderRadius.circular(18),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  const Icon(Icons.info_outline, color: AppColors.warning),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      context.tr('sprayConditions'),
                      style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.warningText),
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                  IconButton(
                    icon: Icon(_isPlaying ? Icons.pause_circle_filled : Icons.volume_up, color: AppColors.primary),
                    tooltip: _isPlaying ? context.tr('pauseAudio') : context.tr('listenAdvisory'),
                    onPressed: () => _toggleTts(advisory, langCode),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Text(
                advisory,
                style: const TextStyle(color: Color(0xff5d513f), height: 1.5, fontSize: 14),
              ),
            ],
          ),
        ),
      ],
    );

    if (widget.onRefresh != null) {
      return RefreshIndicator(
        onRefresh: widget.onRefresh!,
        color: AppColors.primary,
        child: content,
      );
    }
    return content;
  }
}
