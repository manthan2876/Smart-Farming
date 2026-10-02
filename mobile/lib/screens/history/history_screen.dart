import 'package:flutter/material.dart';
import '../../models/prediction.dart';
import '../../providers/locale_provider.dart';
import '../../theme/app_theme.dart';
import '../../utils/app_logger.dart';

class HistoryScreen extends StatefulWidget {
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
  State<HistoryScreen> createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  final TextEditingController _searchCtrl = TextEditingController();
  String _searchQuery = '';
  String _selectedCrop = 'All';

  @override
  void dispose() {
    _searchCtrl.dispose();
    super.dispose();
  }

  Widget _buildSeverityBadge(BuildContext context, int severityPercent, String? bucket) {
    Color bg;
    Color fg;
    String label = bucket != null
        ? context.loc.severity(bucket)
        : context.loc.severityPercent(severityPercent);

    if (severityPercent > 55 || bucket?.toLowerCase() == 'severe' || bucket?.toLowerCase() == 'critical') {
      bg = const Color(0xffffebee);
      fg = const Color(0xffc62828);
    } else if (severityPercent >= 25 || bucket?.toLowerCase() == 'moderate') {
      bg = const Color(0xfffff8e1);
      fg = const Color(0xffe65100);
    } else {
      bg = const Color(0xffe8f5e9);
      fg = const Color(0xff2e7d32);
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        '$severityPercent% $label',
        style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: fg),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    AppLogger.info('HistoryScreen', 'Rendering scan history list with ${widget.history.length} past scans.');

    // Extract unique crops
    final cropSet = <String>{};
    for (final item in widget.history) {
      if (item.crop.isNotEmpty && item.crop != 'Unknown crop') {
        cropSet.add(item.crop);
      }
    }
    final cropList = ['All', ...cropSet];

    // Filter by crop and search query
    final filtered = widget.history.where((item) {
      final matchesCrop = _selectedCrop == 'All' || item.crop.toLowerCase() == _selectedCrop.toLowerCase();
      final query = _searchQuery.trim().toLowerCase();
      if (query.isEmpty) return matchesCrop;

      final matchesQuery = item.crop.toLowerCase().contains(query) ||
          item.disease.toLowerCase().contains(query) ||
          context.loc.crop(item.crop).toLowerCase().contains(query) ||
          context.loc.disease(item.disease).toLowerCase().contains(query);

      return matchesCrop && matchesQuery;
    }).toList();

    final content = ListView(
      padding: const EdgeInsets.all(20),
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
        const SizedBox(height: 6),
        Text(
          context.tr('scanHistoryTitle'),
          style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 16),

        // Search Bar
        TextField(
          controller: _searchCtrl,
          onChanged: (val) => setState(() => _searchQuery = val),
          decoration: InputDecoration(
            hintText: context.tr('searchScans'),
            prefixIcon: const Icon(Icons.search, size: 20, color: AppColors.textMuted),
            suffixIcon: _searchQuery.isNotEmpty
                ? IconButton(
                    icon: const Icon(Icons.clear, size: 18),
                    onPressed: () {
                      _searchCtrl.clear();
                      setState(() => _searchQuery = '');
                    },
                  )
                : null,
            filled: true,
            fillColor: AppColors.cardBg,
            contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: AppColors.cardBorder),
            ),
            enabledBorder: OutlineInputBorder(
              borderRadius: BorderRadius.circular(12),
              borderSide: const BorderSide(color: AppColors.cardBorder),
            ),
          ),
        ),
        const SizedBox(height: 12),

        // Crop Filter Chips
        if (cropList.length > 1) ...[
          SizedBox(
            height: 38,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: cropList.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (_, index) {
                final crop = cropList[index];
                final isSelected = _selectedCrop.toLowerCase() == crop.toLowerCase();
                final label = crop == 'All' ? context.tr('allCrops') : context.loc.crop(crop);

                return ChoiceChip(
                  label: Text(label),
                  selected: isSelected,
                  onSelected: (_) => setState(() => _selectedCrop = crop),
                  selectedColor: AppColors.primary,
                  backgroundColor: AppColors.cardBg,
                  labelStyle: TextStyle(
                    fontSize: 12,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    color: isSelected ? Colors.white : AppColors.textPrimary,
                  ),
                  side: BorderSide(
                    color: isSelected ? AppColors.primary : AppColors.cardBorder,
                  ),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18)),
                  showCheckmark: false,
                );
              },
            ),
          ),
          const SizedBox(height: 16),
        ],

        // Active count
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              '${filtered.length} ${filtered.length == 1 ? "record" : "records"}',
              style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppColors.textMuted),
            ),
            if (_searchQuery.isNotEmpty || _selectedCrop != 'All')
              GestureDetector(
                onTap: () {
                  _searchCtrl.clear();
                  setState(() {
                    _searchQuery = '';
                    _selectedCrop = 'All';
                  });
                },
                child: const Text('Reset filters', style: TextStyle(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.bold)),
              ),
          ],
        ),
        const SizedBox(height: 12),

        // Empty state vs items list
        if (widget.history.isEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 40),
            child: Center(
              child: Column(
                children: [
                  const Icon(Icons.history, size: 48, color: AppColors.textSubtle),
                  const SizedBox(height: 12),
                  Text(
                    context.tr('emptyHistory'),
                    style: const TextStyle(color: AppColors.textMuted),
                  ),
                ],
              ),
            ),
          )
        else if (filtered.isEmpty)
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 40),
            child: Center(
              child: Column(
                children: [
                  const Icon(Icons.search_off, size: 42, color: AppColors.textSubtle),
                  const SizedBox(height: 10),
                  Text(
                    'No scans match "$_searchQuery"',
                    style: const TextStyle(color: AppColors.textMuted, fontSize: 13),
                  ),
                ],
              ),
            ),
          )
        else
          ...filtered.map(
            (item) {
              final rawDate = item.createdAt;
              final dateStr = rawDate != null && rawDate.contains('T')
                  ? rawDate.split('T').first
                  : (rawDate ?? 'Recent');

              return Card(
                elevation: 0,
                color: AppColors.cardBg,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                  side: const BorderSide(color: AppColors.cardBorder),
                ),
                margin: const EdgeInsets.only(bottom: 12),
                child: ListTile(
                  onTap: () {
                    AppLogger.info('HistoryScreen', 'Tapped scan item #${item.id}: ${item.crop} - ${item.disease}');
                    widget.onSelectPrediction(item);
                  },
                  contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                  leading: const CircleAvatar(
                    backgroundColor: AppColors.primaryLight,
                    child: Icon(Icons.eco_outlined, color: AppColors.primary),
                  ),
                  title: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Expanded(
                        child: Text(
                          context.loc.disease(item.disease),
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      Text(
                        '${(item.confidence * 100).round()}%',
                        style: const TextStyle(
                          color: AppColors.primary,
                          fontWeight: FontWeight.bold,
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                  subtitle: Padding(
                    padding: const EdgeInsets.only(top: 6),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Expanded(
                          child: Text(
                            '${context.loc.crop(item.crop)} · $dateStr',
                            style: const TextStyle(fontSize: 12, color: AppColors.textMuted),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                        _buildSeverityBadge(context, item.severity, item.severityBucket),
                      ],
                    ),
                  ),
                  trailing: const Icon(Icons.chevron_right, size: 18, color: Colors.grey),
                ),
              );
            },
          ),
      ],
    );

    if (widget.onRefresh != null) {
      return RefreshIndicator(
        onRefresh: widget.onRefresh!,
        color: AppColors.primary,
        child: content,
      );
    }
    return content;
  }
}
