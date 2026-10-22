// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'profile_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ProfileResponseCWProxy {
  ProfileResponse id(String id);

  ProfileResponse name(String? name);

  ProfileResponse phone(String? phone);

  ProfileResponse email(String? email);

  ProfileResponse isEmailVerified(bool? isEmailVerified);

  ProfileResponse pendingEmail(String? pendingEmail);

  ProfileResponse language(String language);

  ProfileResponse role(String role);

  ProfileResponse location(String? location);

  ProfileResponse latitude(num? latitude);

  ProfileResponse longitude(num? longitude);

  ProfileResponse cropHistory(List<String> cropHistory);

  ProfileResponse farmName(String? farmName);

  ProfileResponse farmAreaAcres(num? farmAreaAcres);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ProfileResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ProfileResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ProfileResponse call({
    String id,
    String? name,
    String? phone,
    String? email,
    bool? isEmailVerified,
    String? pendingEmail,
    String language,
    String role,
    String? location,
    num? latitude,
    num? longitude,
    List<String> cropHistory,
    String? farmName,
    num? farmAreaAcres,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfProfileResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfProfileResponse.copyWith.fieldName(...)`
class _$ProfileResponseCWProxyImpl implements _$ProfileResponseCWProxy {
  const _$ProfileResponseCWProxyImpl(this._value);

  final ProfileResponse _value;

  @override
  ProfileResponse id(String id) => this(id: id);

  @override
  ProfileResponse name(String? name) => this(name: name);

  @override
  ProfileResponse phone(String? phone) => this(phone: phone);

  @override
  ProfileResponse email(String? email) => this(email: email);

  @override
  ProfileResponse isEmailVerified(bool? isEmailVerified) =>
      this(isEmailVerified: isEmailVerified);

  @override
  ProfileResponse pendingEmail(String? pendingEmail) =>
      this(pendingEmail: pendingEmail);

  @override
  ProfileResponse language(String language) => this(language: language);

  @override
  ProfileResponse role(String role) => this(role: role);

  @override
  ProfileResponse location(String? location) => this(location: location);

  @override
  ProfileResponse latitude(num? latitude) => this(latitude: latitude);

  @override
  ProfileResponse longitude(num? longitude) => this(longitude: longitude);

  @override
  ProfileResponse cropHistory(List<String> cropHistory) =>
      this(cropHistory: cropHistory);

  @override
  ProfileResponse farmName(String? farmName) => this(farmName: farmName);

  @override
  ProfileResponse farmAreaAcres(num? farmAreaAcres) =>
      this(farmAreaAcres: farmAreaAcres);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ProfileResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ProfileResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ProfileResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? phone = const $CopyWithPlaceholder(),
    Object? email = const $CopyWithPlaceholder(),
    Object? isEmailVerified = const $CopyWithPlaceholder(),
    Object? pendingEmail = const $CopyWithPlaceholder(),
    Object? language = const $CopyWithPlaceholder(),
    Object? role = const $CopyWithPlaceholder(),
    Object? location = const $CopyWithPlaceholder(),
    Object? latitude = const $CopyWithPlaceholder(),
    Object? longitude = const $CopyWithPlaceholder(),
    Object? cropHistory = const $CopyWithPlaceholder(),
    Object? farmName = const $CopyWithPlaceholder(),
    Object? farmAreaAcres = const $CopyWithPlaceholder(),
  }) {
    return ProfileResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as String,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String?,
      phone: phone == const $CopyWithPlaceholder()
          ? _value.phone
          // ignore: cast_nullable_to_non_nullable
          : phone as String?,
      email: email == const $CopyWithPlaceholder()
          ? _value.email
          // ignore: cast_nullable_to_non_nullable
          : email as String?,
      isEmailVerified: isEmailVerified == const $CopyWithPlaceholder()
          ? _value.isEmailVerified
          // ignore: cast_nullable_to_non_nullable
          : isEmailVerified as bool?,
      pendingEmail: pendingEmail == const $CopyWithPlaceholder()
          ? _value.pendingEmail
          // ignore: cast_nullable_to_non_nullable
          : pendingEmail as String?,
      language: language == const $CopyWithPlaceholder()
          ? _value.language
          // ignore: cast_nullable_to_non_nullable
          : language as String,
      role: role == const $CopyWithPlaceholder()
          ? _value.role
          // ignore: cast_nullable_to_non_nullable
          : role as String,
      location: location == const $CopyWithPlaceholder()
          ? _value.location
          // ignore: cast_nullable_to_non_nullable
          : location as String?,
      latitude: latitude == const $CopyWithPlaceholder()
          ? _value.latitude
          // ignore: cast_nullable_to_non_nullable
          : latitude as num?,
      longitude: longitude == const $CopyWithPlaceholder()
          ? _value.longitude
          // ignore: cast_nullable_to_non_nullable
          : longitude as num?,
      cropHistory: cropHistory == const $CopyWithPlaceholder()
          ? _value.cropHistory
          // ignore: cast_nullable_to_non_nullable
          : cropHistory as List<String>,
      farmName: farmName == const $CopyWithPlaceholder()
          ? _value.farmName
          // ignore: cast_nullable_to_non_nullable
          : farmName as String?,
      farmAreaAcres: farmAreaAcres == const $CopyWithPlaceholder()
          ? _value.farmAreaAcres
          // ignore: cast_nullable_to_non_nullable
          : farmAreaAcres as num?,
    );
  }
}

extension $ProfileResponseCopyWith on ProfileResponse {
  /// Returns a callable class that can be used as follows: `instanceOfProfileResponse.copyWith(...)` or like so:`instanceOfProfileResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ProfileResponseCWProxy get copyWith => _$ProfileResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ProfileResponse _$ProfileResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'ProfileResponse',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const [
            'id',
            'name',
            'phone',
            'email',
            'language',
            'role',
            'location',
            'latitude',
            'longitude',
            'crop_history',
          ],
        );
        final val = ProfileResponse(
          id: $checkedConvert('id', (v) => v as String),
          name: $checkedConvert('name', (v) => v as String?),
          phone: $checkedConvert('phone', (v) => v as String?),
          email: $checkedConvert('email', (v) => v as String?),
          isEmailVerified: $checkedConvert(
            'is_email_verified',
            (v) => v as bool? ?? false,
          ),
          pendingEmail: $checkedConvert('pending_email', (v) => v as String?),
          language: $checkedConvert('language', (v) => v as String),
          role: $checkedConvert('role', (v) => v as String),
          location: $checkedConvert('location', (v) => v as String?),
          latitude: $checkedConvert('latitude', (v) => v as num?),
          longitude: $checkedConvert('longitude', (v) => v as num?),
          cropHistory: $checkedConvert(
            'crop_history',
            (v) => (v as List<dynamic>).map((e) => e as String).toList(),
          ),
          farmName: $checkedConvert('farm_name', (v) => v as String?),
          farmAreaAcres: $checkedConvert('farm_area_acres', (v) => v as num?),
        );
        return val;
      },
      fieldKeyMap: const {
        'isEmailVerified': 'is_email_verified',
        'pendingEmail': 'pending_email',
        'cropHistory': 'crop_history',
        'farmName': 'farm_name',
        'farmAreaAcres': 'farm_area_acres',
      },
    );

Map<String, dynamic> _$ProfileResponseToJson(ProfileResponse instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'phone': instance.phone,
      'email': instance.email,
      'is_email_verified': ?instance.isEmailVerified,
      'pending_email': ?instance.pendingEmail,
      'language': instance.language,
      'role': instance.role,
      'location': instance.location,
      'latitude': instance.latitude,
      'longitude': instance.longitude,
      'crop_history': instance.cropHistory,
      'farm_name': ?instance.farmName,
      'farm_area_acres': ?instance.farmAreaAcres,
    };
