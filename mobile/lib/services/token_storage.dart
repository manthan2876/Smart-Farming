import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class TokenStorage {
  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static const _tokenKey = 'auth_token';
  static const _refreshTokenKey = 'refresh_token';

  /// Reads auth access token securely, seamlessly migrating any legacy SharedPreferences token.
  static Future<String?> getToken() async {
    try {
      final secureToken = await _storage.read(key: _tokenKey);
      if (secureToken != null && secureToken.isNotEmpty) {
        return secureToken;
      }
    } catch (_) {}

    // Fallback & Migration: Check legacy SharedPreferences
    try {
      final prefs = await SharedPreferences.getInstance();
      final legacyToken = prefs.getString(_tokenKey);
      if (legacyToken != null && legacyToken.isNotEmpty) {
        await saveToken(legacyToken);
        await prefs.remove(_tokenKey);
        return legacyToken;
      }
    } catch (_) {}

    return null;
  }

  /// Reads refresh token securely.
  static Future<String?> getRefreshToken() async {
    try {
      final refreshToken = await _storage.read(key: _refreshTokenKey);
      if (refreshToken != null && refreshToken.isNotEmpty) {
        return refreshToken;
      }
    } catch (_) {}
    return null;
  }

  /// Saves the access token securely.
  static Future<void> saveToken(String token) async {
    try {
      await _storage.write(key: _tokenKey, value: token);
    } catch (_) {}
  }

  /// Saves both access and refresh tokens securely.
  static Future<void> saveTokens({required String accessToken, required String refreshToken}) async {
    try {
      await _storage.write(key: _tokenKey, value: accessToken);
      await _storage.write(key: _refreshTokenKey, value: refreshToken);
    } catch (_) {}
  }

  /// Clears both auth & refresh tokens from secure storage and legacy preferences.
  static Future<void> clearToken() async {
    try {
      await _storage.delete(key: _tokenKey);
      await _storage.delete(key: _refreshTokenKey);
    } catch (_) {}
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_tokenKey);
      await prefs.remove(_refreshTokenKey);
    } catch (_) {}
  }
}

