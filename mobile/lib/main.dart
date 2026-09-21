import 'package:flutter/material.dart';
import 'providers/locale_provider.dart';
import 'screens/auth/auth_wrapper.dart';
import 'theme/app_theme.dart';

void main() => runApp(const RootApp());

class RootApp extends StatefulWidget {
  const RootApp({super.key});

  @override
  State<RootApp> createState() => _RootAppState();
}

class _RootAppState extends State<RootApp> {
  late final LocaleProvider _localeProvider;

  @override
  void initState() {
    super.initState();
    _localeProvider = LocaleProvider();
  }

  @override
  void dispose() {
    _localeProvider.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LocaleScope(
      notifier: _localeProvider,
      child: const FieldnoteApp(),
    );
  }
}

class FieldnoteApp extends StatelessWidget {
  const FieldnoteApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        title: context.tr('appTitle'),
        theme: AppTheme.lightTheme,
        home: const AuthWrapper(),
      );
}
