import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';
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
      final api = ApiService(accessToken: savedToken);
      try {
        final profile = await api.getProfile();
        final role = profile['role']?.toString().toLowerCase();
        if (role == 'farmer') {
          if (mounted) {
            setState(() {
              _token = savedToken;
              _user = profile;
              _loading = false;
            });
          }
          return;
        } else {
          // Log out non-farmer immediately
          await prefs.remove('auth_token');
        }
      } catch (_) {
        await prefs.remove('auth_token');
      }
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

