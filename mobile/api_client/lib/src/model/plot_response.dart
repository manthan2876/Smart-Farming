//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'plot_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PlotResponse {
  /// Returns a new [PlotResponse] instance.
  PlotResponse({
    required this.id,

    required this.name,

    required this.crop,

    required this.areaAcres,

    required this.status,

    this.geometry,
  });

  @JsonKey(name: r'id', required: true, includeIfNull: false)
  final int id;

  @JsonKey(name: r'name', required: true, includeIfNull: false)
  final String name;

  @JsonKey(name: r'crop', required: true, includeIfNull: true)
  final String? crop;

  @JsonKey(name: r'area_acres', required: true, includeIfNull: true)
  final num? areaAcres;

  @JsonKey(name: r'status', required: true, includeIfNull: false)
  final String status;

  @JsonKey(name: r'geometry', required: false, includeIfNull: false)
  final Map<String, Object>? geometry;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PlotResponse &&
          other.id == id &&
          other.name == name &&
          other.crop == crop &&
          other.areaAcres == areaAcres &&
          other.status == status &&
          other.geometry == geometry;

  @override
  int get hashCode =>
      id.hashCode +
      name.hashCode +
      (crop == null ? 0 : crop.hashCode) +
      (areaAcres == null ? 0 : areaAcres.hashCode) +
      status.hashCode +
      (geometry == null ? 0 : geometry.hashCode);

  factory PlotResponse.fromJson(Map<String, dynamic> json) =>
      _$PlotResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PlotResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
