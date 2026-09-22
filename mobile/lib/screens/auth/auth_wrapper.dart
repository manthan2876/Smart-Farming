import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';
import '../../utils/app_logger.dart';
import '../shell/farmer_shell.dart';
import 'login_screen.dart';

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({super.key});

  @override
  State<AuthWrapper> createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _loading = true;
  String? _token;
  Map<String, dynamic>? _user;

  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    final prefs = await SharedPreferences.getInstance();
    final savedToken = prefs.getString('auth_token');
    if (savedToken != null && savedToken.isNotEmpty) {
      AppLogger.info('AuthWrapper', 'Found stored auth token. Validating user session...');
      final api = ApiService(accessToken: savedToken);
      try {
        final profile = await api.getProfile();
        final role = profile['role']?.toString().toLowerCase();
        if (role == 'farmer') {
          AppLogger.info('AuthWrapper', 'Session restored successfully for ${profile['name']} (role: farmer).');
          if (mounted) {
            setState(() {
              _token = savedToken;
              _user = profile;
              _loading = false;
            });
          }
          return;
        } else {
          AppLogger.warn('AuthWrapper', 'User has role "$role" but mobile app is restricted to farmers. Clearing session.');
          await prefs.remove('auth_token');
        }
      } catch (e) {
        AppLogger.warn('AuthWrapper', 'Stored token is expired or invalid: $e. Prompting login.');
        await prefs.remove('auth_token');
      }
    } else {
      AppLogger.info('AuthWrapper', 'No stored auth token found. Displaying login screen.');
    }
    if (mounted) {
      setState(() {
        _token = null;
        _user = null;
        _loading = false;
      });
    }
  }

  void _onLoggedIn(String token, Map<String, dynamic> user) async {
    AppLogger.info('AuthWrapper', 'Farmer logged in successfully: ${user['name']} (${user['email'] ?? user['phone']})');
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('auth_token', token);
    if (mounted) {
      setState(() {
        _token = token;
        _user = user;
      });
    }
  }

  void _onLoggedOut() async {
    AppLogger.info('AuthWrapper', 'Farmer logged out. Clearing local session.');
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
    if (mounted) {
      setState(() {
        _token = null;
        _user = null;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(
          child: CircularProgressIndicator(color: AppColors.primary),
        ),
      );
    }
    if (_token != null && _user != null) {
      return FarmerShell(
        token: _token!,
        user: _user!,
        onLogout: _onLoggedOut,
      );
    }
    return LoginScreen(onLoggedIn: _onLoggedIn);
  }
}

