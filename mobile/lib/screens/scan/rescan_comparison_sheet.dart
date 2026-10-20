import 'package:flutter/material.dart';
import '../../models/prediction.dart';
import '../../providers/locale_provider.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class RescanComparisonSheet extends StatelessWidget {
  const RescanComparisonSheet({
    super.key,
    required this.initialPrediction,
    required this.rescanPrediction,
    required this.api,
    this.onRequestExpert,
  });

  final Prediction initialPrediction;
  final Prediction rescanPrediction;
  final ApiService api;
  final VoidCallback? onRequestExpert;

  @override
  Widget build(BuildContext context) {
    final initSev = initialPrediction.severity;
    final newSev = rescanPrediction.severity;
    final delta = newSev - initSev;
    final isImproving = delta < 0;

    final initialImgUrl = initialPrediction.rawUrl != null
        ? api.getAssetUrl(initialPrediction.rawUrl)
        : (initialPrediction.imagePath != null ? api.getAssetUrl(initialPrediction.imagePath) : null);
    final rescanImgUrl = rescanPrediction.rawUrl != null
        ? api.getAssetUrl(rescanPrediction.rawUrl)
        : (rescanPrediction.imagePath != null ? api.getAssetUrl(rescanPrediction.imagePath) : null);

    return DraggableScrollableSheet(
      initialChildSize: 0.85,
      minChildSize: 0.5,
      maxChildSize: 0.95,
      expand: false,
      builder: (ctx, scrollController) => ListView(
        controller: scrollController,
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
        children: [
          // Drag handle
          Center(
            child: Container(
              width: 44,
              height: 5,
              decoration: BoxDecoration(
                color: Colors.grey.shade300,
                borderRadius: BorderRadius.circular(10),
              ),
            ),
          ),
          const SizedBox(height: 16),

          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                context.tr('rescanCompareTitle'),
                style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
              ),
              IconButton(
                onPressed: () => Navigator.pop(ctx),
                icon: const Icon(Icons.close),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Recovery Outcome Banner
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isImproving ? const Color(0xffecfdf5) : const Color(0xfffef2f2),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: isImproving ? const Color(0xff10b981) : const Color(0xffef4444),
                width: 1.5,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  isImproving ? Icons.trending_down : Icons.trending_up,
                  color: isImproving ? const Color(0xff047857) : const Color(0xffb91c1c),
                  size: 28,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isImproving ? context.tr('recoveryProgress') : context.tr('conditionWorsened'),
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: isImproving ? const Color(0xff065f46) : const Color(0xff991b1b),
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Lesion surface area changed from $initSev% to $newSev% (${delta > 0 ? "+$delta" : "$delta"}%)',
                        style: TextStyle(
                          fontSize: 12,
                          color: isImproving ? const Color(0xff047857) : const Color(0xffb91c1c),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Side-by-Side Images
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      context.tr('previousScan'),
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppColors.textMuted),
                    ),
                    const SizedBox(height: 6),
                    Container(
                      height: 140,
                      decoration: BoxDecoration(
                        color: Colors.black12,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AppColors.cardBorder),
                      ),
                      clipBehavior: Clip.antiAlias,
                      child: initialImgUrl != null
                          ? Image.network(
                              initialImgUrl,
                              fit: BoxFit.cover,
                              errorBuilder: (_, __, ___) => const Center(
                                child: Icon(Icons.broken_image, color: Colors.grey),
                              ),
                            )
                          : const Center(child: Icon(Icons.image, color: Colors.grey)),
                    ),
                    const SizedBox(height: 6),
                    Center(
                      child: Text(
                        'Severity: $initSev%',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(width: 14),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      context.tr('currentScan'),
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppColors.primary),
                    ),
                    const SizedBox(height: 6),
                    Container(
                      height: 140,
                      decoration: BoxDecoration(
                        color: Colors.black12,
                        borderRadius: BorderRadius.circular(14),
                        border: Border.all(color: AppColors.primary, width: 2),
                      ),
                      clipBehavior: Clip.antiAlias,
                      child: rescanImgUrl != null
                          ? Image.network(
                              rescanImgUrl,
                              fit: BoxFit.cover,
                              errorBuilder: (_, __, ___) => const Center(
                                child: Icon(Icons.broken_image, color: Colors.grey),
                              ),
                            )
                          : const Center(child: Icon(Icons.image, color: Colors.grey)),
                    ),
                    const SizedBox(height: 6),
                    Center(
                      child: Text(
                        'Severity: $newSev%',
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppColors.primary),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Diagnostic Summary
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xfff4f1e8),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '${context.loc.crop(rescanPrediction.crop)}: ${context.loc.disease(rescanPrediction.disease)}',
                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                ),
                const SizedBox(height: 8),
                if (rescanPrediction.treatment != null && rescanPrediction.treatment!.isNotEmpty) ...[
                  Text(
                    rescanPrediction.localizedTreatment(context.loc.languageCode) ?? rescanPrediction.treatment!,
                    style: const TextStyle(fontSize: 13, color: Color(0xff5d513f), height: 1.4),
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 16),

          // Statutory Disclaimer
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xfffff7ed),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xfffed7aa)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.shield_outlined, color: Color(0xffc2410c), size: 18),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    context.tr('statutoryDisclaimer'),
                    style: const TextStyle(fontSize: 11, color: Color(0xff9a3412), height: 1.35),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Escalation Action
          if (onRequestExpert != null) ...[
            FilledButton.icon(
              onPressed: () {
                Navigator.pop(ctx);
                onRequestExpert!();
              },
              icon: const Icon(Icons.support_agent),
              label: const Text('Consult Agronomist on this Follow-up'),
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.primary,
                padding: const EdgeInsets.symmetric(vertical: 14),
              ),
            ),
          ],
        ],
      ),
    );
  }
}

