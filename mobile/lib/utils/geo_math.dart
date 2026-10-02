import 'dart:math' as math;
import 'package:latlong2/latlong.dart';

/// Comprehensive geographic and geometric calculation utilities for farm and plot boundaries.
class GeoMath {
  GeoMath._();

  static const double earthRadiusMeters = 6371008.8;
  static const double metersPerDegreeLat = 111132.92;
  static const double sqMetersPerAcre = 4046.8564224;

  /// Computes geodesic planar meters conversion factor for longitude at a given latitude.
  static double metersPerDegreeLon(double latitudeDeg) {
    final rad = latitudeDeg * (math.pi / 180.0);
    return 111412.84 * math.cos(rad);
  }

  /// Calculates geodesic polygon area using the Shoelace formula on a locally projected plane.
  /// Returns area in square meters.
  static double calculatePolygonAreaSqMeters(List<LatLng> points) {
    if (points.length < 3) return 0.0;

    // Centroid latitude for local planar projection
    double sumLat = 0.0;
    for (final p in points) {
      sumLat += p.latitude;
    }
    final meanLat = sumLat / points.length;
    final mPerLon = metersPerDegreeLon(meanLat);

    // Project points to local (x, y) coordinates in meters relative to first point
    final origin = points.first;
    final planar = points.map((p) {
      final x = (p.longitude - origin.longitude) * mPerLon;
      final y = (p.latitude - origin.latitude) * metersPerDegreeLat;
      return math.Point<double>(x, y);
    }).toList();

    // Shoelace formula
    double area = 0.0;
    final n = planar.length;
    for (int i = 0; i < n; i++) {
      final j = (i + 1) % n;
      area += planar[i].x * planar[j].y;
      area -= planar[j].x * planar[i].y;
    }
    return (area.abs() / 2.0);
  }

  /// Calculates area in acres (rounded to 2 decimal places).
  static double calculatePolygonAreaAcres(List<LatLng> points) {
    final sqM = calculatePolygonAreaSqMeters(points);
    return double.parse((sqM / sqMetersPerAcre).toStringAsFixed(2));
  }

  /// Calculates area in hectares (rounded to 2 decimal places).
  static double calculatePolygonAreaHectares(List<LatLng> points) {
    final sqM = calculatePolygonAreaSqMeters(points);
    return double.parse((sqM / 10000.0).toStringAsFixed(2));
  }

