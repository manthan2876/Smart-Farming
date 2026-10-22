//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'plot_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PlotRequest {
  /// Returns a new [PlotRequest] instance.
  PlotRequest({
    required this.name,

    this.crop,

    this.areaAcres,

    this.geometry,

    this.resetGeometry = false,
  });

  @JsonKey(name: r'name', required: true, includeIfNull: false)
  final String name;

  @JsonKey(name: r'crop', required: false, includeIfNull: false)
  final String? crop;

  // minimum: 0.0
  @JsonKey(name: r'area_acres', required: false, includeIfNull: false)
  final num? areaAcres;

  @JsonKey(name: r'geometry', required: false, includeIfNull: false)
  final Map<String, Object>? geometry;

  @JsonKey(
    defaultValue: false,
    name: r'reset_geometry',
    required: false,
    includeIfNull: false,
  )
  final bool? resetGeometry;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PlotRequest &&
          other.name == name &&
          other.crop == crop &&
          other.areaAcres == areaAcres &&
          other.geometry == geometry &&
          other.resetGeometry == resetGeometry;

  @override
  int get hashCode =>
      name.hashCode +
      (crop == null ? 0 : crop.hashCode) +
      (areaAcres == null ? 0 : areaAcres.hashCode) +
      (geometry == null ? 0 : geometry.hashCode) +
      resetGeometry.hashCode;

  factory PlotRequest.fromJson(Map<String, dynamic> json) =>
      _$PlotRequestFromJson(json);

  Map<String, dynamic> toJson() => _$PlotRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
