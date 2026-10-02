import 'package:flutter/material.dart';
import '../../providers/locale_provider.dart';
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
  bool _busy = false;
  bool _obscurePassword = true;
  String? _error;

  @override
  void dispose() {
    _identifierCtrl.dispose();
    _passwordCtrl.dispose();
    _nameCtrl.dispose();
    _locationCtrl.dispose();
    super.dispose();
  }

  Future<void> _submit(BuildContext context) async {
    setState(() {
      _busy = true;
      _error = null;
    });
    final api = ApiService();
    final lang = context.loc.currentLanguage;
    try {
      if (_isRegister) {
        if (_nameCtrl.text.trim().isEmpty || _passwordCtrl.text.trim().isEmpty) {
          throw Exception(context.tr('emptyCredentialsMsg'));
        }
        final res = await api.register(
          name: _nameCtrl.text.trim(),
          password: _passwordCtrl.text.trim(),
          email: _identifierCtrl.text.contains('@') ? _identifierCtrl.text.trim() : null,
          phone: !_identifierCtrl.text.contains('@') ? _identifierCtrl.text.trim() : null,
          location: _locationCtrl.text.trim(),
          language: lang,
          cropHistory: ['Tomato', 'Cotton'],
        );
        final tokens = res['tokens'] as Map<String, dynamic>;
        final user = res['user'] as Map<String, dynamic>;
        widget.onLoggedIn(tokens['access_token'].toString(), user);
      } else {
        if (_identifierCtrl.text.trim().isEmpty || _passwordCtrl.text.trim().isEmpty) {
          throw Exception(context.tr('emptyCredentialsMsg'));
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

  void _showForgotPasswordSheet(BuildContext context) {
    final emailCtrl = TextEditingController(
      text: _identifierCtrl.text.contains('@') ? _identifierCtrl.text.trim() : '',
    );
    final tokenCtrl = TextEditingController();
    final newPasswordCtrl = TextEditingController();
    final confirmPasswordCtrl = TextEditingController();
    bool isSubmitting = false;
    bool sentEmail = false;
    bool obscureNew = true;
    bool obscureConfirm = true;
    String? recoveryError;
    String? recoverySuccess;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (sheetCtx) => StatefulBuilder(
        builder: (ctx, setSheetState) {

          return Padding(
            padding: EdgeInsets.only(
              left: 24,
              right: 24,
              top: 20,
              bottom: MediaQuery.of(sheetCtx).viewInsets.bottom + 24,
            ),
            child: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Center(
                    child: Container(
                      width: 40,
                      height: 4,
                      decoration: BoxDecoration(
                        color: AppColors.cardBorder,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Row(
                    children: [
                      const Icon(Icons.lock_reset, color: AppColors.primary),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          context.tr('forgotPasswordTitle'),
                          style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  if (recoveryError != null)
                    Container(
                      margin: const EdgeInsets.only(bottom: 14),
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: Colors.red.shade50,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: Colors.red.shade200),
                      ),
                      child: Text(
                        recoveryError!,
                        style: TextStyle(color: Colors.red.shade800, fontSize: 13),
                      ),
                    ),
                  if (recoverySuccess != null)
                    Container(
                      margin: const EdgeInsets.only(bottom: 14),
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.primaryLight,
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppColors.primaryBorder),
                      ),
                      child: Text(
                        recoverySuccess!,
                        style: const TextStyle(color: AppColors.primaryDark, fontSize: 13, fontWeight: FontWeight.w600),
                      ),
                    ),

                  // Step 1: Email for reset token
                  if (!sentEmail) ...[
                    Text(
                      context.tr('enterRegisteredEmail'),
                      style: const TextStyle(fontSize: 13, color: AppColors.textMuted),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: emailCtrl,
                      keyboardType: TextInputType.emailAddress,
                      decoration: const InputDecoration(
                        labelText: 'Email Address',
                        prefixIcon: Icon(Icons.email_outlined),
                        border: OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: isSubmitting
                          ? null
                          : () async {
                              final email = emailCtrl.text.trim();
                              if (email.isEmpty || !email.contains('@')) {
                                setSheetState(() => recoveryError = 'Please enter a valid email address');
                                return;
                              }
                              setSheetState(() {
                                isSubmitting = true;
                                recoveryError = null;
                              });
                              try {
                                final msg = await ApiService().forgotPassword(email);
                                setSheetState(() {
                                  sentEmail = true;
                                  recoverySuccess = msg;
                                  isSubmitting = false;
                                });
                              } catch (e) {
                                setSheetState(() {
                                  recoveryError = e.toString().replaceFirst('Exception: ', '');
                                  isSubmitting = false;
                                });
                              }
                            },
                      style: FilledButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                      ),
                      child: isSubmitting
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                            )
                          : Text(context.tr('sendResetLink')),
                    ),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: () => setSheetState(() => sentEmail = true),
                      child: const Text('Already have a reset token? Enter it here'),
                    ),
                  ] else ...[
                    // Step 2: Reset password using token
                    Text(
                      context.tr('resetPasswordTitle'),
                      style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: tokenCtrl,
                      decoration: InputDecoration(
                        labelText: context.tr('resetToken'),
                        prefixIcon: const Icon(Icons.key_outlined),
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: newPasswordCtrl,
                      obscureText: obscureNew,
                      decoration: InputDecoration(
                        labelText: context.tr('newPassword'),
                        prefixIcon: const Icon(Icons.lock_outline),
                        suffixIcon: IconButton(
                          icon: Icon(obscureNew ? Icons.visibility_off_outlined : Icons.visibility_outlined),
                          onPressed: () => setSheetState(() => obscureNew = !obscureNew),
                        ),
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: confirmPasswordCtrl,
                      obscureText: obscureConfirm,
                      decoration: InputDecoration(
                        labelText: context.tr('confirmPassword'),
                        prefixIcon: const Icon(Icons.check_circle_outline),
                        suffixIcon: IconButton(
                          icon: Icon(obscureConfirm ? Icons.visibility_off_outlined : Icons.visibility_outlined),
                          onPressed: () => setSheetState(() => obscureConfirm = !obscureConfirm),
                        ),
                        border: const OutlineInputBorder(),
                      ),
                    ),
                    const SizedBox(height: 18),
                    FilledButton(
                      onPressed: isSubmitting
                          ? null
                          : () async {
                              final token = tokenCtrl.text.trim();
                              final newP = newPasswordCtrl.text;
                              final confP = confirmPasswordCtrl.text;

                              if (token.isEmpty) {
                                setSheetState(() => recoveryError = 'Please enter the reset token.');
                                return;
                              }
                              if (newP.length < 8) {
                                setSheetState(() => recoveryError = context.tr('passwordTooShort'));
                                return;
                              }
                              if (newP != confP) {
                                setSheetState(() => recoveryError = context.tr('passwordsDoNotMatch'));
                                return;
                              }

                              setSheetState(() {
                                isSubmitting = true;
                                recoveryError = null;
                              });

                                final messenger = ScaffoldMessenger.of(context);
                                final successMsg = context.tr('passwordChangedSuccess');

                                try {
                                  await ApiService().resetPassword(
                                    token: token,
                                    newPassword: newP,
                                  );
                                  if (sheetCtx.mounted) {
                                    Navigator.pop(sheetCtx);
                                  }
                                  if (mounted) {
                                    _passwordCtrl.text = newP;
                                    messenger.showSnackBar(
                                      SnackBar(
                                        backgroundColor: AppColors.primary,
                                        content: Text(successMsg),
                                      ),
                                    );
                                  }
                                } catch (e) {
                                setSheetState(() {
                                  recoveryError = e.toString().replaceFirst('Exception: ', '');
                                  isSubmitting = false;
                                });
                              }
                            },
                      style: FilledButton.styleFrom(
                        backgroundColor: AppColors.primary,
                        padding: const EdgeInsets.symmetric(vertical: 14),
                      ),
                      child: isSubmitting
                          ? const SizedBox(
                              width: 18,
                              height: 18,
                              child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                            )
                          : Text(context.tr('resetPasswordTitle')),
                    ),
                    const SizedBox(height: 8),
                    TextButton(
                      onPressed: () => setSheetState(() => sentEmail = false),
                      child: const Text('Back to request token'),
                    ),
                  ],
                ],
              ),
            ),
          );
        },
      ),
    );
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
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Container(
                        width: 60,
                        height: 60,
                        decoration: BoxDecoration(
                          color: AppColors.primary,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: const Icon(Icons.eco, size: 34, color: Colors.white),
                      ),
                      TextButton.icon(
                        onPressed: () => showLanguageSelectionSheet(context),
                        icon: const Icon(Icons.language, size: 18, color: AppColors.primary),
                        label: Text(
                          context.loc.currentLanguage,
                          style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
                        ),
                        style: TextButton.styleFrom(
                          backgroundColor: AppColors.primaryLight,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  Text(
                    context.tr('appTitle'),
                    style: const TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                      color: AppColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    context.tr('loginSubtitle'),
                    style: const TextStyle(
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
                    child: Row(
                      children: [
                        const Icon(Icons.shield_outlined, size: 18, color: AppColors.primary),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            context.tr('farmersOnlyNotice'),
                            style: const TextStyle(
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
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            _error!,
                            style: TextStyle(color: Colors.red.shade800, fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                  if (_isRegister) ...[
                    TextField(
                      controller: _nameCtrl,
                      decoration: InputDecoration(
                        labelText: context.tr('fullNameLabel'),
                        border: const OutlineInputBorder(),
                        prefixIcon: const Icon(Icons.person_outline),
                      ),
                    ),
                    const SizedBox(height: 16),
                    TextField(
                      controller: _locationCtrl,
                      decoration: InputDecoration(
                        labelText: context.tr('farmLocationLabel'),
                        border: const OutlineInputBorder(),
                        prefixIcon: const Icon(Icons.location_on_outlined),
                      ),
                    ),
                    const SizedBox(height: 16),
                  ],
                  TextField(
                    controller: _identifierCtrl,
                    decoration: InputDecoration(
                      labelText: context.tr('identifierHint'),
                      border: const OutlineInputBorder(),
                      prefixIcon: const Icon(Icons.account_circle_outlined),
                    ),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _passwordCtrl,
                    obscureText: _obscurePassword,
                    decoration: InputDecoration(
                      labelText: context.tr('passwordHint'),
                      border: const OutlineInputBorder(),
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(_obscurePassword ? Icons.visibility_off_outlined : Icons.visibility_outlined),
                        onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                      ),
                    ),
                  ),
                  if (!_isRegister) ...[
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: () => _showForgotPasswordSheet(context),
                        style: TextButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
                        ),
                        child: Text(
                          context.tr('forgotPasswordBtn'),
                          style: const TextStyle(
                            fontSize: 13,
                            color: AppColors.primary,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),
                    ),
                  ] else
                    const SizedBox(height: 16),
                  const SizedBox(height: 8),
                  FilledButton(
                    onPressed: _busy ? null : () => _submit(context),
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
                            _isRegister ? context.tr('registerBtn') : context.tr('signInBtn'),
                            style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                          ),
                  ),
                  const SizedBox(height: 16),
                  TextButton(
                    onPressed: () => setState(() {
                      _isRegister = !_isRegister;
                      _error = null;
                    }),
                    child: Text(
                      _isRegister
                          ? context.tr('alreadyHaveAccount')
                          : context.tr('dontHaveAccount'),
                      style: const TextStyle(color: AppColors.primary),
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
