import 'package:flutter/material.dart';
import '../../providers/locale_provider.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';
import '../scan/result_detail_sheet.dart';

class AlertsScreen extends StatefulWidget {
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
  State<AlertsScreen> createState() => _AlertsScreenState();
}

class _AlertsScreenState extends State<AlertsScreen> {
  String _activeTab = 'all'; // 'all', 'unread', 'weather', 'expert'
  bool _isMarkingAll = false;
  int? _loadingPredictionId;

  Future<void> _handleMarkAllRead() async {
    final unreadIds = widget.alerts
        .where((a) => a['is_read'] != true)
        .map((a) => int.tryParse(a['id']?.toString() ?? ''))
        .whereType<int>()
        .toList();
    if (unreadIds.isEmpty) return;

    setState(() => _isMarkingAll = true);
    try {
      await widget.api.markAllAlertsRead(unreadIds);
      await widget.onRefresh();
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to mark all alerts as read: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isMarkingAll = false);
      }
    }
  }

  Future<void> _handleOpenScan(Map<String, dynamic> alert) async {
    final rawPredId = alert['prediction_id'];
    if (rawPredId == null) return;
    final predId = int.tryParse(rawPredId.toString());
    if (predId == null) return;

    final alertId = int.tryParse(alert['id']?.toString() ?? '');

    // Mark as read if not read yet
    if (alert['is_read'] != true && alertId != null) {
      try {
        await widget.api.markAlertRead(alertId);
        widget.onRefresh();
      } catch (_) {}
    }

    setState(() => _loadingPredictionId = predId);
    try {
      final prediction = await widget.api.getPrediction(predId);
      if (mounted) {
        showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          backgroundColor: Theme.of(context).scaffoldBackgroundColor,
          shape: const RoundedRectangleBorder(
            borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
          ),
          builder: (ctx) => ResultDetailSheet(
            prediction: prediction,
            api: widget.api,
            onFeedbackSubmitted: () {
              widget.onRefresh();
            },
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Could not load diagnosis: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _loadingPredictionId = null);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final unreadCount = widget.alerts.where((a) => a['is_read'] != true).length;

    final filteredAlerts = widget.alerts.where((alert) {
      if (_activeTab == 'unread') {
        return alert['is_read'] != true;
      }
      if (_activeTab == 'weather') {
        final kind = alert['kind']?.toString().toLowerCase() ?? '';
        final title = alert['title']?.toString().toLowerCase() ?? '';
        return kind.contains('weather') ||
            title.contains('weather') ||
            title.contains('मौसम') ||
            title.contains('હવામાન') ||
            title.contains('વરસાદ') ||
            title.contains('ગરમી') ||
            title.contains('જોખમ') ||
            title.contains('जोखिम');
      }
      if (_activeTab == 'expert') {
        final kind = alert['kind']?.toString().toLowerCase() ?? '';
        final title = alert['title']?.toString().toLowerCase() ?? '';
        return kind.contains('expert') ||
            title.contains('expert') ||
            title.contains('विशेषज्ञ') ||
            title.contains('નિષ્ણાત');
      }
      return true;
    }).toList();

    return RefreshIndicator(
      onRefresh: widget.onRefresh,
      color: AppColors.primary,
      child: ListView(
        padding: const EdgeInsets.all(22),
        children: [
          Row(
            crossAxisAlignment: CrossAxisAlignment.start,
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
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            context.tr('alertsTitle'),
                            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        if (unreadCount > 0) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: AppColors.warning,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Text(
                              '$unreadCount',
                              style: const TextStyle(
                                color: Colors.white,
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                        ],
                      ],
                    ),
                  ],
                ),
              ),
              if (unreadCount > 0)
                TextButton.icon(
                  onPressed: _isMarkingAll ? null : _handleMarkAllRead,
                  icon: _isMarkingAll
                      ? const SizedBox(
                          width: 14,
                          height: 14,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.done_all, size: 18),
                  label: Text(
                    context.tr('markAllRead'),
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 16),

          // Horizontal Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildFilterChip('all', '${context.tr('allAlertsTab')} (${widget.alerts.length})'),
                const SizedBox(width: 8),
                _buildFilterChip('unread', '${context.tr('unreadTab')} ($unreadCount)'),
                const SizedBox(width: 8),
                _buildFilterChip('weather', context.tr('weatherTab')),
                const SizedBox(width: 8),
                _buildFilterChip('expert', context.tr('expertTab')),
              ],
            ),
          ),
          const SizedBox(height: 16),

          if (filteredAlerts.isEmpty)
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 48),
              child: Center(
                child: Column(
                  children: [
                    const Icon(Icons.check_circle_outline, size: 48, color: AppColors.primary),
                    const SizedBox(height: 12),
                    Text(
                      context.tr('noAlerts'),
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: AppColors.textMuted),
                    ),
                  ],
                ),
              ),
            )
          else
            ...filteredAlerts.map(
              (alert) {
                final isRead = alert['is_read'] == true;
                final kind = alert['kind']?.toString().toLowerCase() ?? '';
                final title = alert['title']?.toString() ?? '';
                final isExpert = kind.contains('expert') || title.toLowerCase().contains('expert');
                final isWeather = kind.contains('weather') || title.toLowerCase().contains('weather');
                final rawPredId = alert['prediction_id'];
                final hasScan = rawPredId != null;
                final alertId = int.tryParse(alert['id']?.toString() ?? '');
                final createdAt = alert['created_at']?.toString();

                return Card(
                  elevation: 0,
                  color: isRead ? AppColors.cardBg : AppColors.primaryLight,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                    side: BorderSide(
                      color: isRead ? AppColors.cardBorder : AppColors.primaryBorder,
                      width: isRead ? 1 : 1.5,
                    ),
                  ),
                  margin: const EdgeInsets.only(bottom: 12),
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            CircleAvatar(
                              backgroundColor: isExpert
                                  ? AppColors.warningBg
                                  : isWeather
                                      ? Colors.blue.shade50
                                      : AppColors.primaryLight,
                              child: Icon(
                                isExpert
                                    ? Icons.verified_user
                                    : isWeather
                                        ? Icons.cloud_outlined
                                        : Icons.warning_amber_rounded,
                                color: isExpert
                                    ? AppColors.warning
                                    : isWeather
                                        ? Colors.blue.shade700
                                        : AppColors.primary,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Expanded(
                                        child: Text(
                                          context.loc.alertTitle(title),
                                          style: TextStyle(
                                            fontWeight: FontWeight.bold,
                                            fontSize: 15,
                                            color: isRead ? AppColors.textPrimary : Colors.black87,
                                          ),
                                        ),
                                      ),
                                      if (!isRead)
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: AppColors.warning,
                                            borderRadius: BorderRadius.circular(4),
                                          ),
                                          child: const Text(
                                            'NEW',
                                            style: TextStyle(
                                              fontSize: 9,
                                              fontWeight: FontWeight.bold,
                                              color: Colors.white,
                                            ),
                                          ),
                                        ),
                                    ],
                                  ),
                                  if (createdAt != null) ...[
                                    const SizedBox(height: 2),
                                    Text(
                                      createdAt.length >= 10 ? createdAt.substring(0, 10) : createdAt,
                                      style: const TextStyle(fontSize: 11, color: AppColors.textSubtle),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text(
                          alert['body']?.toString() ?? '',
                          style: const TextStyle(fontSize: 13, height: 1.4, color: AppColors.textPrimary),
                        ),
                        const SizedBox(height: 12),
                        Wrap(
                          alignment: WrapAlignment.spaceBetween,
                          crossAxisAlignment: WrapCrossAlignment.center,
                          spacing: 8,
                          runSpacing: 8,
                          children: [
                            if (hasScan)
                              FilledButton.tonalIcon(
                                onPressed: _loadingPredictionId != null
                                    ? null
                                    : () => _handleOpenScan(alert),
                                icon: _loadingPredictionId == int.tryParse(rawPredId.toString())
                                    ? const SizedBox(
                                        width: 14,
                                        height: 14,
                                        child: CircularProgressIndicator(strokeWidth: 2),
                                      )
                                    : const Icon(Icons.arrow_forward, size: 14),
                                label: Text(
                                  context.tr('viewScan'),
                                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                                ),
                              ),
                            if (!isRead && alertId != null)
                              TextButton(
                                onPressed: () async {
                                  try {
                                    await widget.api.markAlertRead(alertId);
                                    await widget.onRefresh();
                                  } catch (_) {}
                                },
                                child: Text(
                                  context.tr('markAsRead'),
                                  style: const TextStyle(
                                    fontSize: 12,
                                    color: AppColors.primary,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ),
                          ],
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

  Widget _buildFilterChip(String tabKey, String label) {
    final isSelected = _activeTab == tabKey;
    return ChoiceChip(
      label: Text(label),
      selected: isSelected,
      selectedColor: AppColors.primary,
      labelStyle: TextStyle(
        fontSize: 12,
        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        color: isSelected ? Colors.white : AppColors.textPrimary,
      ),
      backgroundColor: AppColors.cardBg,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: BorderSide(
          color: isSelected ? AppColors.primary : AppColors.cardBorder,
        ),
      ),
      onSelected: (selected) {
        if (selected) {
          setState(() => _activeTab = tabKey);
        }
      },
    );
  }
}
