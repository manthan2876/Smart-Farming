//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'profile_update_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ProfileUpdateRequest {
  /// Returns a new [ProfileUpdateRequest] instance.
  ProfileUpdateRequest({
    this.name,

    this.phone,

    this.location,

    this.latitude,

    this.longitude,

    this.language,

    this.cropHistory,

    this.farmName,

    this.farmAreaAcres,
  });

  @JsonKey(name: r'name', required: false, includeIfNull: false)
  final String? name;

  @JsonKey(name: r'phone', required: false, includeIfNull: false)
  final String? phone;

  @JsonKey(name: r'location', required: false, includeIfNull: false)
  final String? location;

  // minimum: -90.0
  // maximum: 90.0
  @JsonKey(name: r'latitude', required: false, includeIfNull: false)
  final num? latitude;

  // minimum: -180.0
  // maximum: 180.0
  @JsonKey(name: r'longitude', required: false, includeIfNull: false)
  final num? longitude;

  @JsonKey(name: r'language', required: false, includeIfNull: false)
  final String? language;

  @JsonKey(name: r'crop_history', required: false, includeIfNull: false)
  final List<String>? cropHistory;

  @JsonKey(name: r'farm_name', required: false, includeIfNull: false)
  final String? farmName;

  // minimum: 0.0
  // maximum: 1000000.0
  @JsonKey(name: r'farm_area_acres', required: false, includeIfNull: false)
  final num? farmAreaAcres;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ProfileUpdateRequest &&
          other.name == name &&
          other.phone == phone &&
          other.location == location &&
          other.latitude == latitude &&
          other.longitude == longitude &&
          other.language == language &&
          other.cropHistory == cropHistory &&
          other.farmName == farmName &&
          other.farmAreaAcres == farmAreaAcres;

  @override
  int get hashCode =>
      (name == null ? 0 : name.hashCode) +
      (phone == null ? 0 : phone.hashCode) +
      (location == null ? 0 : location.hashCode) +
      (latitude == null ? 0 : latitude.hashCode) +
      (longitude == null ? 0 : longitude.hashCode) +
      (language == null ? 0 : language.hashCode) +
      (cropHistory == null ? 0 : cropHistory.hashCode) +
      (farmName == null ? 0 : farmName.hashCode) +
      (farmAreaAcres == null ? 0 : farmAreaAcres.hashCode);

  factory ProfileUpdateRequest.fromJson(Map<String, dynamic> json) =>
      _$ProfileUpdateRequestFromJson(json);

  Map<String, dynamic> toJson() => _$ProfileUpdateRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
