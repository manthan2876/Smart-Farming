import 'package:flutter/material.dart';
import '../../providers/locale_provider.dart';
import '../../services/api_service.dart';
import '../../services/tts_service.dart';
import '../../theme/app_theme.dart';

class WeatherScreen extends StatefulWidget {
  const WeatherScreen({
    super.key,
    required this.weather,
    this.api,
    this.onRefresh,
  });

  final Map<String, dynamic>? weather;
  final ApiService? api;
  final Future<void> Function()? onRefresh;

  @override
  State<WeatherScreen> createState() => _WeatherScreenState();
}

class _WeatherScreenState extends State<WeatherScreen> {
  final TtsService _ttsService = TtsService.instance;
  String? _dynamicTranslatedAdvisory;
  String? _dynamicLangCode;
  bool _translating = false;

  @override
  void initState() {
    super.initState();
    _ttsService.addListener(_onTtsChange);
  }

  void _onTtsChange() {
    if (mounted) setState(() {});
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _checkDynamicTranslation();
  }

  @override
  void didUpdateWidget(covariant WeatherScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.weather != widget.weather) {
      _dynamicTranslatedAdvisory = null;
      _checkDynamicTranslation();
    }
  }

  Future<void> _checkDynamicTranslation() async {
    final langCode = context.localeCode;
    if (langCode == 'en') return;

    final weather = widget.weather;
    if (weather == null) return;

    final translations = weather['translations'] as Map<String, dynamic>?;
    if (translations != null && translations[langCode] != null) {
      return; // Already present in backend response
    }

    if (_dynamicLangCode == langCode && _dynamicTranslatedAdvisory != null) {
      return; // Already dynamically translated
    }

    if (_translating || widget.api == null) return;

    final baseAdvisory = weather['advisory']?.toString();
    if (baseAdvisory == null || baseAdvisory.trim().isEmpty) return;

    setState(() => _translating = true);
    try {
      final translated = await widget.api!.translateWeatherAdvisory(baseAdvisory, langCode);
      if (translated != null && translated.trim().isNotEmpty && mounted) {
        setState(() {
          _dynamicTranslatedAdvisory = translated;
          _dynamicLangCode = langCode;
        });
      }
    } catch (_) {
    } finally {
      if (mounted) setState(() => _translating = false);
    }
  }

  @override
  void dispose() {
    _ttsService.removeListener(_onTtsChange);
    if (_ttsService.isItemPlaying('weather_advisory')) {
      _ttsService.stop();
    }
    super.dispose();
  }

  Future<void> _toggleTts({
    required String temp,
    required String cond,
    required String hum,
    required String advisory,
    required String langCode,
  }) async {
    final buffer = StringBuffer();
    if (langCode == 'hi') {
      buffer.write('मौसम रिपोर्ट: ');
      if (temp != '--') buffer.write('तापमान $temp, ');
      buffer.write('स्थिति $cond, ');
      if (hum != '--') buffer.write('आर्द्रता $hum. ');
      buffer.write('कृषि सलाह: $advisory');
    } else if (langCode == 'gu') {
      buffer.write('હવામાન અહેવાલ: ');
      if (temp != '--') buffer.write('તાપમાન $temp, ');
      buffer.write('સ્થિતિ $cond, ');
      if (hum != '--') buffer.write('ભેજ $hum. ');
      buffer.write('ખેતી સલાહ: $advisory');
    } else {
      buffer.write('Weather report: ');
      if (temp != '--') buffer.write('Temperature $temp, ');
      buffer.write('Condition $cond, ');
      if (hum != '--') buffer.write('Humidity $hum. ');
      buffer.write('Agronomic advisory: $advisory');
    }

    await _ttsService.toggle(
      id: 'weather_advisory',
      text: buffer.toString(),
      langCode: langCode,
      api: widget.api,
    );
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
        (langCode == _dynamicLangCode ? _dynamicTranslatedAdvisory : null) ??
        weather?['translated_advisory']?.toString() ??
        weather?['advisory']?.toString() ??
        context.tr('weatherAdvisoryOptimal');

    final isPlaying = _ttsService.isItemPlaying('weather_advisory');
    final isAudioLoading = _ttsService.isItemLoading('weather_advisory');

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
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              context.tr('weatherTitle'),
              style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w600),
            ),
            if (widget.onRefresh != null)
              IconButton(
                onPressed: widget.onRefresh,
                icon: const Icon(Icons.refresh, color: AppColors.primary),
                tooltip: context.tr('refresh'),
              ),
          ],
        ),
        const SizedBox(height: 22),
        if (weather == null) ...[
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              color: AppColors.primaryLight,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: Row(
              children: [
                const SizedBox(
                  width: 24,
                  height: 24,
                  child: CircularProgressIndicator(strokeWidth: 2.5, color: AppColors.primary),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Text(
                    context.tr('loading'),
                    style: const TextStyle(fontWeight: FontWeight.w600, color: AppColors.primary),
                  ),
                ),
                if (widget.onRefresh != null)
                  TextButton(
                    onPressed: widget.onRefresh,
                    child: Text(context.tr('refresh')),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 16),
        ],
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
                  if (_translating)
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 8),
                      child: SizedBox(
                        width: 16,
                        height: 16,
                        child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
                      ),
                    ),
                  if (isAudioLoading)
                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 12),
                      child: SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
                      ),
                    )
                  else
                    IconButton(
                      icon: Icon(
                        isPlaying ? Icons.stop_circle_outlined : Icons.volume_up,
                        color: isPlaying ? AppColors.warning : AppColors.primary,
                      ),
                      tooltip: isPlaying ? context.tr('pauseAudio') : context.tr('listenAdvisory'),
                      onPressed: () => _toggleTts(
                        temp: temp,
                        cond: cond,
                        hum: hum,
                        advisory: advisory,
                        langCode: langCode,
                      ),
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
