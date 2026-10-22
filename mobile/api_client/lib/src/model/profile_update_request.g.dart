// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'profile_update_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ProfileUpdateRequestCWProxy {
  ProfileUpdateRequest name(String? name);

  ProfileUpdateRequest phone(String? phone);

  ProfileUpdateRequest location(String? location);

  ProfileUpdateRequest latitude(num? latitude);

  ProfileUpdateRequest longitude(num? longitude);

  ProfileUpdateRequest language(String? language);

  ProfileUpdateRequest cropHistory(List<String>? cropHistory);

  ProfileUpdateRequest farmName(String? farmName);

  ProfileUpdateRequest farmAreaAcres(num? farmAreaAcres);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ProfileUpdateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ProfileUpdateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  ProfileUpdateRequest call({
    String? name,
    String? phone,
    String? location,
    num? latitude,
    num? longitude,
    String? language,
    List<String>? cropHistory,
    String? farmName,
    num? farmAreaAcres,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfProfileUpdateRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfProfileUpdateRequest.copyWith.fieldName(...)`
class _$ProfileUpdateRequestCWProxyImpl
    implements _$ProfileUpdateRequestCWProxy {
  const _$ProfileUpdateRequestCWProxyImpl(this._value);

  final ProfileUpdateRequest _value;

  @override
  ProfileUpdateRequest name(String? name) => this(name: name);

  @override
  ProfileUpdateRequest phone(String? phone) => this(phone: phone);

  @override
  ProfileUpdateRequest location(String? location) => this(location: location);

  @override
  ProfileUpdateRequest latitude(num? latitude) => this(latitude: latitude);

  @override
  ProfileUpdateRequest longitude(num? longitude) => this(longitude: longitude);

  @override
  ProfileUpdateRequest language(String? language) => this(language: language);

  @override
  ProfileUpdateRequest cropHistory(List<String>? cropHistory) =>
      this(cropHistory: cropHistory);

  @override
  ProfileUpdateRequest farmName(String? farmName) => this(farmName: farmName);

  @override
  ProfileUpdateRequest farmAreaAcres(num? farmAreaAcres) =>
      this(farmAreaAcres: farmAreaAcres);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ProfileUpdateRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ProfileUpdateRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  ProfileUpdateRequest call({
    Object? name = const $CopyWithPlaceholder(),
    Object? phone = const $CopyWithPlaceholder(),
    Object? location = const $CopyWithPlaceholder(),
    Object? latitude = const $CopyWithPlaceholder(),
    Object? longitude = const $CopyWithPlaceholder(),
    Object? language = const $CopyWithPlaceholder(),
    Object? cropHistory = const $CopyWithPlaceholder(),
    Object? farmName = const $CopyWithPlaceholder(),
    Object? farmAreaAcres = const $CopyWithPlaceholder(),
  }) {
    return ProfileUpdateRequest(
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String?,
      phone: phone == const $CopyWithPlaceholder()
          ? _value.phone
          // ignore: cast_nullable_to_non_nullable
          : phone as String?,
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
      language: language == const $CopyWithPlaceholder()
          ? _value.language
          // ignore: cast_nullable_to_non_nullable
          : language as String?,
      cropHistory: cropHistory == const $CopyWithPlaceholder()
          ? _value.cropHistory
          // ignore: cast_nullable_to_non_nullable
          : cropHistory as List<String>?,
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

extension $ProfileUpdateRequestCopyWith on ProfileUpdateRequest {
  /// Returns a callable class that can be used as follows: `instanceOfProfileUpdateRequest.copyWith(...)` or like so:`instanceOfProfileUpdateRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ProfileUpdateRequestCWProxy get copyWith =>
      _$ProfileUpdateRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ProfileUpdateRequest _$ProfileUpdateRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'ProfileUpdateRequest',
  json,
  ($checkedConvert) {
    final val = ProfileUpdateRequest(
      name: $checkedConvert('name', (v) => v as String?),
      phone: $checkedConvert('phone', (v) => v as String?),
      location: $checkedConvert('location', (v) => v as String?),
      latitude: $checkedConvert('latitude', (v) => v as num?),
      longitude: $checkedConvert('longitude', (v) => v as num?),
      language: $checkedConvert('language', (v) => v as String?),
      cropHistory: $checkedConvert(
        'crop_history',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
      ),
      farmName: $checkedConvert('farm_name', (v) => v as String?),
      farmAreaAcres: $checkedConvert('farm_area_acres', (v) => v as num?),
    );
    return val;
  },
  fieldKeyMap: const {
    'cropHistory': 'crop_history',
    'farmName': 'farm_name',
    'farmAreaAcres': 'farm_area_acres',
  },
);

Map<String, dynamic> _$ProfileUpdateRequestToJson(
  ProfileUpdateRequest instance,
) => <String, dynamic>{
  'name': ?instance.name,
  'phone': ?instance.phone,
  'location': ?instance.location,
  'latitude': ?instance.latitude,
  'longitude': ?instance.longitude,
  'language': ?instance.language,
  'crop_history': ?instance.cropHistory,
  'farm_name': ?instance.farmName,
  'farm_area_acres': ?instance.farmAreaAcres,
};
