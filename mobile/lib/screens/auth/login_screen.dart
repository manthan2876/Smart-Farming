import 'package:flutter/material.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, required this.onLoggedIn});
  final void Function(String token, Map<String, dynamic> user) onLoggedIn;

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  bool _isRegister = false;
  final _identifierCtrl = TextEditingController();
  final _passwordCtrl = TextEditingController();
  final _nameCtrl = TextEditingController();
  final _locationCtrl = TextEditingController(text: 'Anand, Gujarat');
  String _language = 'English';
  bool _busy = false;
  String? _error;

  @override
  void dispose() {
    _identifierCtrl.dispose();
    _passwordCtrl.dispose();
    _nameCtrl.dispose();
    _locationCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    final api = ApiService();
    try {
      if (_isRegister) {
        if (_nameCtrl.text.trim().isEmpty || _passwordCtrl.text.trim().isEmpty) {
          throw Exception('Please fill in your name and password.');
        }
        final res = await api.register(
          name: _nameCtrl.text.trim(),
          password: _passwordCtrl.text.trim(),
          email: _identifierCtrl.text.contains('@') ? _identifierCtrl.text.trim() : null,
          phone: !_identifierCtrl.text.contains('@') ? _identifierCtrl.text.trim() : null,
          location: _locationCtrl.text.trim(),
          language: _language,
          cropHistory: ['Tomato', 'Cotton'],
        );
        final tokens = res['tokens'] as Map<String, dynamic>;
        final user = res['user'] as Map<String, dynamic>;
        widget.onLoggedIn(tokens['access_token'].toString(), user);
      } else {
        if (_identifierCtrl.text.trim().isEmpty || _passwordCtrl.text.trim().isEmpty) {
          throw Exception('Please enter username and password.');
        }
        final res = await api.login(_identifierCtrl.text.trim(), _passwordCtrl.text.trim());
        final tokens = res['tokens'] as Map<String, dynamic>;
        final user = res['user'] as Map<String, dynamic>;
        widget.onLoggedIn(tokens['access_token'].toString(), user);
      }
    } catch (e) {
      setState(() {
        _error = e.toString().replaceFirst('Exception: ', '');
      });
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(28),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 420),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Container(
                    width: 64,
                    height: 64,
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Icon(Icons.eco, size: 36, color: Colors.white),
                  ),
                  const SizedBox(height: 20),
                  const Text(
                    'Smart Farming',
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'Farmer Portal · AI Crop Health & Management',
                    style: TextStyle(
                      fontSize: 13,
                      color: AppColors.textMuted,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                  Container(
                    margin: const EdgeInsets.only(top: 14),
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    decoration: BoxDecoration(
                      color: AppColors.primaryLight,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppColors.primaryBorder),
                    ),
                    child: const Row(
                      children: [
                        Icon(Icons.shield_outlined, size: 18, color: AppColors.primary),
                        SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            'Farmer-exclusive client. Experts & Admins must use the web dashboard.',
                            style: TextStyle(
                              fontSize: 11,
                              color: AppColors.primary,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 28),
                  if (_error != null)
                    Container(
                      padding: const EdgeInsets.all(12),
                      margin: const EdgeInsets.only(bottom: 16),
                      decoration: BoxDecoration(
                        color: const Color(0xffffebee),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.red.shade200),
                      ),
                      child: Text(
                        _error!,
                        style: TextStyle(color: Colors.red.shade800, fontSize: 13),
                      ),
                    ),
                  if (_isRegister) ...[
                    TextField(
                      controller: _nameCtrl,
                      decoration: const InputDecoration(
                        labelText: 'Full Name',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.person_outline),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _locationCtrl,
                      decoration: const InputDecoration(
                        labelText: 'Farm Location (e.g. Anand, Gujarat)',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.location_on_outlined),
                      ),
                    ),
                    const SizedBox(height: 16),
                    DropdownButtonFormField<String>(
                      initialValue: _language,
                      decoration: const InputDecoration(
                        labelText: 'Language',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.language),
                      ),
                      items: const [
                        DropdownMenuItem(value: 'English', child: Text('English')),
                        DropdownMenuItem(value: 'Gujarati', child: Text('ગુજરાતી (Gujarati)')),
                        DropdownMenuItem(value: 'Hindi', child: Text('हिन्दी (Hindi)')),
                      ],
                      onChanged: (val) {
                        if (val != null) setState(() => _language = val);
                      },
                    ),
                    const SizedBox(height: 16),
                  ],
                  TextField(
                    controller: _identifierCtrl,
                    decoration: InputDecoration(
                      labelText: _isRegister ? 'Email or Phone' : 'Email, Phone or Username',
                      border: const OutlineInputBorder(),
                      prefixIcon: const Icon(Icons.account_circle_outlined),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _passwordCtrl,
                    obscureText: true,
                    decoration: const InputDecoration(
                      labelText: 'Password',
                      border: OutlineInputBorder(),
                      prefixIcon: Icon(Icons.lock_outline),
                    ),
                  ),
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: _busy ? null : _submit,
                    style: FilledButton.styleFrom(
                      backgroundColor: AppColors.primary,
                      padding: const EdgeInsets.symmetric(vertical: 16),
                    ),
                    child: _busy
                        ? const SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2),
                          )
                        : Text(
                            _isRegister ? 'Register Farmer Account' : 'Sign In as Farmer',
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                  ),
                  const SizedBox(height: 16),
                  TextButton(
                    onPressed: () => setState(() => _isRegister = !_isRegister),
                    child: Text(
                      _isRegister ? 'Already have an account? Sign In' : 'New farmer? Create Account',
                      style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}
