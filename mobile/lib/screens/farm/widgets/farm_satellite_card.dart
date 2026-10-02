import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../../providers/locale_provider.dart';
import '../../../theme/app_theme.dart';
import '../../../utils/geo_math.dart';

class FarmSatelliteCard extends StatelessWidget {
  const FarmSatelliteCard({
    super.key,
    required this.farm,
    required this.plots,
    required this.onDefineFarmBoundary,
    required this.onEditFarmBoundary,
    required this.onAddPlotOnMap,
    required this.onSelectPlot,
  });

  final Map<String, dynamic>? farm;
  final List<dynamic> plots;
  final VoidCallback onDefineFarmBoundary;
  final VoidCallback onEditFarmBoundary;
  final VoidCallback onAddPlotOnMap;
  final ValueChanged<Map<String, dynamic>> onSelectPlot;

  Color _getCropColor(String? crop) {
    switch (crop?.toLowerCase()) {
      case 'cotton':
        return const Color(0xff00bcd4);
      case 'tomato':
        return const Color(0xfff44336);
      case 'potato':
        return const Color(0xffff9800);
      case 'wheat':
        return const Color(0xffffc107);
      case 'corn':
      case 'maize':
        return const Color(0xff8bc34a);
      case 'groundnut':
      case 'peanut':
        return const Color(0xff795548);
      case 'pepper':
      case 'bell pepper':
      case 'chilli':
        return const Color(0xff4caf50);
      default:
        return AppColors.primary;
    }
  }

  @override
  Widget build(BuildContext context) {
    final rawBoundary = farm?['boundary'] as Map<String, dynamic>?;
    final farmPts = GeoMath.geoJsonToLatLngList(rawBoundary);
    final hasFarmBoundary = farmPts.length >= 3;

    final farmAreaAcres = hasFarmBoundary
        ? GeoMath.calculatePolygonAreaAcres(farmPts)
        : (farm?['area_acres'] != null ? (farm!['area_acres'] as num).toDouble() : 0.0);

    // Initial center for preview
    LatLng center;
    if (farmPts.isNotEmpty) {
      center = farmPts.first;
    } else if (farm?['latitude'] != null && farm?['longitude'] != null) {
      center = LatLng(
        (farm!['latitude'] as num).toDouble(),
        (farm!['longitude'] as num).toDouble(),
      );
    } else {
      center = const LatLng(21.7645, 72.1519);
    }

    // Build plot polygons
    final plotPolygons = <Polygon>[];
    for (final p in plots) {
      if (p is Map<String, dynamic>) {
        final geom = p['geometry'] as Map<String, dynamic>?;
        final pts = GeoMath.geoJsonToLatLngList(geom);
        if (pts.length >= 3) {
          final cColor = _getCropColor(p['crop']?.toString());
          plotPolygons.add(
            Polygon(
              points: pts,
              color: cColor.withValues(alpha: 0.32),
              borderColor: cColor,
              borderStrokeWidth: 2.0,
            ),
          );
        }
      }
    }

    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardBg,
        borderRadius: BorderRadius.circular(18),
        border: Border.all(color: AppColors.cardBorder),
        boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 6, offset: Offset(0, 2))],
      ),
      clipBehavior: Clip.antiAlias,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // ── Map Viewport Header ───────────────────────────────────────────
          SizedBox(
            height: 190,
            child: Stack(
              children: [
                FlutterMap(
                  options: MapOptions(
                    initialCenter: center,
                    initialZoom: hasFarmBoundary ? 16.2 : 15.0,
                    interactionOptions: const InteractionOptions(
                      flags: InteractiveFlag.none, // Static non-blocking preview in list
                    ),
                  ),
                  children: [
                    // Satellite Imagery Layer
                    TileLayer(
                      urlTemplate: 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
                      userAgentPackageName: 'com.smartfarming.mobile',
                      maxNativeZoom: 18,
                    ),

                    // Farm Boundary Perimeter (Golden Amber Outline)
                    if (hasFarmBoundary)
                      PolygonLayer(
                        polygons: [
                          Polygon(
                            points: farmPts,
                            color: const Color(0xfff57f17).withValues(alpha: 0.12),
                            borderColor: const Color(0xfff57f17),
                            borderStrokeWidth: 2.5,
                          ),
                        ],
                      ),

                    // Cultivated Plot Polygons
                    if (plotPolygons.isNotEmpty)
                      PolygonLayer(polygons: plotPolygons),
                  ],
                ),

                // Top Badge: Boundary Status
                Positioned(
                  top: 10,
                  left: 10,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.75),
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: Colors.white24),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(
                          hasFarmBoundary ? Icons.check_circle : Icons.warning_amber_rounded,
                          size: 14,
                          color: hasFarmBoundary ? const Color(0xff00e676) : Colors.amberAccent,
                        ),
                        const SizedBox(width: 6),
                        Text(
                          hasFarmBoundary ? 'Farm Boundary: Active ($farmAreaAcres ac)' : 'No Farm Boundary Set',
                          style: const TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.bold),
                        ),
                      ],
                    ),
                  ),
                ),

                // Top Right Badge: Plotted fields count
                Positioned(
                  top: 10,
                  right: 10,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 5),
                    decoration: BoxDecoration(
                      color: AppColors.primary,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      '${plotPolygons.length} of ${plots.length} Mapped',
                      style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // ── Bottom Action Controls ────────────────────────────────────────
          Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                if (!hasFarmBoundary)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 10),
                    child: Text(
                      'Trace your property fence line first to establish the farm perimeter. All plots will be kept within this boundary.',
                      style: TextStyle(fontSize: 12, color: AppColors.textMuted, height: 1.3),
                    ),
                  ),

                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: hasFarmBoundary ? onEditFarmBoundary : onDefineFarmBoundary,
                        icon: Icon(
                          hasFarmBoundary ? Icons.edit_location_alt : Icons.add_location_alt,
                          size: 16,
                          color: AppColors.primary,
                        ),
                        label: Text(
                          hasFarmBoundary ? 'Edit Farm Perimeter' : 'Define Farm Perimeter',
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                          overflow: TextOverflow.ellipsis,
                        ),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: FilledButton.icon(
                        onPressed: hasFarmBoundary ? onAddPlotOnMap : null,
                        icon: const Icon(Icons.draw, size: 16),
                        label: Text(
                          context.tr('drawPlotBoundary'),
                          style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                          overflow: TextOverflow.ellipsis,
                        ),
                        style: FilledButton.styleFrom(
                          backgroundColor: hasFarmBoundary ? AppColors.primary : Colors.grey.shade400,
                          padding: const EdgeInsets.symmetric(vertical: 10, horizontal: 8),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
