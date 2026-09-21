import 'package:flutter/material.dart';
import '../../providers/locale_provider.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class FarmScreen extends StatefulWidget {
  const FarmScreen({
    super.key,
    required this.farm,
    required this.userProfile,
    required this.api,
    required this.onFarmUpdated,
  });

  final Map<String, dynamic>? farm;
  final Map<String, dynamic> userProfile;
  final ApiService api;
  final Future<void> Function() onFarmUpdated;

  @override
  State<FarmScreen> createState() => _FarmScreenState();
}

class _FarmScreenState extends State<FarmScreen> {
  void _showAddPlotDialog() {
    final nameCtrl = TextEditingController();
    final cropCtrl = TextEditingController(text: 'Tomato');
    final areaCtrl = TextEditingController(text: '1.5');
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(context.tr('addPlotTitle')),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(controller: nameCtrl, decoration: InputDecoration(labelText: context.tr('plotNameLabel'))),
            TextField(controller: cropCtrl, decoration: InputDecoration(labelText: context.tr('primaryCropLabel'))),
            TextField(controller: areaCtrl, keyboardType: TextInputType.number, decoration: InputDecoration(labelText: context.tr('areaAcresLabel'))),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text(context.tr('cancel'))),
          FilledButton(
            onPressed: () async {
              if (nameCtrl.text.trim().isEmpty) return;
              Navigator.pop(ctx);
              try {
                await widget.api.createPlot(
                  name: nameCtrl.text.trim(),
                  crop: cropCtrl.text.trim(),
                  areaAcres: double.tryParse(areaCtrl.text.trim()) ?? 1.0,
                );
                await widget.onFarmUpdated();
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('${context.tr('failedCreatePlot')}: $e')),
                  );
                }
              }
            },
            child: Text(context.tr('save')),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final plots = (widget.farm?['plots'] as List?) ?? [];
    final name = widget.farm?['name']?.toString() ?? widget.userProfile['farm_name']?.toString() ?? 'My Family Farm';
    final location = widget.farm?['location']?.toString() ?? widget.userProfile['location']?.toString() ?? 'Anand, Gujarat';
    final area = widget.farm?['area_acres'] != null ? '${widget.farm!['area_acres']} ${context.tr('acres')}' : '5.0 ${context.tr('acres')}';

    return RefreshIndicator(
      onRefresh: widget.onFarmUpdated,
      color: AppColors.primary,
      child: ListView(
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
          Text(name, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w600)),
          Text('$location · $area', style: const TextStyle(color: AppColors.textMuted)),
          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  '${context.tr('plotsTitle')} (${plots.length})',
                  style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              TextButton.icon(
                onPressed: _showAddPlotDialog,
                icon: const Icon(Icons.add, size: 16),
                label: Text(context.tr('addPlotBtn')),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (plots.isEmpty)
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.cardBg,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Center(
                child: Text(context.tr('noPlotsFound'), style: const TextStyle(color: AppColors.textMuted)),
              ),
            )
          else
            ...plots.map(
              (p) => Card(
                elevation: 0,
                color: AppColors.cardBg,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                  side: const BorderSide(color: AppColors.cardBorder),
                ),
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  leading: const CircleAvatar(
                    backgroundColor: AppColors.primaryLight,
                    child: Icon(Icons.grass, color: AppColors.primary),
                  ),
                  title: Text(p['name']?.toString() ?? 'Plot', style: const TextStyle(fontWeight: FontWeight.bold)),
                  subtitle: Text('${context.loc.crop(p['crop']?.toString())} · ${p['area_acres'] ?? 1.0} ${context.tr('acres')}'),
                  trailing: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.primaryLight,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      context.tr('activeStatus'),
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.primary),
                    ),
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }
}
