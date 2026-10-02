import 'package:flutter/material.dart';
import '../../providers/locale_provider.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({
    super.key,
    required this.userProfile,
    required this.farm,
    required this.api,
    required this.onLogout,
    this.onProfileUpdated,
  });

  final Map<String, dynamic> userProfile;
  final Map<String, dynamic>? farm;
  final ApiService api;
  final VoidCallback onLogout;
  final VoidCallback? onProfileUpdated;

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  // Password form controllers
  final _oldPasswordCtrl = TextEditingController();
  final _newPasswordCtrl = TextEditingController();
  final _confirmPasswordCtrl = TextEditingController();
  bool _obscureOld = true;
  bool _obscureNew = true;
  bool _obscureConfirm = true;
  bool _isChangingPassword = false;
  String? _pwdError;

  // Supported crops
  List<String>? _supportedCrops;
  bool _isLoadingCrops = false;

  @override
  void initState() {
    super.initState();
    _loadCrops();
  }

  @override
  void dispose() {
    _oldPasswordCtrl.dispose();
    _newPasswordCtrl.dispose();
    _confirmPasswordCtrl.dispose();
    super.dispose();
  }

  Future<void> _loadCrops() async {
    setState(() => _isLoadingCrops = true);
    try {
      final crops = await widget.api.getSupportedCrops();
      if (mounted) setState(() => _supportedCrops = crops);
    } catch (_) {
      // Fallback default crops
      if (mounted) {
        setState(() => _supportedCrops = [
              'Tomato',
              'Cotton',
              'Potato',
              'Corn',
              'Wheat',
              'Rice',
              'Apple',
              'Grape',
              'Bell Pepper',
            ]);
      }
    } finally {
      if (mounted) setState(() => _isLoadingCrops = false);
    }
  }

  void _showChangePasswordDialog() {
    _oldPasswordCtrl.clear();
    _newPasswordCtrl.clear();
    _confirmPasswordCtrl.clear();
    setState(() => _pwdError = null);

    showDialog(
      context: context,
      builder: (dialogCtx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
          title: Row(
            children: [
              const Icon(Icons.lock_reset, color: AppColors.primary),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  context.tr('changePassword'),
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (_pwdError != null)
                  Container(
                    margin: const EdgeInsets.only(bottom: 12),
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: Colors.red.shade200),
                    ),
                    child: Text(
                      _pwdError!,
                      style: TextStyle(color: Colors.red.shade800, fontSize: 12),
                    ),
                  ),
                TextField(
                  controller: _oldPasswordCtrl,
                  obscureText: _obscureOld,
                  decoration: InputDecoration(
                    labelText: context.tr('oldPassword'),
                    prefixIcon: const Icon(Icons.lock_outline),
                    suffixIcon: IconButton(
                      icon: Icon(_obscureOld ? Icons.visibility_off : Icons.visibility),
                      onPressed: () => setDialogState(() => _obscureOld = !_obscureOld),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _newPasswordCtrl,
                  obscureText: _obscureNew,
                  decoration: InputDecoration(
                    labelText: context.tr('newPassword'),
                    prefixIcon: const Icon(Icons.vpn_key_outlined),
                    suffixIcon: IconButton(
                      icon: Icon(_obscureNew ? Icons.visibility_off : Icons.visibility),
                      onPressed: () => setDialogState(() => _obscureNew = !_obscureNew),
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: _confirmPasswordCtrl,
                  obscureText: _obscureConfirm,
                  decoration: InputDecoration(
                    labelText: context.tr('confirmPassword'),
                    prefixIcon: const Icon(Icons.check_circle_outline),
                    suffixIcon: IconButton(
                      icon: Icon(_obscureConfirm ? Icons.visibility_off : Icons.visibility),
                      onPressed: () => setDialogState(() => _obscureConfirm = !_obscureConfirm),
                    ),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogCtx),
              child: Text(context.tr('cancel')),
            ),
            FilledButton(
              onPressed: _isChangingPassword
                  ? null
                  : () async {
                      final oldP = _oldPasswordCtrl.text;
                      final newP = _newPasswordCtrl.text;
                      final confP = _confirmPasswordCtrl.text;

                      if (newP.length < 8) {
                        setDialogState(() => _pwdError = context.tr('passwordTooShort'));
                        return;
                      }
                      if (newP != confP) {
                        setDialogState(() => _pwdError = context.tr('passwordsDoNotMatch'));
                        return;
                      }

                      setDialogState(() {
                        _isChangingPassword = true;
                        _pwdError = null;
                      });

                      try {
                        await widget.api.changePassword(
                          oldPassword: oldP,
                          newPassword: newP,
                        );
                        if (dialogCtx.mounted) {
                          Navigator.pop(dialogCtx);
                        }
                        if (mounted) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              backgroundColor: AppColors.primary,
                              content: Text(context.tr('passwordChangedSuccess')),
                            ),
                          );
                        }
                      } catch (e) {
                        setDialogState(() {
                          _pwdError = e.toString().replaceFirst('Exception: ', '');
                        });
                      } finally {
                        setDialogState(() => _isChangingPassword = false);
                      }
                    },
              child: _isChangingPassword
                  ? const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : Text(context.tr('save')),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final name = widget.userProfile['name']?.toString() ?? 'Farmer';
    final emailOrPhone = widget.userProfile['email']?.toString() ??
        widget.userProfile['phone']?.toString() ??
        '';
    final farmName = widget.farm?['name']?.toString() ??
        widget.userProfile['farm_name']?.toString() ??
        'My Family Farm';
    final location = widget.farm?['location']?.toString() ??
        widget.userProfile['location']?.toString() ??
        'Anand, Gujarat';

    final localeProvider = LocaleScope.of(context);
    final currentLang = localeProvider.currentLanguage;
    final currentUnit = localeProvider.currentUnit;

    return Scaffold(
      appBar: AppBar(
        title: Text(context.tr('settingsTitle')),
        backgroundColor: AppColors.cardBg,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          // Farmer Profile Card
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  radius: 30,
                  backgroundColor: AppColors.primaryLight,
                  child: Text(
                    name.isNotEmpty ? name[0].toUpperCase() : 'F',
                    style: const TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.bold,
                      color: AppColors.primary,
                    ),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Expanded(
                            child: Text(
                              name,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: AppColors.textPrimary,
                              ),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: AppColors.primaryLight,
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              context.tr('farmerBadge'),
                              style: const TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: AppColors.primary,
                              ),
                            ),
                          ),
                        ],
                      ),
                      if (emailOrPhone.isNotEmpty) ...[
                        const SizedBox(height: 3),
                        Text(
                          emailOrPhone,
                          style: const TextStyle(fontSize: 13, color: AppColors.textMuted),
                        ),
                      ],
                      const SizedBox(height: 4),
                      Row(
                        children: [
                          const Icon(Icons.place_outlined, size: 14, color: AppColors.textSubtle),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              '$farmName · $location',
                              style: const TextStyle(fontSize: 12, color: AppColors.textSubtle),
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),
          _buildSectionHeader(Icons.language, context.tr('selectLanguage')),
          const SizedBox(height: 10),

          // Language Selection Card
          Container(
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: Column(
              children: [
                _buildLanguageTile('English', 'English', currentLang, (val) {
                  localeProvider.setLanguage(val);
                }),
                const Divider(height: 1, color: AppColors.cardBorder),
                _buildLanguageTile('हिन्दी (Hindi)', 'Hindi', currentLang, (val) {
                  localeProvider.setLanguage(val);
                }),
                const Divider(height: 1, color: AppColors.cardBorder),
                _buildLanguageTile('ગુજરાતી (Gujarati)', 'Gujarati', currentLang, (val) {
                  localeProvider.setLanguage(val);
                }),
              ],
            ),
          ),

          const SizedBox(height: 24),
          _buildSectionHeader(Icons.straighten, context.tr('unitPreference')),
          const SizedBox(height: 10),

          // Unit Preferences Card
          Container(
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: Column(
              children: [
                ListTile(
                  title: Text(
                    context.tr('metric'),
                    style: TextStyle(
                      fontWeight: currentUnit == 'Metric' ? FontWeight.bold : FontWeight.w600,
                      fontSize: 14,
                      color: currentUnit == 'Metric' ? AppColors.primary : AppColors.textPrimary,
                    ),
                  ),
                  subtitle: const Text('Celsius, km/h, Hectares', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                  trailing: currentUnit == 'Metric'
                      ? const Icon(Icons.check_circle, color: AppColors.primary)
                      : const Icon(Icons.radio_button_unchecked, color: AppColors.cardBorder),
                  onTap: () => localeProvider.setUnit('Metric'),
                ),
                const Divider(height: 1, color: AppColors.cardBorder),
                ListTile(
                  title: Text(
                    context.tr('imperial'),
                    style: TextStyle(
                      fontWeight: currentUnit == 'Imperial' ? FontWeight.bold : FontWeight.w600,
                      fontSize: 14,
                      color: currentUnit == 'Imperial' ? AppColors.primary : AppColors.textPrimary,
                    ),
                  ),
                  subtitle: const Text('Fahrenheit, mph, Acres', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                  trailing: currentUnit == 'Imperial'
                      ? const Icon(Icons.check_circle, color: AppColors.primary)
                      : const Icon(Icons.radio_button_unchecked, color: AppColors.cardBorder),
                  onTap: () => localeProvider.setUnit('Imperial'),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),
          _buildSectionHeader(Icons.security, context.tr('changePassword')),
          const SizedBox(height: 10),

          // Security / Password Tile
          Container(
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: ListTile(
              leading: const CircleAvatar(
                backgroundColor: AppColors.primaryLight,
                child: Icon(Icons.key, color: AppColors.primary, size: 20),
              ),
              title: Text(
                context.tr('changePassword'),
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
              subtitle: const Text('Update your farmer account password', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
              trailing: const Icon(Icons.chevron_right),
              onTap: _showChangePasswordDialog,
            ),
          ),

          const SizedBox(height: 24),
          _buildSectionHeader(Icons.eco_outlined, context.tr('supportedCropsTitle')),
          const SizedBox(height: 10),

          // Supported Crops Directory Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: _isLoadingCrops
                ? const Center(
                    child: Padding(
                      padding: EdgeInsets.all(12),
                      child: CircularProgressIndicator(strokeWidth: 2),
                    ),
                  )
                : (_supportedCrops == null || _supportedCrops!.isEmpty)
                    ? const Text('No crop models found', style: TextStyle(color: AppColors.textMuted))
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            context.tr('activeModelPipelines'),
                            style: const TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                              letterSpacing: 1.2,
                              color: AppColors.textSubtle,
                            ),
                          ),
                          const SizedBox(height: 10),
                          Wrap(
                            spacing: 8,
                            runSpacing: 8,
                            children: _supportedCrops!.map((c) {
                              final localizedName = context.loc.crop(c);
                              return Container(
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                decoration: BoxDecoration(
                                  color: AppColors.primaryLight,
                                  borderRadius: BorderRadius.circular(8),
                                  border: Border.all(color: AppColors.primaryBorder),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    const Icon(Icons.check_circle, size: 14, color: AppColors.primary),
                                    const SizedBox(width: 6),
                                    Text(
                                      localizedName,
                                      style: const TextStyle(
                                        fontSize: 12,
                                        fontWeight: FontWeight.bold,
                                        color: AppColors.primaryDark,
                                      ),
                                    ),
                                  ],
                                ),
                              );
                            }).toList(),
                          ),
                        ],
                      ),
          ),

          const SizedBox(height: 32),

          // Sign Out Button
          OutlinedButton.icon(
            onPressed: widget.onLogout,
            style: OutlinedButton.styleFrom(
              foregroundColor: Colors.red.shade700,
              side: BorderSide(color: Colors.red.shade300),
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            icon: const Icon(Icons.logout),
            label: Text(
              context.tr('signOut'),
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(IconData icon, String title) {
    return Row(
      children: [
        Icon(icon, size: 18, color: AppColors.primary),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            title,
            style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }

  Widget _buildLanguageTile(
    String displayLabel,
    String value,
    String selectedValue,
    ValueChanged<String> onChanged,
  ) {
    final isSelected = selectedValue == value;
    return ListTile(
      title: Text(
        displayLabel,
        style: TextStyle(
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
          color: isSelected ? AppColors.primary : AppColors.textPrimary,
        ),
      ),
      trailing: isSelected
          ? const Icon(Icons.check_circle, color: AppColors.primary)
          : null,
      onTap: () => onChanged(value),
    );
  }
}
