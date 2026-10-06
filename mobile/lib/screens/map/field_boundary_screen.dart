import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import '../../providers/locale_provider.dart';
import '../../theme/app_theme.dart';
import '../../utils/geo_math.dart';

enum BoundaryType { farm, plot }

class BoundaryResult {
  BoundaryResult({
    required this.points,
    required this.acres,
    required this.hectares,
    this.deleted = false,
  });

  final List<LatLng> points;
  final double acres;
  final double hectares;
  final bool deleted;
}

class FieldBoundaryScreen extends StatefulWidget {
  const FieldBoundaryScreen({
    super.key,
    required this.type,
    this.initialPoints = const [],
    this.farmBoundary = const [],
    this.existingPlots = const [],
    this.title,
    this.crop,
    this.centerLat,
    this.centerLon,
    this.onSave,
  });

  final BoundaryType type;
  final List<LatLng> initialPoints;
  final List<LatLng> farmBoundary;
  final List<Map<String, dynamic>> existingPlots;
  final String? title;
  final String? crop;
  final double? centerLat;
  final double? centerLon;
  final void Function(BoundaryResult result)? onSave;

  @override
  State<FieldBoundaryScreen> createState() => _FieldBoundaryScreenState();
}

class _FieldBoundaryScreenState extends State<FieldBoundaryScreen> {
  final MapController _mapController = MapController();

  late List<LatLng> _points;
  late LatLng _mapCenter;
  bool _isSatellite = true;

  // Boundary workflow states
  bool _isClosed = false;
  int? _hoveredPointIndex;
  int? _movingPointIndex;
  LatLng? _originalMovingPointPos;

  @override
  void initState() {
    super.initState();
    _points = List.from(widget.initialPoints);
    _isClosed = _points.length >= 3;
    _mapCenter = _getInitialCenter();
  }

  LatLng _getInitialCenter() {
    if (_points.isNotEmpty) {
      return GeoMath.calculateCentroid(_points);
    }
    if (widget.farmBoundary.isNotEmpty) {
      return GeoMath.calculateCentroid(widget.farmBoundary);
    }
    if (widget.centerLat != null && widget.centerLon != null) {
      return LatLng(widget.centerLat!, widget.centerLon!);
    }
    return const LatLng(21.7645, 72.1519); // Default agricultural belt
  }

  /// Effective crosshair coordinate: if drawing a plot and the center is slightly outside
  /// the farm boundary (within 25m), automatically snaps to the nearest farm perimeter point.
  LatLng get _effectiveCrosshairPosition {
    if (widget.type == BoundaryType.plot && widget.farmBoundary.length >= 3) {
      return GeoMath.snapPlotPointToFarmBoundary(
        point: _mapCenter,
        farmBoundary: widget.farmBoundary,
        maxSnapDistanceMeters: 25.0,
      );
    }
    return _mapCenter;
  }

  /// Whether the crosshair is currently snapped onto the farm boundary line
  bool get _isSnappingToFarm {
    if (widget.type != BoundaryType.plot || widget.farmBoundary.length < 3) return false;
    final snapped = _effectiveCrosshairPosition;
    return (snapped.latitude != _mapCenter.latitude || snapped.longitude != _mapCenter.longitude);
  }

  /// Calculates effective points list accounting for live point-moving and magnetic farm edge snapping
  List<LatLng> get _effectivePoints {
    if (_movingPointIndex == null || _movingPointIndex! >= _points.length) {
      return _points;
    }
    final copy = List<LatLng>.from(_points);
    copy[_movingPointIndex!] = _effectiveCrosshairPosition;
    return copy;
  }

