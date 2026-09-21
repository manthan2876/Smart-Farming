import 'package:flutter/material.dart';

class AppColors {
  static const primary = Color(0xff276b52);
  static const primaryDark = Color(0xff20312b);
  static const primaryLight = Color(0xffe5eee2);
  static const primaryBorder = Color(0xffb8d3b7);
  static const accent = Color(0xffffd681);
  static const background = Color(0xfff4f1e8);
  static const cardBg = Color(0xfffbfaf5);
  static const cardBorder = Color(0xffdddcd1);
  static const textPrimary = Color(0xff20312b);
  static const textMuted = Color(0xff728079);
  static const textSubtle = Color(0xff8c968c);
  static const warning = Color(0xffd66d43);
  static const warningBg = Color(0xffffe8c6);
  static const warningText = Color(0xff866b47);
}

class AppTheme {
  static ThemeData get lightTheme => ThemeData(
        useMaterial3: true,
        scaffoldBackgroundColor: AppColors.background,
        colorScheme: ColorScheme.fromSeed(
          seedColor: AppColors.primary,
          brightness: Brightness.light,
        ),
        fontFamily: 'sans',
      );
}

