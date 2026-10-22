//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'farm_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class FarmRequest {
  /// Returns a new [FarmRequest] instance.
  FarmRequest({
    required this.name,

    required this.location,

    required this.areaAcres,

    this.latitude,

    this.longitude,

    this.cropHistory,

    this.boundary,

    this.resetBoundary = false,
  });

  @JsonKey(name: r'name', required: true, includeIfNull: false)
  final String name;

  @JsonKey(name: r'location', required: true, includeIfNull: false)
  final String location;

  // minimum: 0.0
  // maximum: 1000000.0
  @JsonKey(name: r'area_acres', required: true, includeIfNull: false)
  final num areaAcres;

  // minimum: -90.0
  // maximum: 90.0
  @JsonKey(name: r'latitude', required: false, includeIfNull: false)
  final num? latitude;

  // minimum: -180.0
  // maximum: 180.0
  @JsonKey(name: r'longitude', required: false, includeIfNull: false)
  final num? longitude;

  @JsonKey(name: r'crop_history', required: false, includeIfNull: false)
  final List<String>? cropHistory;

  @JsonKey(name: r'boundary', required: false, includeIfNull: false)
  final Map<String, Object>? boundary;

  @JsonKey(
    defaultValue: false,
    name: r'reset_boundary',
    required: false,
    includeIfNull: false,
  )
  final bool? resetBoundary;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FarmRequest &&
          other.name == name &&
          other.location == location &&
          other.areaAcres == areaAcres &&
          other.latitude == latitude &&
          other.longitude == longitude &&
          other.cropHistory == cropHistory &&
          other.boundary == boundary &&
          other.resetBoundary == resetBoundary;

  @override
  int get hashCode =>
      name.hashCode +
      location.hashCode +
      areaAcres.hashCode +
      (latitude == null ? 0 : latitude.hashCode) +
      (longitude == null ? 0 : longitude.hashCode) +
      cropHistory.hashCode +
      (boundary == null ? 0 : boundary.hashCode) +
      resetBoundary.hashCode;

  factory FarmRequest.fromJson(Map<String, dynamic> json) =>
      _$FarmRequestFromJson(json);

  Map<String, dynamic> toJson() => _$FarmRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
