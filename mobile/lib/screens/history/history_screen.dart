import 'package:flutter/material.dart';
import '../../models/prediction.dart';
import '../../providers/locale_provider.dart';
import '../../theme/app_theme.dart';

class HistoryScreen extends StatelessWidget {
  const HistoryScreen({
    super.key,
    required this.history,
    required this.onSelectPrediction,
    this.onRefresh,
  });

  final List<Prediction> history;
  final ValueChanged<Prediction> onSelectPrediction;
  final Future<void> Function()? onRefresh;

  @override
  Widget build(BuildContext context) {
    final listWidget = ListView(
      padding: const EdgeInsets.all(22),
      children: [
        Text(
          context.tr('appTitle').toUpperCase(),
          style: const TextStyle(
            letterSpacing: 2,
            color: AppColors.textSubtle,
            fontSize: 10,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 8),
        Text(
          context.tr('scanHistoryTitle'),
          style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 22),
        if (history.isEmpty)
          Padding(
            padding: const EdgeInsets.all(30),
            child: Center(
              child: Text(
                context.tr('emptyHistory'),
                style: const TextStyle(color: AppColors.textMuted),
              ),
            ),
          )
        else
          ...history.map(
            (item) => Card(
              elevation: 0,
              color: AppColors.cardBg,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(14),
                side: const BorderSide(color: AppColors.cardBorder),
              ),
              margin: const EdgeInsets.only(bottom: 12),
              child: ListTile(
                onTap: () => onSelectPrediction(item),
                contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
                leading: const CircleAvatar(
                  backgroundColor: AppColors.primaryLight,
                  child: Icon(Icons.eco_outlined, color: AppColors.primary),
                ),
                title: Text(
                  context.loc.disease(item.disease),
                  style: const TextStyle(fontWeight: FontWeight.w600),
                ),
                subtitle: Text(
                  '${context.loc.crop(item.crop)}  ·  ${item.severity}% ${context.tr('severity')}',
                ),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(
                      '${(item.confidence * 100).round()}%',
                      style: const TextStyle(
                        color: AppColors.primary,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(width: 8),
                    const Icon(Icons.chevron_right, size: 18, color: Colors.grey),
                  ],
                ),
              ),
            ),
          ),
      ],
    );

    if (onRefresh != null) {
      return RefreshIndicator(
        onRefresh: onRefresh!,
        color: AppColors.primary,
        child: listWidget,
      );
    }
    return listWidget;
  }
}
