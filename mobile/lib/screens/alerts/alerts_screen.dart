import 'package:flutter/material.dart';
import '../../providers/locale_provider.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class AlertsScreen extends StatelessWidget {
  const AlertsScreen({
    super.key,
    required this.alerts,
    required this.api,
    required this.onRefresh,
  });

  final List<Map<String, dynamic>> alerts;
  final ApiService api;
  final Future<void> Function() onRefresh;

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: onRefresh,
      color: AppColors.primary,
      child: ListView(
        padding: const EdgeInsets.all(22),
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
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
                    const SizedBox(height: 4),
                    Text(context.tr('alertsTitle'), style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w600)),
                  ],
                ),
              ),
              IconButton(onPressed: onRefresh, icon: const Icon(Icons.refresh)),
            ],
          ),
          const SizedBox(height: 20),
          if (alerts.isEmpty)
            Padding(
              padding: const EdgeInsets.all(30),
              child: Center(
                child: Text(context.tr('noAlerts'), textAlign: TextAlign.center, style: const TextStyle(color: AppColors.textMuted)),
              ),
            )
          else
            ...alerts.map(
              (alert) {
                final isRead = alert['is_read'] == true;
                final isExpert = alert['kind']?.toString().toLowerCase().contains('expert') == true ||
                    alert['title']?.toString().toLowerCase().contains('expert') == true;

                return Card(
                  elevation: 0,
                  color: isRead ? AppColors.cardBg : AppColors.primaryLight,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                    side: BorderSide(color: isRead ? AppColors.cardBorder : AppColors.primaryBorder),
                  ),
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ListTile(
                    contentPadding: const EdgeInsets.all(16),
                    leading: CircleAvatar(
                      backgroundColor: isExpert ? AppColors.warningBg : AppColors.primary,
                      child: Icon(
                        isExpert ? Icons.shield : Icons.warning_amber_rounded,
                        color: isExpert ? AppColors.warning : Colors.white,
                      ),
                    ),
                    title: Text(
                      alert['title']?.toString() ?? 'Alert',
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        color: isRead ? Colors.black87 : AppColors.textPrimary,
                      ),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const SizedBox(height: 6),
                        Text(alert['body']?.toString() ?? '', style: const TextStyle(fontSize: 13, height: 1.4)),
                        if (!isRead)
                          TextButton(
                            style: TextButton.styleFrom(padding: EdgeInsets.zero),
                            onPressed: () async {
                              final id = alert['id'];
                              if (id is int) {
                                await api.markAlertRead(id);
                                await onRefresh();
                              }
                            },
                            child: Text('Mark as Read', style: const TextStyle(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.bold)),
                          ),
                      ],
                    ),
                  ),
                );
              },
            ),
        ],
      ),
    );
  }
}