  /// Computes geodesic distance between two coordinates using the Haversine formula (in meters).
  static double distanceMeters(LatLng p1, LatLng p2) {
    const d2r = math.pi / 180.0;
    final dLat = (p2.latitude - p1.latitude) * d2r;
    final dLon = (p2.longitude - p1.longitude) * d2r;
    final a = math.sin(dLat / 2) * math.sin(dLat / 2) +
        math.cos(p1.latitude * d2r) *
            math.cos(p2.latitude * d2r) *
            math.sin(dLon / 2) *
            math.sin(dLon / 2);
    final c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a));
    return earthRadiusMeters * c;
  }

  /// Calculates the total perimeter of a polygon in meters.
  static double calculatePerimeterMeters(List<LatLng> points) {
    if (points.length < 2) return 0.0;
    double perimeter = 0.0;
    for (int i = 0; i < points.length; i++) {
      final p1 = points[i];
      final p2 = points[(i + 1) % points.length];
      perimeter += distanceMeters(p1, p2);
    }
    return perimeter;
  }

  /// Calculates the geometric centroid of a list of coordinates.
  static LatLng calculateCentroid(List<LatLng> points) {
    if (points.isEmpty) return const LatLng(21.7645, 72.1519);
    double sumLat = 0.0;
    double sumLon = 0.0;
    for (final p in points) {
      sumLat += p.latitude;
      sumLon += p.longitude;
    }
    return LatLng(sumLat / points.length, sumLon / points.length);
  }

  /// Finds the index of the nearest point in [points] to [target] within [thresholdMeters].
  /// Returns null if no point is within the threshold.
  static int? findNearbyPointIndex(
    LatLng target,
    List<LatLng> points, {
    double thresholdMeters = 15.0,
  }) {
    int? bestIndex;
    double bestDist = thresholdMeters;
    for (int i = 0; i < points.length; i++) {
      final d = distanceMeters(target, points[i]);
      if (d <= bestDist) {
        bestDist = d;
        bestIndex = i;
      }
    }
    return bestIndex;
  }

  /// Projects point [p] onto line segment [a] -> [b] and returns the closest point on the segment.
  static LatLng findClosestPointOnSegment(LatLng p, LatLng a, LatLng b) {
    final mPerLon = metersPerDegreeLon(p.latitude);
    final ax = (a.longitude - p.longitude) * mPerLon;
    final ay = (a.latitude - p.latitude) * metersPerDegreeLat;
    final bx = (b.longitude - p.longitude) * mPerLon;
    final by = (b.latitude - p.latitude) * metersPerDegreeLat;

    final abx = bx - ax;
    final aby = by - ay;
    final abLenSq = abx * abx + aby * aby;
    if (abLenSq <= 0.0001) return a;

    final apx = -ax;
    final apy = -ay;
    final t = (apx * abx + apy * aby) / abLenSq;
    final tClamped = t.clamp(0.0, 1.0);

    final qx = ax + tClamped * abx;
    final qy = ay + tClamped * aby;

    final qLon = p.longitude + (qx / mPerLon);
    final qLat = p.latitude + (qy / metersPerDegreeLat);
    return LatLng(qLat, qLon);
  }

  /// Finds the closest point on the perimeter of [polygon] to target point [p].
  static LatLng findClosestPointOnPolygonPerimeter(LatLng p, List<LatLng> polygon) {
    if (polygon.length < 2) return p;
    double minDistance = double.infinity;
    LatLng closestPoint = polygon.first;

    final n = polygon.length;
    for (int i = 0; i < n; i++) {
      final a = polygon[i];
      final b = polygon[(i + 1) % n];
      final q = findClosestPointOnSegment(p, a, b);
      final dist = distanceMeters(p, q);
      if (dist < minDistance) {
        minDistance = dist;
        closestPoint = q;
      }
    }
    return closestPoint;
  }

  /// Nudges point [from] slightly towards point [to] by [nudgeDistMeters].
  static LatLng nudgePointTowards(LatLng from, LatLng to, double nudgeDistMeters) {
    final totalDist = distanceMeters(from, to);
    if (totalDist <= nudgeDistMeters || totalDist == 0) return to;
    final fraction = nudgeDistMeters / totalDist;
    final dLat = to.latitude - from.latitude;
    final dLon = to.longitude - from.longitude;
    return LatLng(from.latitude + dLat * fraction, from.longitude + dLon * fraction);
  }

  /// Snaps a plot point to the farm boundary if it is slightly outside (up to [maxSnapDistanceMeters]).
  /// If the point is already inside, returns the point unchanged.
  /// If the point is snapped, nudges it 10cm inward to guarantee strict containment.
  static LatLng snapPlotPointToFarmBoundary({
    required LatLng point,
    required List<LatLng> farmBoundary,
    double maxSnapDistanceMeters = 25.0,
  }) {
    if (farmBoundary.length < 3) return point;

    // If point is already inside the farm boundary, no snap needed
    if (isPointInsidePolygon(point, farmBoundary)) {
      return point;
    }

    // Point is outside: find closest point on farm boundary
    final closest = findClosestPointOnPolygonPerimeter(point, farmBoundary);
    final dist = distanceMeters(point, closest);

    if (dist <= maxSnapDistanceMeters) {
      final centroid = calculateCentroid(farmBoundary);
      return nudgePointTowards(closest, centroid, 0.10);
    }

    return point;
  }

  /// Returns true if two line segments (p1->p2) and (p3->p4) intersect.
  static bool doSegmentsIntersect(LatLng p1, LatLng p2, LatLng p3, LatLng p4) {
    // 2D cross-product orientation test
    double ccw(LatLng a, LatLng b, LatLng c) {
      return (c.latitude - a.latitude) * (b.longitude - a.longitude) -
          (b.latitude - a.latitude) * (c.longitude - a.longitude);
    }

    final d1 = ccw(p1, p2, p3);
    final d2 = ccw(p1, p2, p4);
    final d3 = ccw(p3, p4, p1);
    final d4 = ccw(p3, p4, p2);

    if (((d1 > 0 && d2 < 0) || (d1 < 0 && d2 > 0)) &&
        ((d3 > 0 && d4 < 0) || (d3 < 0 && d4 > 0))) {
      return true;
    }
    return false;
  }

  /// Checks if a sequence of points creates a self-intersecting polygon.
  /// Returns null if valid, or a descriptive error if lines cross each other.
  static String? checkSelfIntersection(List<LatLng> points) {
    if (points.length < 4) return null;

    final n = points.length;
    for (int i = 0; i < n; i++) {
      final a1 = points[i];
      final a2 = points[(i + 1) % n];

      for (int j = i + 1; j < n; j++) {
        // Skip adjacent edges and the closing edge with first edge
        if ((j - i).abs() <= 1 || (i == 0 && j == n - 1)) continue;

        final b1 = points[j];
        final b2 = points[(j + 1) % n];

        if (doSegmentsIntersect(a1, a2, b1, b2)) {
          return 'Lines between points #${i + 1}-#${(i + 1) % n + 1} and #${j + 1}-#${(j + 1) % n + 1} cross each other.';
        }
      }
    }
    return null;
  }

  /// Tests whether a given point is strictly inside a closed polygon (Ray-Casting Algorithm).
  static bool isPointInsidePolygon(LatLng point, List<LatLng> polygon) {
    if (polygon.length < 3) return false;

    bool inside = false;
    final x = point.longitude;
    final y = point.latitude;
    final n = polygon.length;

    for (int i = 0, j = n - 1; i < n; j = i++) {
      final xi = polygon[i].longitude;
      final yi = polygon[i].latitude;
      final xj = polygon[j].longitude;
      final yj = polygon[j].latitude;

      final intersect = ((yi > y) != (yj > y)) &&
          (x < (xj - xi) * (y - yi) / (yj - yi) + xi);
      if (intersect) inside = !inside;
    }

    return inside;
  }

  /// Verifies whether an inner polygon is completely contained inside an outer polygon.
  /// Returns null if valid, or an error string specifying the out-of-bounds vertex or crossing edge.
  static String? verifyPolygonContainment(
    List<LatLng> innerPolygon,
    List<LatLng> outerPolygon, {
    String innerName = 'Plot',
    String outerName = 'farm boundary',
  }) {
    if (outerPolygon.length < 3) {
      return 'No valid $outerName defined.';
    }

    // 1. Every vertex of inner polygon must be inside outer polygon
    for (int i = 0; i < innerPolygon.length; i++) {
      final pt = innerPolygon[i];
      if (!isPointInsidePolygon(pt, outerPolygon)) {
        return '$innerName corner #${i + 1} is outside the $outerName.';
      }
    }

    // 2. No edge of inner polygon may intersect any edge of outer polygon
    for (int i = 0; i < innerPolygon.length; i++) {
      final p1 = innerPolygon[i];
      final p2 = innerPolygon[(i + 1) % innerPolygon.length];

      for (int j = 0; j < outerPolygon.length; j++) {
        final q1 = outerPolygon[j];
        final q2 = outerPolygon[(j + 1) % outerPolygon.length];

        if (doSegmentsIntersect(p1, p2, q1, q2)) {
          return '$innerName edge between #${i + 1} and #${(i + 1) % innerPolygon.length + 1} crosses outside the $outerName.';
        }
      }
    }

    return null;
  }

  /// Parses GeoJSON polygon geometry dictionary to `List<LatLng>`.
  static List<LatLng> geoJsonToLatLngList(Map<String, dynamic>? geometry) {
    if (geometry == null || geometry['type'] != 'Polygon') return [];
    final coords = geometry['coordinates'] as List?;
    if (coords == null || coords.isEmpty) return [];

    final ring = coords[0] as List?;
    if (ring == null) return [];

    final result = <LatLng>[];
    for (final pt in ring) {
      if (pt is List && pt.length >= 2) {
        final lon = (pt[0] as num).toDouble();
        final lat = (pt[1] as num).toDouble();
        result.add(LatLng(lat, lon));
      }
    }

    // Drop trailing duplicate if closed
    if (result.length > 3 &&
        result.first.latitude == result.last.latitude &&
        result.first.longitude == result.last.longitude) {
      result.removeLast();
    }

    return result;
  }

  /// Serializes `List<LatLng>` to standard RFC 7946 GeoJSON Polygon.
  static Map<String, dynamic> latLngListToGeoJson(
    List<LatLng> points, {
    Map<String, dynamic>? properties,
  }) {
    if (points.isEmpty) return {};

    final ring = points.map((p) => [p.longitude, p.latitude]).toList();
    // Ensure linear ring is closed (first == last)
    if (ring.isNotEmpty &&
        (ring.first[0] != ring.last[0] || ring.first[1] != ring.last[1])) {
      ring.add(ring.first);
    }

    final data = <String, dynamic>{
      'type': 'Polygon',
      'coordinates': [ring],
    };
    if (properties != null && properties.isNotEmpty) {
      data['properties'] = properties;
    }
    return data;
  }
}

