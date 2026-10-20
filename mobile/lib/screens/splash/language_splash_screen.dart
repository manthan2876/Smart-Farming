import 'package:flutter/material.dart';
import '../../providers/locale_provider.dart';
import '../../theme/app_theme.dart';

class LanguageSplashScreen extends StatefulWidget {
  const LanguageSplashScreen({super.key, required this.onLanguageConfirmed});

  final VoidCallback onLanguageConfirmed;

  @override
  State<LanguageSplashScreen> createState() => _LanguageSplashScreenState();
}

class _LanguageSplashScreenState extends State<LanguageSplashScreen> {
  String _selectedLanguage = 'Gujarati';

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        setState(() {
          _selectedLanguage = context.loc.currentLanguage;
        });
      }
    });
  }

  void _chooseLanguage(String lang) {
    setState(() => _selectedLanguage = lang);
    context.loc.setLanguage(lang);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAF7),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 20),
              // App Brand Header
              Center(
                child: Container(
                  width: 72,
                  height: 72,
                  decoration: BoxDecoration(
                    color: AppColors.primary,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withValues(alpha: 0.25),
                        blurRadius: 16,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: const Icon(Icons.eco_rounded, size: 44, color: Colors.white),
                ),
              ),
              const SizedBox(height: 16),
              const Center(
                child: Text(
                  'Smart Farm AI',
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.w800,
                    color: AppColors.textPrimary,
                    letterSpacing: -0.5,
                  ),
                ),
              ),
              const SizedBox(height: 8),
              const Center(
                child: Text(
                  'તમારી ભાષા પસંદ કરો • अपनी भाषा चुनें • Select Language',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 14,
                    color: AppColors.textMuted,
                    fontWeight: FontWeight.w500,
                  ),
                ),
              ),
              const SizedBox(height: 32),

              // Language Cards
              Expanded(
                child: ListView(
                  physics: const BouncingScrollPhysics(),
                  children: [
                    _buildLanguageCard(
                      lang: 'Gujarati',
                      title: 'ગુજરાતી',
                      transliterated: 'Gujarati',
                      subtitle: 'ગુજરાતીમાં પાક રોગ ઓળખ અને ઉપાય',
                      icon: Icons.grass_rounded,
                    ),
                    const SizedBox(height: 14),
                    _buildLanguageCard(
                      lang: 'Hindi',
                      title: 'हिन्दी',
                      transliterated: 'Hindi',
                      subtitle: 'हिन्दी में फसल सुरक्षा और आईसीएआर सलाह',
                      icon: Icons.agriculture_rounded,
                    ),
                    const SizedBox(height: 14),
                    _buildLanguageCard(
                      lang: 'English',
                      title: 'English',
                      transliterated: 'Indian English',
                      subtitle: 'Crop disease diagnosis and expert guidance',
                      icon: Icons.spa_rounded,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),
              // High-Contrast Proceed Button (>= 54 dp touch target)
              SizedBox(
                height: 56,
                child: FilledButton(
                  onPressed: () {
                    context.loc.setLanguage(_selectedLanguage);
                    widget.onLanguageConfirmed();
                  },
                  style: FilledButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(16),
                    ),
                    elevation: 2,
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        _selectedLanguage == 'Gujarati'
                            ? 'આગળ વધો (Continue)'
                            : _selectedLanguage == 'Hindi'
                                ? 'आगे बढ़ें (Continue)'
                                : 'Continue',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(width: 8),
                      const Icon(Icons.arrow_forward_rounded, size: 22, color: Colors.white),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 10),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildLanguageCard({
    required String lang,
    required String title,
    required String transliterated,
    required String subtitle,
    required IconData icon,
  }) {
    final isSelected = _selectedLanguage == lang;

    return InkWell(
      onTap: () => _chooseLanguage(lang),
      borderRadius: BorderRadius.circular(18),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 16),
        decoration: BoxDecoration(
          color: isSelected ? Colors.white : const Color(0xFFF2F5F0),
          borderRadius: BorderRadius.circular(18),
          border: Border.all(
            color: isSelected ? AppColors.primary : Colors.black12,
            width: isSelected ? 2.5 : 1.0,
          ),
          boxShadow: isSelected
              ? [
                  BoxShadow(
                    color: AppColors.primary.withValues(alpha: 0.15),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ]
              : null,
        ),
        child: Row(
          children: [
            Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                color: isSelected ? AppColors.primaryLight : Colors.white,
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(
                icon,
                size: 30,
                color: isSelected ? AppColors.primary : Colors.grey.shade600,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Text(
                        title,
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: isSelected ? AppColors.primary : AppColors.textPrimary,
                        ),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '($transliterated)',
                        style: const TextStyle(
                          fontSize: 13,
                          color: AppColors.textMuted,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: const TextStyle(
                      fontSize: 13,
                      color: AppColors.textMuted,
                      height: 1.25,
                    ),
                  ),
                ],
              ),
            ),
            Container(
              width: 28,
              height: 28,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isSelected ? AppColors.primary : Colors.transparent,
                border: Border.all(
                  color: isSelected ? AppColors.primary : Colors.grey.shade400,
                  width: 2,
                ),
              ),
              child: isSelected
                  ? const Icon(Icons.check, size: 18, color: Colors.white)
                  : null,
            ),
          ],
        ),
      ),
    );
  }
}

