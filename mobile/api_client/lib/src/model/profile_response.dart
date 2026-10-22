//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'profile_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ProfileResponse {
  /// Returns a new [ProfileResponse] instance.
  ProfileResponse({
    required this.id,

    required this.name,

    required this.phone,

    required this.email,

    this.isEmailVerified = false,

    this.pendingEmail,

    required this.language,

    required this.role,

    required this.location,

    required this.latitude,

    required this.longitude,

    required this.cropHistory,

    this.farmName,

    this.farmAreaAcres,
  });

  @JsonKey(name: r'id', required: true, includeIfNull: false)
  final String id;

  @JsonKey(name: r'name', required: true, includeIfNull: true)
  final String? name;

  @JsonKey(name: r'phone', required: true, includeIfNull: true)
  final String? phone;

  @JsonKey(name: r'email', required: true, includeIfNull: true)
  final String? email;

  @JsonKey(
    defaultValue: false,
    name: r'is_email_verified',
    required: false,
    includeIfNull: false,
  )
  final bool? isEmailVerified;

  @JsonKey(name: r'pending_email', required: false, includeIfNull: false)
  final String? pendingEmail;

  @JsonKey(name: r'language', required: true, includeIfNull: false)
  final String language;

  @JsonKey(name: r'role', required: true, includeIfNull: false)
  final String role;

  @JsonKey(name: r'location', required: true, includeIfNull: true)
  final String? location;

  @JsonKey(name: r'latitude', required: true, includeIfNull: true)
  final num? latitude;

  @JsonKey(name: r'longitude', required: true, includeIfNull: true)
  final num? longitude;

  @JsonKey(name: r'crop_history', required: true, includeIfNull: false)
  final List<String> cropHistory;

  @JsonKey(name: r'farm_name', required: false, includeIfNull: false)
  final String? farmName;

  @JsonKey(name: r'farm_area_acres', required: false, includeIfNull: false)
  final num? farmAreaAcres;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ProfileResponse &&
          other.id == id &&
          other.name == name &&
          other.phone == phone &&
          other.email == email &&
          other.isEmailVerified == isEmailVerified &&
          other.pendingEmail == pendingEmail &&
          other.language == language &&
          other.role == role &&
          other.location == location &&
          other.latitude == latitude &&
          other.longitude == longitude &&
          other.cropHistory == cropHistory &&
          other.farmName == farmName &&
          other.farmAreaAcres == farmAreaAcres;

  @override
  int get hashCode =>
      id.hashCode +
      (name == null ? 0 : name.hashCode) +
      (phone == null ? 0 : phone.hashCode) +
      (email == null ? 0 : email.hashCode) +
      isEmailVerified.hashCode +
      (pendingEmail == null ? 0 : pendingEmail.hashCode) +
      language.hashCode +
      role.hashCode +
      (location == null ? 0 : location.hashCode) +
      (latitude == null ? 0 : latitude.hashCode) +
      (longitude == null ? 0 : longitude.hashCode) +
      cropHistory.hashCode +
      (farmName == null ? 0 : farmName.hashCode) +
      (farmAreaAcres == null ? 0 : farmAreaAcres.hashCode);

  factory ProfileResponse.fromJson(Map<String, dynamic> json) =>
      _$ProfileResponseFromJson(json);

  Map<String, dynamic> toJson() => _$ProfileResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
