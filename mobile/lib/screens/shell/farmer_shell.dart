import 'dart:async';
import 'dart:typed_data';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/material.dart';
import '../../models/prediction.dart';
import '../../providers/locale_provider.dart';
import '../../i18n/domain_translations.dart';
import '../../services/api_service.dart';
import '../../services/sync_service.dart';
import '../../services/tts_service.dart';
import '../../utils/app_logger.dart';
import '../../theme/app_theme.dart';
import '../alerts/alerts_screen.dart';
import '../farm/farm_screen.dart';
import '../history/history_screen.dart';
import '../scan/create_prediction_sheet.dart';
import '../scan/processing_sheet.dart';
import '../scan/result_detail_sheet.dart';
import '../today/today_screen.dart';
import '../weather/weather_screen.dart';

class FarmerShell extends StatefulWidget {
  const FarmerShell({
    super.key,
    required this.token,
    required this.user,
    required this.onLogout,
  });

  final String token;
  final Map<String, dynamic> user;
  final VoidCallback onLogout;

  @override
  State<FarmerShell> createState() => _FarmerShellState();
}

class _FarmerShellState extends State<FarmerShell> {
  late final ApiService _api = ApiService(accessToken: widget.token);
  late final SyncService _sync = SyncService(_api);

  int _tab = 0;
  Uint8List? _photoBytes;
  int _pending = 0;

  Prediction? _latest;
  final _history = <Prediction>[];
  late Map<String, dynamic> _userProfile = widget.user;
  Map<String, dynamic>? _farm;
  Map<String, dynamic>? _weather;
  List<Map<String, dynamic>> _alerts = [];
  String? _lastLocale;