  void _onPositionChanged(MapCamera camera, bool hasGesture) {
    _mapCenter = camera.center;

    // Detect if crosshair hovers close to any existing plot corner (within ~18m snapping distance)
    if (_movingPointIndex == null && _points.isNotEmpty) {
      final nearbyIndex = GeoMath.findNearbyPointIndex(_mapCenter, _points, thresholdMeters: 18.0);
      if (nearbyIndex != _hoveredPointIndex) {
        setState(() {
          _hoveredPointIndex = nearbyIndex;
        });
        return;
      }
    }
    // Update live display coordinates during map pan
    setState(() {});
  }

  /// Adds a new vertex at the current crosshair position (snapped if slightly outside farm)
  void _addPointAtCrosshair() {
    // If hovering on point #1 and we have 3+ points, close the boundary
    if (!_isClosed && _hoveredPointIndex == 0 && _points.length >= 3) {
      _completeBoundary();
      return;
    }

    final pointToAdd = _effectiveCrosshairPosition;
    final wasSnapped = _isSnappingToFarm;

    // Minimum distance check: avoid accidentally creating overlapping points (< 1.5m)
    if (_points.isNotEmpty) {
      final distToLast = GeoMath.distanceMeters(pointToAdd, _points.last);
      if (distToLast < 1.5) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Pan the map away from the last point before adding another corner.'),
            duration: Duration(seconds: 1),
          ),
        );
        return;
      }
    }

    setState(() {
      _points.add(pointToAdd);
      _hoveredPointIndex = _points.length - 1;
    });

    if (wasSnapped) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: const Color(0xfff57f17),
          content: Text(context.tr('cornerSnappedToBoundary')),
          duration: const Duration(seconds: 1),
        ),
      );
    }
  }

  /// Starts moving an existing point with the crosshair
  void _startMovingPoint(int index) {
    if (index < 0 || index >= _points.length) return;
    setState(() {
      _movingPointIndex = index;
      _originalMovingPointPos = _points[index];
      _hoveredPointIndex = null;
    });
    // Center map on this point smoothly
    _mapController.move(_points[index], _mapController.camera.zoom);
  }

  /// Commits the moved point to its new crosshair position (snapped to farm edge if needed)
  void _commitMovedPoint() {
    if (_movingPointIndex == null) return;

    final targetPoint = _effectiveCrosshairPosition;
    final wasSnapped = _isSnappingToFarm;

    // Validation check before dropping
    final effective = List<LatLng>.from(_points);
    effective[_movingPointIndex!] = targetPoint;

    final selfIntersectErr = GeoMath.checkSelfIntersection(effective);
    final containmentErr = (widget.type == BoundaryType.plot &&
            widget.farmBoundary.length >= 3 &&
            effective.length >= 3)
        ? GeoMath.verifyPolygonContainment(effective, widget.farmBoundary)
        : null;

    if (selfIntersectErr != null || containmentErr != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: Colors.red.shade700,
          content: Text(selfIntersectErr ?? containmentErr ?? 'Invalid location for this corner.'),
          duration: const Duration(seconds: 2),
        ),
      );
      return;
    }

    setState(() {
      _points[_movingPointIndex!] = targetPoint;
      _movingPointIndex = null;
      _originalMovingPointPos = null;
      _hoveredPointIndex = null;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: wasSnapped ? const Color(0xfff57f17) : AppColors.primary,
        content: Text(wasSnapped
            ? context.tr('cornerSnappedAndSaved')
            : 'Corner location updated.'),
        duration: const Duration(seconds: 1),
      ),
    );
  }

  /// Cancels moving the point and reverts to original position
  void _cancelMovingPoint() {
    if (_movingPointIndex == null) return;
    setState(() {
      if (_originalMovingPointPos != null) {
        _points[_movingPointIndex!] = _originalMovingPointPos!;
      }
      _movingPointIndex = null;
      _originalMovingPointPos = null;
    });
  }

  /// Deletes a specific point
  void _deletePoint(int index) {
    if (index < 0 || index >= _points.length) return;
    setState(() {
      _points.removeAt(index);
      _hoveredPointIndex = null;
      _movingPointIndex = null;
      if (_points.length < 3) {
        _isClosed = false;
      }
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Deleted corner #${index + 1}'),
        duration: const Duration(seconds: 1),
      ),
    );
  }

  /// Closes and completes the boundary polygon
  void _completeBoundary() {
    if (_points.length < 3) return;
    final selfIntersectErr = GeoMath.checkSelfIntersection(_points);
    final containmentErr = (widget.type == BoundaryType.plot &&
            widget.farmBoundary.length >= 3 &&
            _points.length >= 3)
        ? GeoMath.verifyPolygonContainment(_points, widget.farmBoundary)
        : null;

    if (selfIntersectErr != null || containmentErr != null) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          backgroundColor: Colors.red.shade700,
          content: Text(selfIntersectErr ?? containmentErr ?? 'Please adjust boundary corners to resolve errors.'),
        ),
      );
      return;
    }

    setState(() {
      _isClosed = true;
      _hoveredPointIndex = null;
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        backgroundColor: AppColors.primary,
        content: Text('Boundary closed successfully! You can fine-tune corners or save.'),
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _undo() {
    if (_points.isNotEmpty) {
      setState(() {
        _points.removeLast();
        _hoveredPointIndex = null;
        if (_points.length < 3) {
          _isClosed = false;
        }
      });
    }
  }

  void _clear() {
    if (_points.isNotEmpty) {
      setState(() {
        _points.clear();
        _isClosed = false;
        _hoveredPointIndex = null;
        _movingPointIndex = null;
      });
    }
  }

  void _showDeleteBoundaryDialog() {
    final isFarm = widget.type == BoundaryType.farm;
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
        title: Text(isFarm ? 'Delete Farm Boundary?' : 'Delete Plot Boundary?'),
        content: Text(
          isFarm
              ? 'Removing the farm boundary resets the property fence line. Existing plots will remain, but spatial containment checks will be disabled until a new farm boundary is drawn.'
              : 'Are you sure you want to delete the boundary coordinates for this plot? The plot record will remain as unmapped.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: Text(context.tr('cancel')),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Colors.red.shade700),
            onPressed: () {
              Navigator.pop(ctx);
              final result = BoundaryResult(
                points: const [],
                acres: 0.0,
                hectares: 0.0,
                deleted: true,
              );
              if (widget.onSave != null) {
                widget.onSave!(result);
              }
              Navigator.pop(context, result);
            },
            child: const Text('Delete Boundary'),
          ),
        ],
      ),
    );
  }

  void _saveBoundaryAndExit() {
    final effective = _effectivePoints;
    final acres = GeoMath.calculatePolygonAreaAcres(effective);
    final hectares = GeoMath.calculatePolygonAreaHectares(effective);

    final result = BoundaryResult(
      points: effective,
      acres: acres,
      hectares: hectares,
    );
    if (widget.onSave != null) {
      widget.onSave!(result);
    }
    Navigator.pop(context, result);
  }

  @override
  Widget build(BuildContext context) {
    final isPlot = widget.type == BoundaryType.plot;
    final effective = _effectivePoints;
    final acres = GeoMath.calculatePolygonAreaAcres(effective);
    final hectares = GeoMath.calculatePolygonAreaHectares(effective);
    final perimeterM = GeoMath.calculatePerimeterMeters(effective);

    // Spatial validation checks
    final selfIntersectErr = GeoMath.checkSelfIntersection(effective);
    final containmentErr = (isPlot && widget.farmBoundary.length >= 3 && effective.length >= 3)
        ? GeoMath.verifyPolygonContainment(effective, widget.farmBoundary)
        : null;

    final hasErrors = selfIntersectErr != null || containmentErr != null;
    final canComplete = effective.length >= 3 && !hasErrors;

    final defaultTitle = isPlot
        ? (widget.initialPoints.isNotEmpty ? 'Edit Plot Boundary' : 'Draw Plot Boundary')
        : (widget.initialPoints.isNotEmpty ? 'Edit Farm Boundary' : 'Draw Farm Boundary');
    final screenTitle = widget.title ?? defaultTitle;

    // Crosshair state evaluation
    final isHoveringStart = !_isClosed && _hoveredPointIndex == 0 && effective.length >= 3;
    final isHoveringAnyPoint = _hoveredPointIndex != null && _movingPointIndex == null;
    final isMovingPoint = _movingPointIndex != null;
    final isSnapping = _isSnappingToFarm;
    final snappedTarget = _effectiveCrosshairPosition;

    // Dynamic color for active crosshair
    Color reticleColor;
    if (isMovingPoint) {
      reticleColor = const Color(0xff00b0ff); // Cyan
    } else if (isHoveringStart) {
      reticleColor = const Color(0xff00e676); // Neon Green
    } else if (isSnapping) {
      reticleColor = const Color(0xfff57f17); // Amber Property Gold (Snapping)
    } else if (isHoveringAnyPoint) {
      reticleColor = const Color(0xffffab00); // Amber Corner Highlight
    } else {
      reticleColor = Colors.white;
    }

    return Scaffold(
      appBar: AppBar(
        title: Text(screenTitle, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        elevation: 0,
        actions: [
          if (widget.initialPoints.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_outline, color: Colors.red),
              tooltip: 'Delete Boundary',
              onPressed: _showDeleteBoundaryDialog,
            ),
        ],
      ),
      body: Stack(
        children: [
          // ── FlutterMap Viewport ───────────────────────────────────────────
          FlutterMap(
            mapController: _mapController,
            options: MapOptions(
              initialCenter: _getInitialCenter(),
              initialZoom: 17.5,
              maxZoom: 19.5,
              minZoom: 4.0,
              onPositionChanged: _onPositionChanged,
            ),
            children: [
              // 1. Satellite (ESRI World Imagery) or OSM Roads Tile Layer
              TileLayer(
                urlTemplate: _isSatellite
                    ? 'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
                    : 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
                userAgentPackageName: 'com.smartfarming.mobile',
                maxNativeZoom: 18,
              ),

              // 2. Outer Farm Property Boundary (Amber Gold Fence Line)
              if (isPlot && widget.farmBoundary.length >= 3)
                PolygonLayer(
                  polygons: [
                    Polygon(
                      points: widget.farmBoundary,
                      color: const Color(0xfff57f17).withValues(alpha: 0.08),
                      borderColor: const Color(0xfff57f17),
                      borderStrokeWidth: 2.8,
                    ),
                  ],
                ),

              // 3. Other Existing Cultivated Plots for Context
              if (isPlot && widget.existingPlots.isNotEmpty)
                PolygonLayer(
                  polygons: widget.existingPlots.map((plot) {
                    final geom = plot['geometry'] as Map<String, dynamic>?;
                    final pts = GeoMath.geoJsonToLatLngList(geom);
                    if (pts.length < 3) return null;
                    return Polygon(
                      points: pts,
                      color: Colors.blueGrey.withValues(alpha: 0.20),
                      borderColor: Colors.blueGrey.shade400,
                      borderStrokeWidth: 1.5,
                    );
                  }).whereType<Polygon>().toList(),
                ),

              // 4. Closed Boundary Polygon Fill (when closed or 3+ points)
              if (effective.length >= 3 && (_isClosed || isMovingPoint))
                PolygonLayer(
                  polygons: [
                    Polygon(
                      points: effective,
                      color: hasErrors
                          ? Colors.red.withValues(alpha: 0.18)
                          : (isPlot
                              ? const Color(0xff00e676).withValues(alpha: 0.22)
                              : const Color(0xfff57f17).withValues(alpha: 0.18)),
                      borderColor: Colors.transparent,
                    ),
                  ],
                ),

              // 5. Active Boundary Perimeter Polyline
              if (effective.length >= 2)
                PolylineLayer(
                  polylines: [
                    Polyline(
                      points: (_isClosed || isMovingPoint) && effective.length >= 3
                          ? [...effective, effective.first]
                          : effective,
                      color: hasErrors
                          ? Colors.red
                          : (isPlot ? const Color(0xff00e676) : const Color(0xfff57f17)),
                      strokeWidth: 3.5,
                    ),
                  ],
                ),

              // 6. Dynamic Rubber-Band Guide Line (from last point to crosshair or snapped point)
              if (!_isClosed && !isMovingPoint && effective.isNotEmpty)
                PolylineLayer(
                  polylines: [
                    Polyline(
                      points: [
                        effective.last,
                        isHoveringStart ? effective.first : snappedTarget,
                      ],
                      color: isHoveringStart
                          ? const Color(0xff00e676)
                          : (isSnapping
                              ? const Color(0xfff57f17)
                              : Colors.white.withValues(alpha: 0.85)),
                      strokeWidth: (isHoveringStart || isSnapping) ? 3.0 : 2.0,
                    ),
                  ],
                ),

              // 7. Magnetic Snap Projection Vector & Indicator (when snapping to farm boundary)
              if (isSnapping) ...[
                PolylineLayer(
                  polylines: [
                    Polyline(
                      points: [_mapCenter, snappedTarget],
                      color: const Color(0xfff57f17).withValues(alpha: 0.9),
                      strokeWidth: 2.2,
                    ),
                  ],
                ),
                MarkerLayer(
                  markers: [
                    Marker(
                      point: snappedTarget,
                      width: 24,
                      height: 24,
                      child: Container(
                        decoration: BoxDecoration(
                          color: const Color(0xfff57f17),
                          shape: BoxShape.circle,
                          border: Border.all(color: Colors.white, width: 2),
                          boxShadow: const [BoxShadow(color: Colors.black45, blurRadius: 4)],
                        ),
                        alignment: Alignment.center,
                        child: const Icon(Icons.flash_on, size: 14, color: Colors.white),
                      ),
                    ),
                  ],
                ),
              ],

              // 8. Numbered Corner Vertex Markers
              MarkerLayer(
                markers: [
                  for (int i = 0; i < effective.length; i++)
                    Marker(
                      point: effective[i],
                      width: 34,
                      height: 34,
                      child: GestureDetector(
                        onTap: () {
                          // Tapping marker centers crosshair on it
                          _mapController.move(effective[i], _mapController.camera.zoom);
                          setState(() => _hoveredPointIndex = i);
                        },
                        child: AnimatedContainer(
                          duration: const Duration(milliseconds: 200),
                          decoration: BoxDecoration(
                            color: _hoveredPointIndex == i
                                ? const Color(0xffffab00)
                                : (_movingPointIndex == i
                                    ? const Color(0xff00b0ff)
                                    : (hasErrors
                                        ? Colors.red
                                        : (isPlot ? AppColors.primary : const Color(0xfff57f17)))),
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: _hoveredPointIndex == i ? Colors.amber.shade100 : Colors.white,
                              width: _hoveredPointIndex == i ? 3 : 2,
                            ),
                            boxShadow: [
                              BoxShadow(
                                color: _hoveredPointIndex == i
                                    ? Colors.amber.withValues(alpha: 0.6)
                                    : Colors.black45,
                                blurRadius: _hoveredPointIndex == i ? 8 : 4,
                                spreadRadius: _hoveredPointIndex == i ? 2 : 0,
                              ),
                            ],
                          ),
                          alignment: Alignment.center,
                          child: Text(
                            '${i + 1}',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),

          // ── Fixed Screen-Center Small Cross Icon ──────────────────────────
          IgnorePointer(
            child: Center(
              child: SizedBox(
                width: 24,
                height: 24,
                child: Stack(
                  alignment: Alignment.center,
                  children: [
                    // High-contrast shadow behind cross for dark & light satellite imagery
                    Icon(
                      Icons.add,
                      size: 22,
                      color: Colors.black.withValues(alpha: 0.8),
                      shadows: const [
                        Shadow(color: Colors.black54, blurRadius: 4),
                      ],
                    ),
                    // Small cross icon with dynamic state color
                    Icon(
                      Icons.add,
                      size: 20,
                      color: reticleColor,
                    ),
                  ],
                ),
              ),
            ),
          ),

          // ── Floating Crosshair Context Badge ──────────────────────────────
          if (isMovingPoint || isHoveringAnyPoint || isHoveringStart || isSnapping)
            Positioned(
              top: MediaQuery.of(context).size.height * 0.5 - 48,
              left: 20,
              right: 20,
              child: Center(
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 5),
                  decoration: BoxDecoration(
                    color: isMovingPoint
                        ? const Color(0xff0091ea)
                        : (isHoveringStart
                            ? const Color(0xff00c853)
                            : (isSnapping ? const Color(0xfff57f17) : const Color(0xffff8f00))),
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: const [BoxShadow(color: Colors.black38, blurRadius: 6)],
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        isMovingPoint
                            ? Icons.open_with
                            : (isHoveringStart
                                ? Icons.check_circle
                                : (isSnapping ? Icons.flash_on : Icons.gps_fixed)),
                        size: 14,
                        color: Colors.white,
                      ),
                      const SizedBox(width: 6),
                      Text(
                        isMovingPoint
                            ? (isSnapping
                                ? 'Moving Corner #${_movingPointIndex! + 1} (Snapping to Edge)'
                                : 'Moving Corner #${_movingPointIndex! + 1}')
                            : (isHoveringStart
                                ? 'Start Point · Tap + to Close'
                                : (isSnapping
                                    ? context.tr('snappingToBoundary')
                                    : 'Targeting Corner #${_hoveredPointIndex! + 1}')),
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),

          // ── Top Telemetry & Spatial Validation Card ───────────────────────
          Positioned(
            top: 12,
            left: 14,
            right: 14,
            child: Column(
              children: [
                // Error Alert Banner
                if (hasErrors)
                  Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      color: const Color(0xffd32f2f),
                      borderRadius: BorderRadius.circular(12),
                      boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 4)],
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: Colors.white, size: 20),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Text(
                            selfIntersectErr ?? containmentErr ?? 'Invalid boundary configuration',
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                // Main Info Card
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: const [
                      BoxShadow(color: Colors.black12, blurRadius: 8, offset: Offset(0, 2))
                    ],
                  ),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      // Area (Acres & Hectares)
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.aspect_ratio, size: 16, color: AppColors.primary),
                              const SizedBox(width: 4),
                              Text(
                                '$acres ac',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                            ],
                          ),
                          Text(
                            '$hectares ha',
                            style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                          ),
                        ],
                      ),
                      Container(width: 1, height: 30, color: AppColors.cardBorder),

                      // Perimeter
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.straighten, size: 16, color: AppColors.primary),
                              const SizedBox(width: 4),
                              Text(
                                '${perimeterM.round()} m',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 16,
                                  color: AppColors.textPrimary,
                                ),
                              ),
                            ],
                          ),
                          const Text(
                            'Perimeter',
                            style: TextStyle(fontSize: 11, color: AppColors.textMuted),
                          ),
                        ],
                      ),
                      Container(width: 1, height: 30, color: AppColors.cardBorder),

                      // Status Badge
                      Column(
                        crossAxisAlignment: CrossAxisAlignment.end,
                        children: [
                          if (effective.length < 3)
                            Text(
                              '${3 - effective.length} pts needed',
                              style: const TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: Colors.orange,
                              ),
                            )
                          else if (hasErrors)
                            const Text(
                              'Violation',
                              style: TextStyle(
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                                color: Colors.red,
                              ),
                            )
                          else
                            Row(
                              children: [
                                const Icon(Icons.check_circle, size: 14, color: Colors.green),
                                const SizedBox(width: 4),
                                Text(
                                  _isClosed ? 'Closed' : (isPlot ? 'In Farm' : 'Valid'),
                                  style: const TextStyle(
                                    fontSize: 12,
                                    fontWeight: FontWeight.bold,
                                    color: Colors.green,
                                  ),
                                ),
                              ],
                            ),
                          Text(
                            '${effective.length} corners',
                            style: const TextStyle(fontSize: 11, color: AppColors.textMuted),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          // ── Map Floating Action Buttons (Right Side) ───────────────────────
          Positioned(
            right: 14,
            top: 96,
            child: Column(
              children: [
                FloatingActionButton.small(
                  heroTag: 'map_layer_toggle',
                  backgroundColor: Colors.white,
                  onPressed: () => setState(() => _isSatellite = !_isSatellite),
                  tooltip: _isSatellite ? 'Roads View' : 'Satellite View',
                  child: Icon(
                    _isSatellite ? Icons.map_outlined : Icons.satellite_alt_outlined,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(height: 8),
                FloatingActionButton.small(
                  heroTag: 'map_recenter',
                  backgroundColor: Colors.white,
                  onPressed: () => _mapController.move(_getInitialCenter(), 17.5),
                  tooltip: 'Re-center Map',
                  child: const Icon(Icons.my_location, color: AppColors.primary),
                ),
                const SizedBox(height: 8),
                FloatingActionButton.small(
                  heroTag: 'map_zoom_in',
                  backgroundColor: Colors.white,
                  onPressed: () => _mapController.move(
                    _mapController.camera.center,
                    _mapController.camera.zoom + 1,
                  ),
                  child: const Icon(Icons.add, color: AppColors.primary),
                ),
                const SizedBox(height: 8),
                FloatingActionButton.small(
                  heroTag: 'map_zoom_out',
                  backgroundColor: Colors.white,
                  onPressed: () => _mapController.move(
                    _mapController.camera.center,
                    _mapController.camera.zoom - 1,
                  ),
                  child: const Icon(Icons.remove, color: AppColors.primary),
                ),
              ],
            ),
          ),

          // ── Contextual Bottom Action Bar ──────────────────────────────────
          Positioned(
            bottom: 24,
            left: 14,
            right: 14,
            child: _buildContextualBottomBar(canComplete, hasErrors),
          ),
        ],
      ),
    );
  }

  /// Builds dynamic bottom bar depending on current user state
  Widget _buildContextualBottomBar(bool canComplete, bool hasErrors) {
    // ── STATE 1: Moving a Corner Point with the Crosshair ───────────────────
    if (_movingPointIndex != null) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 4))],
        ),
        child: Row(
          children: [
            OutlinedButton.icon(
              onPressed: _cancelMovingPoint,
              icon: const Icon(Icons.close, size: 18),
              label: const Text('Cancel'),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: FilledButton.icon(
                onPressed: hasErrors ? null : _commitMovedPoint,
                icon: const Icon(Icons.check, size: 20),
                label: Text(
                  _isSnappingToFarm ? 'Snap & Set Location' : 'Set New Location',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                style: FilledButton.styleFrom(
                  backgroundColor: hasErrors
                      ? Colors.grey
                      : (_isSnappingToFarm ? const Color(0xfff57f17) : const Color(0xff0091ea)),
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
          ],
        ),
      );
    }

    // ── STATE 2: Crosshair Hovering an Existing Point ───────────────────────
    if (_hoveredPointIndex != null) {
      final idx = _hoveredPointIndex!;
      final isHoveringFirstAndCanClose = !_isClosed && idx == 0 && _points.length >= 3;

      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 4))],
        ),
        child: Row(
          children: [
            // Delete Corner button
            IconButton.filledTonal(
              onPressed: () => _deletePoint(idx),
              icon: const Icon(Icons.delete_outline, color: Colors.red, size: 20),
              tooltip: 'Delete Corner #${idx + 1}',
            ),
            const SizedBox(width: 8),

            // Move Corner button
            IconButton.filledTonal(
              onPressed: () => _startMovingPoint(idx),
              icon: const Icon(Icons.open_with, color: Colors.blueAccent, size: 20),
              tooltip: 'Move Corner #${idx + 1}',
            ),
            const SizedBox(width: 10),

            // Action / Complete / Add button
            Expanded(
              child: isHoveringFirstAndCanClose
                  ? FilledButton.icon(
                      onPressed: hasErrors ? null : _completeBoundary,
                      icon: const Icon(Icons.check_circle, size: 20),
                      label: const Text('Close Boundary', style: TextStyle(fontWeight: FontWeight.bold)),
                      style: FilledButton.styleFrom(
                        backgroundColor: hasErrors ? Colors.grey : const Color(0xff00c853),
                        padding: const EdgeInsets.symmetric(vertical: 13),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    )
                  : OutlinedButton.icon(
                      onPressed: () => setState(() => _hoveredPointIndex = null),
                      icon: const Icon(Icons.arrow_forward, size: 16),
                      label: Text('Pan Away from #${idx + 1}', style: const TextStyle(fontSize: 12)),
                      style: OutlinedButton.styleFrom(
                        padding: const EdgeInsets.symmetric(vertical: 12),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      ),
                    ),
            ),
          ],
        ),
      );
    }

    // ── STATE 3: Boundary Closed & Ready to Save ───────────────────────────
    if (_isClosed && _points.length >= 3 && !hasErrors) {
      return Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(20),
          boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 4))],
        ),
        child: Row(
          children: [
            OutlinedButton.icon(
              onPressed: () => setState(() => _isClosed = false),
              icon: const Icon(Icons.edit_outlined, size: 18),
              label: const Text('Edit Shape'),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 13),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: FilledButton.icon(
                onPressed: _saveBoundaryAndExit,
                icon: const Icon(Icons.save_outlined, size: 20),
                label: const Text('Save Boundary', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                style: FilledButton.styleFrom(
                  backgroundColor: AppColors.primary,
                  padding: const EdgeInsets.symmetric(vertical: 13),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ),
          ],
        ),
      );
    }

    // ── STATE 4: Normal Crosshair Boundary Drawing ─────────────────────────
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(22),
        boxShadow: const [BoxShadow(color: Colors.black26, blurRadius: 10, offset: Offset(0, 4))],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          // Undo last point
          IconButton.filledTonal(
            onPressed: _points.isNotEmpty ? _undo : null,
            icon: const Icon(Icons.undo, size: 20),
            tooltip: 'Undo Last Corner',
          ),

          // Big prominent Center (+) Add Point Button
          FilledButton.icon(
            onPressed: _addPointAtCrosshair,
            icon: Icon(_isSnappingToFarm ? Icons.flash_on : Icons.add, size: 24),
            label: Text(
              _isSnappingToFarm
                  ? 'Snap to Farm'
                  : (_points.isEmpty ? 'Start Point' : 'Add Corner'),
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
            ),
            style: FilledButton.styleFrom(
              backgroundColor: _isSnappingToFarm ? const Color(0xfff57f17) : AppColors.primary,
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
              elevation: 3,
            ),
          ),

          // Complete Boundary button (visible when 3+ points placed)
          if (canComplete)
            IconButton.filled(
              onPressed: _completeBoundary,
              icon: const Icon(Icons.check_circle_outline, size: 22),
              tooltip: 'Complete Boundary',
              style: IconButton.styleFrom(
                backgroundColor: const Color(0xff00c853),
                foregroundColor: Colors.white,
              ),
            )
          else
            IconButton.filledTonal(
              onPressed: _points.isNotEmpty ? _clear : null,
              icon: const Icon(Icons.clear_all, size: 20),
              tooltip: 'Clear All Points',
            ),
        ],
      ),
    );
  }
}
