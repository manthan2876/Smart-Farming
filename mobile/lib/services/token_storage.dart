import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class TokenStorage {
  static const _storage = FlutterSecureStorage(
    aOptions: AndroidOptions(encryptedSharedPreferences: true),
    iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
  );

  static const _tokenKey = 'auth_token';

  /// Reads auth token securely, seamlessly migrating any legacy SharedPreferences token.
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

  /// Saves the token securely in Android Keystore / iOS Keychain.
  static Future<void> saveToken(String token) async {
    try {
      await _storage.write(key: _tokenKey, value: token);
    } catch (_) {}
  }

  /// Clears the auth token from both secure storage and legacy preferences.
  static Future<void> clearToken() async {
    try {
      await _storage.delete(key: _tokenKey);
    } catch (_) {}
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.remove(_tokenKey);
    } catch (_) {}
  }
}

