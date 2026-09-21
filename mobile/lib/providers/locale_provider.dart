import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../i18n/app_translations.dart';
import '../i18n/domain_translations.dart';

class LocaleProvider extends ChangeNotifier {
  LocaleProvider() {
    _loadSavedLanguage();
  }

  static const String _prefKey = 'smart_farm_lang';
  String _currentLanguage = 'English';

  String get currentLanguage => _currentLanguage;
  String get languageCode => DomainTranslations.normalizeLang(_currentLanguage);

  Future<void> _loadSavedLanguage() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final saved = prefs.getString(_prefKey);
      if (saved != null && (saved == 'English' || saved == 'Hindi' || saved == 'Gujarati')) {
        _currentLanguage = saved;
        notifyListeners();
      }
    } catch (_) {}
  }

  Future<void> setLanguage(String newLang) async {
    if (_currentLanguage == newLang) return;
    _currentLanguage = newLang;
    notifyListeners();
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_prefKey, newLang);
    } catch (_) {}
  }

  String tr(String key) => AppTranslations.get(key, _currentLanguage);
  String crop(String? name) => DomainTranslations.translateCrop(name, _currentLanguage);
  String disease(String? name) => DomainTranslations.translateDisease(name, _currentLanguage);
  String pest(String? name) => DomainTranslations.translatePest(name, _currentLanguage);
  String severity(String? bucket) => DomainTranslations.translateSeverityBucket(bucket, _currentLanguage);
  String severityPercent(int percent) {
    final bucket = percent < 25
        ? 'low'
        : percent < 55
            ? 'moderate'
            : percent < 80
                ? 'high'
                : 'critical';
    return DomainTranslations.translateSeverityBucket(bucket, _currentLanguage);
  }
  String weather(String? condition) => DomainTranslations.translateWeather(condition, _currentLanguage);
}

/// InheritedWidget wrapper so any widget can easily read LocaleProvider
class LocaleScope extends InheritedNotifier<LocaleProvider> {
  const LocaleScope({
    super.key,
    required LocaleProvider notifier,
    required super.child,
  }) : super(notifier: notifier);

  static LocaleProvider of(BuildContext context) {
    final scope = context.dependOnInheritedWidgetOfExactType<LocaleScope>();
    if (scope == null || scope.notifier == null) {
      throw StateError('LocaleScope not found in widget tree.');
    }
    return scope.notifier!;
  }
}

/// Convenience extension on BuildContext for clean syntax: context.tr('key')
extension LocaleContextX on BuildContext {
  LocaleProvider get loc => LocaleScope.of(this);
  String tr(String key) => LocaleScope.of(this).tr(key);
}

/// Reusable Language Selector Sheet
Future<void> showLanguageSelectionSheet(BuildContext context) async {
  final provider = LocaleScope.of(context);
  final current = provider.currentLanguage;

  final options = [
    {'title': 'English', 'subtitle': 'English', 'value': 'English'},
    {'title': 'हिन्दी', 'subtitle': 'Hindi', 'value': 'Hindi'},
    {'title': 'ગુજરાતી', 'subtitle': 'Gujarati', 'value': 'Gujarati'},
  ];

  await showModalBottomSheet<void>(
    context: context,
    shape: const RoundedRectangleBorder(
      borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
    ),
    builder: (ctx) {
      return SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Padding(
                padding: const EdgeInsets.only(left: 8, bottom: 12),
                child: Text(
                  provider.tr('selectLanguage'),
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
              ...options.map((opt) {
                final isSelected = opt['value'] == current;
                return ListTile(
                  leading: Icon(
                    isSelected ? Icons.radio_button_checked : Icons.radio_button_off,
                    color: isSelected ? const Color(0xff2d6a4f) : Colors.grey,
                  ),
                  title: Text(
                    opt['title']!,
                    style: TextStyle(
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      color: isSelected ? const Color(0xff2d6a4f) : null,
                    ),
                  ),
                  subtitle: Text(opt['subtitle']!),
                  trailing: isSelected
                      ? const Icon(Icons.check, color: Color(0xff2d6a4f))
                      : null,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  tileColor: isSelected ? const Color(0xffd8f3dc).withAlpha(100) : null,
                  onTap: () {
                    provider.setLanguage(opt['value']!);
                    Navigator.pop(ctx);
                  },
                );
              }),
            ],
          ),
        ),
      );
    },
  );
}
