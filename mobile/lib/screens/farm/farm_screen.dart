import 'package:flutter/material.dart';
import '../../providers/locale_provider.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';
import '../../utils/geo_math.dart';
import '../map/field_boundary_screen.dart';
import 'widgets/farm_satellite_card.dart';

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
  bool _isSavingFarm = false;
  bool _isDeletingPlot = false;

  Future<void> _openFarmBoundaryDrawer() async {
    final rawBoundary = widget.farm?['boundary'] as Map<String, dynamic>?;
    final farmPts = GeoMath.geoJsonToLatLngList(rawBoundary);
    final currentFarm = widget.farm ?? {};

    final result = await Navigator.push<BoundaryResult>(
      context,
      MaterialPageRoute(
        builder: (_) => FieldBoundaryScreen(
          type: BoundaryType.farm,
          initialPoints: farmPts,
          centerLat: (currentFarm['latitude'] as num?)?.toDouble(),
          centerLon: (currentFarm['longitude'] as num?)?.toDouble(),
        ),
      ),
    );

    if (result != null) {
      final name = currentFarm['name']?.toString() ?? widget.userProfile['farm_name']?.toString() ?? 'My Family Farm';
      final loc = currentFarm['location']?.toString() ?? widget.userProfile['location']?.toString() ?? 'Anand, Gujarat';
      final currentArea = (currentFarm['area_acres'] as num?)?.toDouble() ?? 5.0;
      final area = result.acres > 0 ? result.acres : currentArea;
      final lat = result.points.isNotEmpty ? result.points.first.latitude : (currentFarm['latitude'] as num?)?.toDouble();
      final lon = result.points.isNotEmpty ? result.points.first.longitude : (currentFarm['longitude'] as num?)?.toDouble();

      try {
        await widget.api.saveFarm(
          name: name,
          location: loc,
          areaAcres: area,
          latitude: lat,
          longitude: lon,
          boundary: result.deleted ? null : GeoMath.latLngListToGeoJson(result.points),
          resetBoundary: result.deleted,
        );
        await widget.onFarmUpdated();
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              backgroundColor: AppColors.primary,
              content: Text(result.deleted ? 'Farm boundary deleted.' : 'Farm boundary saved successfully.'),
            ),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(backgroundColor: Colors.red.shade700, content: Text('Failed to update farm boundary: $e')),
          );
        }
      }
    }
  }

  Future<void> _openDrawPlotFlow([Map<String, dynamic>? existingPlot]) async {
    final rawFarmBoundary = widget.farm?['boundary'] as Map<String, dynamic>?;
    final farmPts = GeoMath.geoJsonToLatLngList(rawFarmBoundary);

    if (farmPts.length < 3) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            backgroundColor: AppColors.warning,
            content: Text('Please trace your farm boundary first. All plot boundaries must be contained inside the farm.'),
          ),
        );
      }
      await _openFarmBoundaryDrawer();
      return;
    }

    final plotsList = (widget.farm?['plots'] as List? ?? []).whereType<Map<String, dynamic>>().toList();

    if (existingPlot != null) {
      final existingGeom = existingPlot['geometry'] as Map<String, dynamic>?;
      final existingPts = GeoMath.geoJsonToLatLngList(existingGeom);

      final otherPlots = plotsList.where((p) => p['id'] != existingPlot['id']).toList();

      final result = await Navigator.push<BoundaryResult>(
        context,
        MaterialPageRoute(
          builder: (_) => FieldBoundaryScreen(
            type: BoundaryType.plot,
            initialPoints: existingPts,
            farmBoundary: farmPts,
            existingPlots: otherPlots,
            title: 'Edit: ${existingPlot['name']}',
            crop: existingPlot['crop']?.toString(),
          ),
        ),
      );

      if (result != null) {
        final plotId = int.tryParse(existingPlot['id']?.toString() ?? '') ?? 0;
        final newGeom = result.deleted
            ? null
            : GeoMath.latLngListToGeoJson(result.points);

        try {
          await widget.api.updatePlot(
            plotId,
            name: existingPlot['name']?.toString() ?? 'Plot',
            crop: existingPlot['crop']?.toString() ?? 'Crop',
            areaAcres: result.acres > 0
                ? result.acres
                : ((existingPlot['area_acres'] as num?)?.toDouble() ?? 1.0),
            geometry: newGeom,
            resetGeometry: result.deleted,
          );
          await widget.onFarmUpdated();
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                backgroundColor: AppColors.primary,
                content: Text(result.deleted ? 'Plot boundary cleared.' : 'Plot boundary saved successfully.'),
              ),
            );
          }
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(backgroundColor: Colors.red.shade700, content: Text('Failed to update plot: $e')),
            );
          }
        }
      }
    } else {
      final nameCtrl = TextEditingController(text: 'Plot #${plotsList.length + 1}');
      final cropCtrl = TextEditingController(text: 'Cotton');

      final confirmed = await showDialog<bool>(
        context: context,
        builder: (ctx) => AlertDialog(
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
          title: const Text('New Plot Setup'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameCtrl,
                decoration: InputDecoration(
                  labelText: context.tr('plotNameLabel'),
                  prefixIcon: const Icon(Icons.drive_file_rename_outline),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: cropCtrl,
                decoration: InputDecoration(
                  labelText: context.tr('primaryCropLabel'),
                  prefixIcon: const Icon(Icons.grass),
                ),
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx, false), child: Text(context.tr('cancel'))),
            FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Open Map Drawer')),
          ],
        ),
      );

      if (!mounted) return;
      if (confirmed != true || nameCtrl.text.trim().isEmpty) return;

      final plotName = nameCtrl.text.trim();
      final plotCrop = cropCtrl.text.trim();

      final result = await Navigator.push<BoundaryResult>(
        context,
        MaterialPageRoute(
          builder: (_) => FieldBoundaryScreen(
            type: BoundaryType.plot,
            farmBoundary: farmPts,
            existingPlots: plotsList,
            title: 'Draw: $plotName',
            crop: plotCrop,
          ),
        ),
      );

      if (result != null && result.points.isNotEmpty) {
        final newGeom = GeoMath.latLngListToGeoJson(result.points);

        try {
          await widget.api.createPlot(
            name: plotName,
            crop: plotCrop,
            areaAcres: result.acres,
            geometry: newGeom,
          );
          await widget.onFarmUpdated();
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(backgroundColor: AppColors.primary, content: Text('Plot created with boundary successfully!')),
            );
          }
        } catch (e) {
          if (mounted) {
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(backgroundColor: Colors.red.shade700, content: Text('Failed to save plot: $e')),
            );
          }
        }
      }
    }
  }

  void _showPlotDetailsSheet(Map<String, dynamic> plot) {
    final geom = plot['geometry'] as Map<String, dynamic>?;
    final pts = GeoMath.geoJsonToLatLngList(geom);
    final hasBoundary = pts.length >= 3;
    final areaAcres = hasBoundary ? GeoMath.calculatePolygonAreaAcres(pts) : ((plot['area_acres'] as num?)?.toDouble() ?? 1.0);
    final areaHectares = hasBoundary ? GeoMath.calculatePolygonAreaHectares(pts) : double.parse((areaAcres * 0.404686).toStringAsFixed(2));
    final perimeterM = hasBoundary ? GeoMath.calculatePerimeterMeters(pts).round() : 0;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (ctx) => Padding(
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Center(
              child: Container(
                width: 44,
                height: 4,
                decoration: BoxDecoration(color: AppColors.cardBorder, borderRadius: BorderRadius.circular(2)),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                const CircleAvatar(
                  backgroundColor: AppColors.primaryLight,
                  child: Icon(Icons.grass, color: AppColors.primary),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        plot['name']?.toString() ?? 'Plot',
                        style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                        overflow: TextOverflow.ellipsis,
                      ),
                      Text(
                        '${context.loc.crop(plot['crop']?.toString())} · $areaAcres ${context.tr('acres')}',
                        style: const TextStyle(fontSize: 13, color: AppColors.textMuted),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: hasBoundary ? AppColors.primaryLight : Colors.grey.shade200,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    hasBoundary ? 'Mapped' : 'Unmapped',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: hasBoundary ? AppColors.primary : Colors.grey.shade700,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 18),

            if (hasBoundary) ...[
              Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppColors.cardBg,
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(color: AppColors.cardBorder),
                ),
                child: Column(
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Calculated Field Area', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                        Text('$areaAcres ac ($areaHectares ha)', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppColors.primary)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Field Perimeter', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                        Text('$perimeterM meters', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        const Text('Boundary Corners', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                        Text('${pts.length} points', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('Farm Containment', style: TextStyle(fontSize: 12, color: AppColors.textMuted)),
                        Row(
                          children: [
                            Icon(Icons.check_circle, size: 14, color: Colors.green),
                            SizedBox(width: 4),
                            Text('Inside Property', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.green)),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 18),
            ],

            FilledButton.icon(
              onPressed: () {
                Navigator.pop(ctx);
                _openDrawPlotFlow(plot);
              },
              icon: Icon(hasBoundary ? Icons.edit_location_alt : Icons.draw),
              label: Text(hasBoundary ? 'Edit Field Boundary' : 'Draw Boundary on Satellite Map'),
              style: FilledButton.styleFrom(
                backgroundColor: AppColors.primary,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(height: 10),

            if (hasBoundary) ...[
              OutlinedButton.icon(
                onPressed: () {
                  Navigator.pop(ctx);
                  _confirmClearPlotBoundary(plot);
                },
                icon: const Icon(Icons.layers_clear, size: 16, color: Colors.orange),
                label: const Text('Clear Boundary Only (Keep Plot)', style: TextStyle(color: Colors.orange)),
                style: OutlinedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  side: const BorderSide(color: Colors.orange),
                ),
              ),
              const SizedBox(height: 10),
            ],

            OutlinedButton.icon(
              onPressed: () {
                Navigator.pop(ctx);
                _confirmDeletePlot(plot);
              },
              icon: const Icon(Icons.delete_outline, size: 16, color: Colors.red),
              label: const Text('Delete Plot Permanently', style: TextStyle(color: Colors.red)),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                side: const BorderSide(color: Colors.red),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _confirmClearPlotBoundary(Map<String, dynamic> plot) {
    final plotId = int.tryParse(plot['id']?.toString() ?? '') ?? 0;
    final plotName = plot['name']?.toString() ?? 'Plot';

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: const Text('Clear Plot Boundary?'),
        content: Text('Remove satellite boundary coordinates for "$plotName"? The plot and its crop history will be kept as unmapped.'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: Text(context.tr('cancel'))),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Colors.orange.shade800),
            onPressed: () async {
              Navigator.pop(ctx);
              try {
                await widget.api.updatePlot(
                  plotId,
                  name: plotName,
                  crop: plot['crop']?.toString() ?? 'Crop',
                  areaAcres: (plot['area_acres'] as num?)?.toDouble() ?? 1.0,
                  resetGeometry: true,
                );
                await widget.onFarmUpdated();
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Boundary cleared for "$plotName".')),
                  );
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Failed to clear boundary: $e')),
                  );
                }
              }
            },
            child: const Text('Clear Boundary'),
          ),
        ],
      ),
    );
  }

  void _showAddPlotDialog() {
    final nameCtrl = TextEditingController();
    final cropCtrl = TextEditingController(text: 'Tomato');
    final areaCtrl = TextEditingController(text: '1.5');
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text(context.tr('addPlotTitle')),
        content: SingleChildScrollView(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: nameCtrl,
                decoration: InputDecoration(
                  labelText: context.tr('plotNameLabel'),
                  prefixIcon: const Icon(Icons.drive_file_rename_outline),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: cropCtrl,
                decoration: InputDecoration(
                  labelText: context.tr('primaryCropLabel'),
                  prefixIcon: const Icon(Icons.grass),
                ),
              ),
              const SizedBox(height: 12),
              TextField(
                controller: areaCtrl,
                keyboardType: const TextInputType.numberWithOptions(decimal: true),
                decoration: InputDecoration(
                  labelText: context.tr('areaAcresLabel'),
                  prefixIcon: const Icon(Icons.square_foot),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(context.tr('cancel')),
          ),
          OutlinedButton.icon(
            onPressed: () {
              Navigator.pop(ctx);
              _openDrawPlotFlow();
            },
            icon: const Icon(Icons.satellite_alt, size: 16),
            label: const Text('Draw on Map'),
          ),
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
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Plot created successfully')),
                  );
                }
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

  void _showEditFarmSheet() {
    final currentFarm = widget.farm ?? {};
    final nameCtrl = TextEditingController(
      text: currentFarm['name']?.toString() ?? widget.userProfile['farm_name']?.toString() ?? 'My Family Farm',
    );
    final locCtrl = TextEditingController(
      text: currentFarm['location']?.toString() ?? widget.userProfile['location']?.toString() ?? 'Anand, Gujarat',
    );
    final areaCtrl = TextEditingController(
      text: currentFarm['area_acres']?.toString() ?? '5.0',
    );
    final latCtrl = TextEditingController(
      text: currentFarm['latitude']?.toString() ?? '21.7645',
    );
    final lonCtrl = TextEditingController(
      text: currentFarm['longitude']?.toString() ?? '72.1519',
    );

    final rawHistory = currentFarm['crop_history'];
    final historyStr = rawHistory is List
        ? rawHistory.join(', ')
        : (rawHistory?.toString() ?? 'Cotton, Groundnut');
    final historyCtrl = TextEditingController(text: historyStr);

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(24)),
      ),
      builder: (sheetCtx) => StatefulBuilder(
        builder: (ctx, setModalState) => Padding(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 20,
            bottom: MediaQuery.of(sheetCtx).viewInsets.bottom + 24,
          ),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              mainAxisSize: MainAxisSize.min,
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
                    const Icon(Icons.edit_location_alt_outlined, color: AppColors.primary),
                    const SizedBox(width: 8),
                    Text(
                      context.tr('editFarm'),
                      style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
                const SizedBox(height: 18),
                TextField(
                  controller: nameCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Farm Name',
                    prefixIcon: Icon(Icons.business_outlined),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: locCtrl,
                  decoration: const InputDecoration(
                    labelText: 'Location / Region',
                    prefixIcon: Icon(Icons.place_outlined),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: areaCtrl,
                  keyboardType: const TextInputType.numberWithOptions(decimal: true),
                  decoration: InputDecoration(
                    labelText: 'Total Farm Area (${context.tr('acres')})',
                    prefixIcon: const Icon(Icons.aspect_ratio_outlined),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: latCtrl,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Latitude',
                          prefixIcon: Icon(Icons.navigation_outlined),
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: TextField(
                        controller: lonCtrl,
                        keyboardType: const TextInputType.numberWithOptions(decimal: true),
                        decoration: const InputDecoration(
                          labelText: 'Longitude',
                          prefixIcon: Icon(Icons.explore_outlined),
                        ),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: historyCtrl,
                  decoration: InputDecoration(
                    labelText: context.tr('cropHistory'),
                    prefixIcon: const Icon(Icons.history_edu_outlined),
                    helperText: 'Comma separated list of previous crops',
                  ),
                ),
                const SizedBox(height: 24),
                FilledButton(
                  onPressed: _isSavingFarm
                      ? null
                      : () async {
                          final name = nameCtrl.text.trim();
                          final loc = locCtrl.text.trim();
                          final area = double.tryParse(areaCtrl.text.trim()) ?? 0.0;
                          final lat = double.tryParse(latCtrl.text.trim());
                          final lon = double.tryParse(lonCtrl.text.trim());
                          final history = historyCtrl.text
                              .split(',')
                              .map((s) => s.trim())
                              .where((s) => s.isNotEmpty)
                              .toList();

                          if (name.isEmpty) return;

                          setModalState(() => _isSavingFarm = true);
                          setState(() => _isSavingFarm = true);

                          try {
                            await widget.api.saveFarm(
                              name: name,
                              location: loc,
                              areaAcres: area,
                              latitude: lat,
                              longitude: lon,
                              cropHistory: history,
                            );
                            await widget.onFarmUpdated();
                            if (sheetCtx.mounted) {
                              Navigator.pop(sheetCtx);
                            }
                            if (mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  backgroundColor: AppColors.primary,
                                  content: Text(context.tr('farmSaved')),
                                ),
                              );
                            }
                          } catch (e) {
                            if (mounted) {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  backgroundColor: Colors.red.shade700,
                                  content: Text('Failed to update farm: $e'),
                                ),
                              );
                            }
                          } finally {
                            if (mounted) {
                              setState(() => _isSavingFarm = false);
                            }
                          }
                        },
                  style: FilledButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 14),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: _isSavingFarm
                      ? const SizedBox(
                          height: 20,
                          width: 20,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                        )
                      : Text(context.tr('save'), style: const TextStyle(fontWeight: FontWeight.bold)),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  void _confirmDeletePlot(Map<String, dynamic> plot) {
    final plotId = int.tryParse(plot['id']?.toString() ?? '');
    if (plotId == null) return;
    final plotName = plot['name']?.toString() ?? 'Plot';

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text(context.tr('deletePlot')),
        content: Text('${context.tr('confirmDeletePlot')}\n\n"$plotName"'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(context.tr('cancel')),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Colors.red.shade700),
            onPressed: () async {
              Navigator.pop(ctx);
              setState(() => _isDeletingPlot = true);
              try {
                await widget.api.deletePlot(plotId);
                await widget.onFarmUpdated();
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Plot "$plotName" deleted.')),
                  );
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('Failed to delete plot: $e')),
                  );
                }
              } finally {
                if (mounted) {
                  setState(() => _isDeletingPlot = false);
                }
              }
            },
            child: Text(context.tr('deletePlot')),
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
    final lat = widget.farm?['latitude'] != null ? widget.farm!['latitude'].toString() : null;
    final lon = widget.farm?['longitude'] != null ? widget.farm!['longitude'].toString() : null;

    final rawHistory = widget.farm?['crop_history'];
    final List<String> cropHistoryList = rawHistory is List
        ? rawHistory.map((e) => e.toString()).toList()
        : [];

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

          // Farm Profile Header Card
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: AppColors.cardBg,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: AppColors.cardBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            name,
                            style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                          ),
                          const SizedBox(height: 4),
                          Row(
                            children: [
                              const Icon(Icons.place, size: 16, color: AppColors.textMuted),
                              const SizedBox(width: 4),
                              Expanded(
                                child: Text(
                                  '$location · $area',
                                  style: const TextStyle(color: AppColors.textMuted, fontSize: 13),
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ),
                            ],
                          ),
                          if (lat != null && lon != null) ...[
                            const SizedBox(height: 4),
                            Text(
                              'GPS: $lat, $lon',
                              style: const TextStyle(fontSize: 11, color: AppColors.textSubtle),
                            ),
                          ],
                        ],
                      ),
                    ),
                    IconButton.filledTonal(
                      icon: const Icon(Icons.edit_outlined, size: 18),
                      tooltip: context.tr('editFarm'),
                      onPressed: _showEditFarmSheet,
                    ),
                  ],
                ),
                if (cropHistoryList.isNotEmpty) ...[
                  const SizedBox(height: 12),
                  const Divider(height: 1, color: AppColors.cardBorder),
                  const SizedBox(height: 10),
                  Text(
                    context.tr('cropHistory'),
                    style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: AppColors.textSubtle),
                  ),
                  const SizedBox(height: 6),
                  Wrap(
                    spacing: 6,
                    runSpacing: 6,
                    children: cropHistoryList.map(
                      (c) => Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                        decoration: BoxDecoration(
                          color: AppColors.background,
                          borderRadius: BorderRadius.circular(6),
                          border: Border.all(color: AppColors.cardBorder),
                        ),
                        child: Text(
                          c,
                          style: const TextStyle(fontSize: 12, color: AppColors.textPrimary),
                        ),
                      ),
                    ).toList(),
                  ),
                ],
              ],
            ),
          ),

          const SizedBox(height: 18),

          // Interactive Satellite Map Card (Farm Perimeter + Plots)
          FarmSatelliteCard(
            farm: widget.farm,
            plots: plots,
            onDefineFarmBoundary: _openFarmBoundaryDrawer,
            onEditFarmBoundary: _openFarmBoundaryDrawer,
            onAddPlotOnMap: () => _openDrawPlotFlow(),
            onSelectPlot: (plot) => _showPlotDetailsSheet(plot),
          ),

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
              FilledButton.tonalIcon(
                onPressed: _showAddPlotDialog,
                icon: const Icon(Icons.add, size: 16),
                label: Text(context.tr('addPlotBtn')),
              ),
            ],
          ),
          const SizedBox(height: 12),
          if (plots.isEmpty)
            Container(
              padding: const EdgeInsets.all(28),
              decoration: BoxDecoration(
                color: AppColors.cardBg,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Center(
                child: Column(
                  children: [
                    const Icon(Icons.grass_outlined, size: 40, color: AppColors.textSubtle),
                    const SizedBox(height: 8),
                    Text(context.tr('noPlotsFound'), style: const TextStyle(color: AppColors.textMuted)),
                  ],
                ),
              ),
            )
          else
            ...plots.map(
              (p) {
                final geom = p['geometry'] as Map<String, dynamic>?;
                final pts = GeoMath.geoJsonToLatLngList(geom);
                final hasBoundary = pts.length >= 3;
                return Card(
                  elevation: 0,
                  color: AppColors.cardBg,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                    side: const BorderSide(color: AppColors.cardBorder),
                  ),
                  margin: const EdgeInsets.only(bottom: 12),
                  child: InkWell(
                    borderRadius: BorderRadius.circular(14),
                    onTap: () => _showPlotDetailsSheet(p),
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                      child: Row(
                        children: [
                          CircleAvatar(
                            backgroundColor: hasBoundary ? AppColors.primaryLight : Colors.grey.shade200,
                            child: Icon(
                              hasBoundary ? Icons.layers : Icons.grass,
                              color: hasBoundary ? AppColors.primary : Colors.grey.shade700,
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
                                        p['name']?.toString() ?? 'Plot',
                                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                                        overflow: TextOverflow.ellipsis,
                                      ),
                                    ),
                                    if (hasBoundary) ...[
                                      const SizedBox(width: 6),
                                      Container(
                                        padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                        decoration: BoxDecoration(
                                          color: AppColors.primaryLight,
                                          borderRadius: BorderRadius.circular(6),
                                        ),
                                        child: const Row(
                                          mainAxisSize: MainAxisSize.min,
                                          children: [
                                            Icon(Icons.check_circle, size: 10, color: AppColors.primary),
                                            SizedBox(width: 3),
                                            Text(
                                              'Mapped',
                                              style: TextStyle(
                                                fontSize: 10,
                                                fontWeight: FontWeight.bold,
                                                color: AppColors.primary,
                                              ),
                                            ),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ],
                                ),
                                const SizedBox(height: 3),
                                Text(
                                  '${context.loc.crop(p['crop']?.toString())} · ${p['area_acres'] ?? 1.0} ${context.tr('acres')}',
                                  style: const TextStyle(color: AppColors.textMuted, fontSize: 13),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 8),
                          Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              IconButton(
                                icon: Icon(
                                  hasBoundary ? Icons.edit_location_alt_outlined : Icons.add_location_alt_outlined,
                                  size: 20,
                                  color: hasBoundary ? AppColors.primary : AppColors.textSubtle,
                                ),
                                tooltip: hasBoundary ? 'Edit Field Boundary' : 'Draw Boundary on Map',
                                onPressed: () => _openDrawPlotFlow(p),
                              ),
                              IconButton(
                                icon: const Icon(Icons.delete_outline, size: 20, color: AppColors.textSubtle),
                                tooltip: context.tr('deletePlot'),
                                onPressed: _isDeletingPlot ? null : () => _confirmDeletePlot(p),
                              ),
                            ],
                          ),
                        ],
                      ),
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
