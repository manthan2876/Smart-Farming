// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'farm_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$FarmRequestCWProxy {
  FarmRequest name(String name);

  FarmRequest location(String location);

  FarmRequest areaAcres(num areaAcres);

  FarmRequest latitude(num? latitude);

  FarmRequest longitude(num? longitude);

  FarmRequest cropHistory(List<String>? cropHistory);

  FarmRequest boundary(Map<String, Object>? boundary);

  FarmRequest resetBoundary(bool? resetBoundary);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `FarmRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// FarmRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  FarmRequest call({
    String name,
    String location,
    num areaAcres,
    num? latitude,
    num? longitude,
    List<String>? cropHistory,
    Map<String, Object>? boundary,
    bool? resetBoundary,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfFarmRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfFarmRequest.copyWith.fieldName(...)`
class _$FarmRequestCWProxyImpl implements _$FarmRequestCWProxy {
  const _$FarmRequestCWProxyImpl(this._value);

  final FarmRequest _value;

  @override
  FarmRequest name(String name) => this(name: name);

  @override
  FarmRequest location(String location) => this(location: location);

  @override
  FarmRequest areaAcres(num areaAcres) => this(areaAcres: areaAcres);

  @override
  FarmRequest latitude(num? latitude) => this(latitude: latitude);

  @override
  FarmRequest longitude(num? longitude) => this(longitude: longitude);

  @override
  FarmRequest cropHistory(List<String>? cropHistory) =>
      this(cropHistory: cropHistory);

  @override
  FarmRequest boundary(Map<String, Object>? boundary) =>
      this(boundary: boundary);

  @override
  FarmRequest resetBoundary(bool? resetBoundary) =>
      this(resetBoundary: resetBoundary);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `FarmRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// FarmRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  FarmRequest call({
    Object? name = const $CopyWithPlaceholder(),
    Object? location = const $CopyWithPlaceholder(),
    Object? areaAcres = const $CopyWithPlaceholder(),
    Object? latitude = const $CopyWithPlaceholder(),
    Object? longitude = const $CopyWithPlaceholder(),
    Object? cropHistory = const $CopyWithPlaceholder(),
    Object? boundary = const $CopyWithPlaceholder(),
    Object? resetBoundary = const $CopyWithPlaceholder(),
  }) {
    return FarmRequest(
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      location: location == const $CopyWithPlaceholder()
          ? _value.location
          // ignore: cast_nullable_to_non_nullable
          : location as String,
      areaAcres: areaAcres == const $CopyWithPlaceholder()
          ? _value.areaAcres
          // ignore: cast_nullable_to_non_nullable
          : areaAcres as num,
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
          : cropHistory as List<String>?,
      boundary: boundary == const $CopyWithPlaceholder()
          ? _value.boundary
          // ignore: cast_nullable_to_non_nullable
          : boundary as Map<String, Object>?,
      resetBoundary: resetBoundary == const $CopyWithPlaceholder()
          ? _value.resetBoundary
          // ignore: cast_nullable_to_non_nullable
          : resetBoundary as bool?,
    );
  }
}

extension $FarmRequestCopyWith on FarmRequest {
  /// Returns a callable class that can be used as follows: `instanceOfFarmRequest.copyWith(...)` or like so:`instanceOfFarmRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$FarmRequestCWProxy get copyWith => _$FarmRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

FarmRequest _$FarmRequestFromJson(Map<String, dynamic> json) => $checkedCreate(
  'FarmRequest',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['name', 'location', 'area_acres']);
    final val = FarmRequest(
      name: $checkedConvert('name', (v) => v as String),
      location: $checkedConvert('location', (v) => v as String),
      areaAcres: $checkedConvert('area_acres', (v) => v as num),
      latitude: $checkedConvert('latitude', (v) => v as num?),
      longitude: $checkedConvert('longitude', (v) => v as num?),
      cropHistory: $checkedConvert(
        'crop_history',
        (v) => (v as List<dynamic>?)?.map((e) => e as String).toList(),
      ),
      boundary: $checkedConvert(
        'boundary',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      resetBoundary: $checkedConvert(
        'reset_boundary',
        (v) => v as bool? ?? false,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'areaAcres': 'area_acres',
    'cropHistory': 'crop_history',
    'resetBoundary': 'reset_boundary',
  },
);

Map<String, dynamic> _$FarmRequestToJson(FarmRequest instance) =>
    <String, dynamic>{
      'name': instance.name,
      'location': instance.location,
      'area_acres': instance.areaAcres,
      'latitude': ?instance.latitude,
      'longitude': ?instance.longitude,
      'crop_history': ?instance.cropHistory,
      'boundary': ?instance.boundary,
      'reset_boundary': ?instance.resetBoundary,
    };
