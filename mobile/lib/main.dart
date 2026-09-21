import 'package:flutter/material.dart';
import 'screens/auth/auth_wrapper.dart';
import 'theme/app_theme.dart';

void main() => runApp(const FieldnoteApp());

class FieldnoteApp extends StatelessWidget {
  const FieldnoteApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Smart Farming',
        theme: AppTheme.lightTheme,
        home: const AuthWrapper(),
      );
}
