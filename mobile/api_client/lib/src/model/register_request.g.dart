// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'register_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$RegisterRequestCWProxy {
  RegisterRequest name(String name);

  RegisterRequest password(String password);

  RegisterRequest phone(String? phone);

  RegisterRequest email(String? email);

  RegisterRequest location(String? location);

  RegisterRequest latitude(num? latitude);

  RegisterRequest longitude(num? longitude);

  RegisterRequest language(String? language);

  RegisterRequest cropHistory(List<String>? cropHistory);

  RegisterRequest farmName(String? farmName);

  RegisterRequest farmAreaAcres(num? farmAreaAcres);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `RegisterRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// RegisterRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  RegisterRequest call({
    String name,
    String password,
    String? phone,
    String? email,
    String? location,
    num? latitude,
    num? longitude,
    String? language,
    List<String>? cropHistory,
    String? farmName,
    num? farmAreaAcres,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfRegisterRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfRegisterRequest.copyWith.fieldName(...)`
class _$RegisterRequestCWProxyImpl implements _$RegisterRequestCWProxy {
  const _$RegisterRequestCWProxyImpl(this._value);

  final RegisterRequest _value;

  @override
  RegisterRequest name(String name) => this(name: name);

  @override
  RegisterRequest password(String password) => this(password: password);

  @override
  RegisterRequest phone(String? phone) => this(phone: phone);

  @override
  RegisterRequest email(String? email) => this(email: email);

  @override
  RegisterRequest location(String? location) => this(location: location);

  @override
  RegisterRequest latitude(num? latitude) => this(latitude: latitude);

  @override
  RegisterRequest longitude(num? longitude) => this(longitude: longitude);

  @override
  RegisterRequest language(String? language) => this(language: language);

  @override
  RegisterRequest cropHistory(List<String>? cropHistory) =>
      this(cropHistory: cropHistory);

  @override
  RegisterRequest farmName(String? farmName) => this(farmName: farmName);

  @override
  RegisterRequest farmAreaAcres(num? farmAreaAcres) =>
      this(farmAreaAcres: farmAreaAcres);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `RegisterRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// RegisterRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  RegisterRequest call({
    Object? name = const $CopyWithPlaceholder(),
    Object? password = const $CopyWithPlaceholder(),
    Object? phone = const $CopyWithPlaceholder(),
    Object? email = const $CopyWithPlaceholder(),
    Object? location = const $CopyWithPlaceholder(),
    Object? latitude = const $CopyWithPlaceholder(),
    Object? longitude = const $CopyWithPlaceholder(),
    Object? language = const $CopyWithPlaceholder(),
    Object? cropHistory = const $CopyWithPlaceholder(),
    Object? farmName = const $CopyWithPlaceholder(),
    Object? farmAreaAcres = const $CopyWithPlaceholder(),
  }) {
    return RegisterRequest(
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      password: password == const $CopyWithPlaceholder()
          ? _value.password
          // ignore: cast_nullable_to_non_nullable
          : password as String,
      phone: phone == const $CopyWithPlaceholder()
          ? _value.phone
          // ignore: cast_nullable_to_non_nullable
          : phone as String?,
      email: email == const $CopyWithPlaceholder()
          ? _value.email
          // ignore: cast_nullable_to_non_nullable
          : email as String?,
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

extension $RegisterRequestCopyWith on RegisterRequest {
  /// Returns a callable class that can be used as follows: `instanceOfRegisterRequest.copyWith(...)` or like so:`instanceOfRegisterRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$RegisterRequestCWProxy get copyWith => _$RegisterRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

RegisterRequest _$RegisterRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'RegisterRequest',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['name', 'password']);
        final val = RegisterRequest(
          name: $checkedConvert('name', (v) => v as String),
          password: $checkedConvert('password', (v) => v as String),
          phone: $checkedConvert('phone', (v) => v as String?),
          email: $checkedConvert('email', (v) => v as String?),
          location: $checkedConvert('location', (v) => v as String?),
          latitude: $checkedConvert('latitude', (v) => v as num?),
          longitude: $checkedConvert('longitude', (v) => v as num?),
          language: $checkedConvert(
            'language',
            (v) => v as String? ?? 'English',
          ),
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

Map<String, dynamic> _$RegisterRequestToJson(RegisterRequest instance) =>
    <String, dynamic>{
      'name': instance.name,
      'password': instance.password,
      'phone': ?instance.phone,
      'email': ?instance.email,
      'location': ?instance.location,
      'latitude': ?instance.latitude,
      'longitude': ?instance.longitude,
      'language': ?instance.language,
      'crop_history': ?instance.cropHistory,
      'farm_name': ?instance.farmName,
      'farm_area_acres': ?instance.farmAreaAcres,
    };