  @override
  void initState() {
    super.initState();
    _refreshQueue();
    _listenConnectivity();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        _loadAllData();
      }
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final currentLocale = context.localeCode;
    if (_lastLocale != null && _lastLocale != currentLocale) {
      _lastLocale = currentLocale;
      _loadWeather();
    } else {
      _lastLocale = currentLocale;
    }
  }

  void _listenConnectivity() {
    Connectivity().onConnectivityChanged.listen((results) async {
      if (!results.contains(ConnectivityResult.none)) {
        final synced = await _sync.drain();
        if (synced > 0) {
          await _refreshQueue();
          await _loadHistory();
        }
      }
    });
  }

  Future<void> _refreshQueue() async {
    final count = await _sync.pendingCount();
    if (mounted) setState(() => _pending = count);
  }

  Future<void> _loadAllData() async {
    AppLogger.info('FarmerShell', 'Initializing mobile session data for user: ${_userProfile['email'] ?? _userProfile['name']}');
    await Future.wait([
      _loadHistory(),
      _loadProfile(),
      _loadFarm(),
      _loadWeather(),
      _loadAlerts(),
    ]);
  }

  Future<void> _loadHistory() async {
    AppLogger.info('FarmerShell', 'Fetching past scan history from API...');
    try {
      final items = await _api.history();
      AppLogger.info('FarmerShell', 'Received ${items.length} scan records.');
      if (mounted) {
        setState(() {
          _history
            ..clear()
            ..addAll(items);
          if (items.isNotEmpty) {
            _latest ??= items.first;
          }
        });
        AppLogger.info('FarmerShell', 'UI state updated with ${_history.length} scans (Latest: ${_latest?.id} ${_latest?.disease}).');
      }
    } catch (e, stack) {
      AppLogger.error('FarmerShell', 'Failed to load scan history: $e', e, stack);
    }
  }

  Future<void> _loadProfile() async {
    try {
      final profile = await _api.getProfile();
      AppLogger.info('FarmerShell', 'Profile loaded for ${profile['name']} (${profile['email'] ?? profile['phone']})');
      if (mounted) setState(() => _userProfile = profile);
    } catch (e, stack) {
      AppLogger.error('FarmerShell', 'Failed to load profile: $e', e, stack);
    }
  }

  Future<void> _loadFarm() async {
    try {
      final farm = await _api.getFarm();
      AppLogger.info('FarmerShell', 'Farm data loaded: ${farm['name'] ?? 'None'} (${farm['area_acres'] ?? 0} acres)');
      if (mounted) {
        setState(() => _farm = farm);
        if (_weather == null && farm['latitude'] != null) {
          _loadWeather();
        }
      }
    } catch (e, stack) {
      AppLogger.error('FarmerShell', 'Failed to load farm: $e', e, stack);
    }
  }

  Future<void> _loadWeather() async {
    try {
      final lang = context.mounted
          ? context.localeCode
          : DomainTranslations.normalizeLang(_userProfile['language']?.toString());
      final lat = double.tryParse(_farm?['latitude']?.toString() ?? '') ??
          double.tryParse(_userProfile['latitude']?.toString() ?? '') ??
          22.2587;
      final lon = double.tryParse(_farm?['longitude']?.toString() ?? '') ??
          double.tryParse(_userProfile['longitude']?.toString() ?? '') ??
          71.1924;

      final weather = await _api.getWeather(lat: lat, lon: lon, language: lang);
      AppLogger.info('FarmerShell', 'Weather loaded for ($lat, $lon): ${weather['temperature_celsius']}°C, condition: ${weather['condition']}');
      if (mounted) setState(() => _weather = weather);
    } catch (e, stack) {
      AppLogger.error('FarmerShell', 'Weather load error: $e', e, stack);
    }
  }

  Future<void> _loadAlerts() async {
    try {
      final alerts = await _api.getAlerts();
      AppLogger.info('FarmerShell', 'Alerts loaded: ${alerts.length} total (${alerts.where((a) => a['is_read'] != true).length} unread)');
      if (mounted) setState(() => _alerts = alerts);
    } catch (e, stack) {
      AppLogger.error('FarmerShell', 'Failed to load alerts: $e', e, stack);
    }
  }

  void _openCreatePredictionModal({Uint8List? initialBytes, String? initialName}) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.cardBg,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => CreatePredictionSheet(
        api: _api,
        sync: _sync,
        user: _userProfile,
        farm: _farm,
        initialBytes: initialBytes,
        initialName: initialName,
        onStarted: (predictionId, bytes, name) {
          Navigator.pop(ctx);
          _openProcessingModal(predictionId, bytes);
        },
      ),
    );
  }

  void _openProcessingModal(int predictionId, Uint8List? bytes) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      isDismissible: false,
      enableDrag: false,
      backgroundColor: AppColors.cardBg,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => ProcessingSheet(
        predictionId: predictionId,
        photoBytes: bytes,
        api: _api,
        onComplete: (pred) {
          Navigator.pop(ctx);
          setState(() {
            _latest = pred;
            _photoBytes = bytes;
            _history.removeWhere((p) => p.id == pred.id);
            _history.insert(0, pred);
          });
          _showResultSheet(pred);
        },
        onRescan: () {
          Navigator.pop(ctx);
          _openCreatePredictionModal();
        },
      ),
    );
  }

  Future<void> _speak(String text) async {
    final lang = context.mounted ? context.localeCode : 'en';
    await TtsService.instance.toggle(
      id: 'shell_speak',
      text: text,
      langCode: lang,
    );
  }

  void _showResultSheet(Prediction pred) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: AppColors.cardBg,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => ResultDetailSheet(
        prediction: pred,
        api: _api,
        onSpeak: _speak,
        onFeedbackSubmitted: () => _loadHistory(),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        body: SafeArea(
          child: IndexedStack(
            index: _tab,
            children: [
              TodayScreen(
                userProfile: _userProfile,
                weather: _weather,
                pendingCount: _pending,
                latestPrediction: _latest,
                photoBytes: _photoBytes,
                onScanLeaf: _openCreatePredictionModal,
                onSelectPrediction: _showResultSheet,
                onSeeTrail: () => setState(() => _tab = 1),
                onLogout: widget.onLogout,
              ),
              HistoryScreen(
                history: _history,
                onSelectPrediction: _showResultSheet,
                onRefresh: _loadHistory,
              ),
              WeatherScreen(
                weather: _weather,
                api: _api,
                onRefresh: _loadWeather,
              ),
              FarmScreen(
                farm: _farm,
                userProfile: _userProfile,
                api: _api,
                onFarmUpdated: _loadFarm,
              ),
              AlertsScreen(
                alerts: _alerts,
                api: _api,
                onRefresh: _loadAlerts,
              ),
            ],
          ),
        ),
        bottomNavigationBar: NavigationBar(
          selectedIndex: _tab,
          onDestinationSelected: (index) => setState(() => _tab = index),
          backgroundColor: AppColors.cardBg,
          destinations: [
            NavigationDestination(
              icon: const Icon(Icons.wb_sunny_outlined),
              selectedIcon: const Icon(Icons.wb_sunny),
              label: context.tr('navToday'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.timeline_outlined),
              selectedIcon: const Icon(Icons.timeline),
              label: context.tr('navHistory'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.cloud_outlined),
              selectedIcon: const Icon(Icons.cloud),
              label: context.tr('navWeather'),
            ),
            NavigationDestination(
              icon: const Icon(Icons.yard_outlined),
              selectedIcon: const Icon(Icons.yard),
              label: context.tr('navFarm'),
            ),
            NavigationDestination(
              icon: Badge(
                isLabelVisible: _alerts.any((a) => a['is_read'] != true),
                label: Text('${_alerts.where((a) => a['is_read'] != true).length}'),
                child: const Icon(Icons.notifications_outlined),
              ),
              selectedIcon: const Icon(Icons.notifications),
              label: context.tr('navAlerts'),
            ),
          ],
        ),
      );
}

