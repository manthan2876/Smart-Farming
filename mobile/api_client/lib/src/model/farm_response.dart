//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:smart_farming_api/src/model/plot_response.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'farm_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class FarmResponse {
  /// Returns a new [FarmResponse] instance.
  FarmResponse({
    required this.id,

    required this.name,

    required this.location,

    required this.areaAcres,

    required this.latitude,

    required this.longitude,

    required this.cropHistory,

    this.boundary,

    this.plots,
  });

  @JsonKey(name: r'id', required: true, includeIfNull: false)
  final int id;

  @JsonKey(name: r'name', required: true, includeIfNull: true)
  final String? name;

  @JsonKey(name: r'location', required: true, includeIfNull: true)
  final String? location;

  @JsonKey(name: r'area_acres', required: true, includeIfNull: true)
  final num? areaAcres;

  @JsonKey(name: r'latitude', required: true, includeIfNull: true)
  final num? latitude;

  @JsonKey(name: r'longitude', required: true, includeIfNull: true)
  final num? longitude;

  @JsonKey(name: r'crop_history', required: true, includeIfNull: false)
  final List<String> cropHistory;

  @JsonKey(name: r'boundary', required: false, includeIfNull: false)
  final Map<String, Object>? boundary;

  @JsonKey(name: r'plots', required: false, includeIfNull: false)
  final List<PlotResponse>? plots;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FarmResponse &&
          other.id == id &&
          other.name == name &&
          other.location == location &&
          other.areaAcres == areaAcres &&
          other.latitude == latitude &&
          other.longitude == longitude &&
          other.cropHistory == cropHistory &&
          other.boundary == boundary &&
          other.plots == plots;

  @override
  int get hashCode =>
      id.hashCode +
      (name == null ? 0 : name.hashCode) +
      (location == null ? 0 : location.hashCode) +
      (areaAcres == null ? 0 : areaAcres.hashCode) +
      (latitude == null ? 0 : latitude.hashCode) +
      (longitude == null ? 0 : longitude.hashCode) +
      cropHistory.hashCode +
      (boundary == null ? 0 : boundary.hashCode) +
      plots.hashCode;

  factory FarmResponse.fromJson(Map<String, dynamic> json) =>
      _$FarmResponseFromJson(json);

  Map<String, dynamic> toJson() => _$FarmResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
