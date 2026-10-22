// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'farm_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$FarmResponseCWProxy {
  FarmResponse id(int id);

  FarmResponse name(String? name);

  FarmResponse location(String? location);

  FarmResponse areaAcres(num? areaAcres);

  FarmResponse latitude(num? latitude);

  FarmResponse longitude(num? longitude);

  FarmResponse cropHistory(List<String> cropHistory);

  FarmResponse boundary(Map<String, Object>? boundary);

  FarmResponse plots(List<PlotResponse>? plots);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `FarmResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// FarmResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  FarmResponse call({
    int id,
    String? name,
    String? location,
    num? areaAcres,
    num? latitude,
    num? longitude,
    List<String> cropHistory,
    Map<String, Object>? boundary,
    List<PlotResponse>? plots,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfFarmResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfFarmResponse.copyWith.fieldName(...)`
class _$FarmResponseCWProxyImpl implements _$FarmResponseCWProxy {
  const _$FarmResponseCWProxyImpl(this._value);

  final FarmResponse _value;

  @override
  FarmResponse id(int id) => this(id: id);

  @override
  FarmResponse name(String? name) => this(name: name);

  @override
  FarmResponse location(String? location) => this(location: location);

  @override
  FarmResponse areaAcres(num? areaAcres) => this(areaAcres: areaAcres);

  @override
  FarmResponse latitude(num? latitude) => this(latitude: latitude);

  @override
  FarmResponse longitude(num? longitude) => this(longitude: longitude);

  @override
  FarmResponse cropHistory(List<String> cropHistory) =>
      this(cropHistory: cropHistory);

  @override
  FarmResponse boundary(Map<String, Object>? boundary) =>
      this(boundary: boundary);

  @override
  FarmResponse plots(List<PlotResponse>? plots) => this(plots: plots);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `FarmResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// FarmResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  FarmResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? location = const $CopyWithPlaceholder(),
    Object? areaAcres = const $CopyWithPlaceholder(),
    Object? latitude = const $CopyWithPlaceholder(),
    Object? longitude = const $CopyWithPlaceholder(),
    Object? cropHistory = const $CopyWithPlaceholder(),
    Object? boundary = const $CopyWithPlaceholder(),
    Object? plots = const $CopyWithPlaceholder(),
  }) {
    return FarmResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as int,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String?,
      location: location == const $CopyWithPlaceholder()
          ? _value.location
          // ignore: cast_nullable_to_non_nullable
          : location as String?,
      areaAcres: areaAcres == const $CopyWithPlaceholder()
          ? _value.areaAcres
          // ignore: cast_nullable_to_non_nullable
          : areaAcres as num?,
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
      boundary: boundary == const $CopyWithPlaceholder()
          ? _value.boundary
          // ignore: cast_nullable_to_non_nullable
          : boundary as Map<String, Object>?,
      plots: plots == const $CopyWithPlaceholder()
          ? _value.plots
          // ignore: cast_nullable_to_non_nullable
          : plots as List<PlotResponse>?,
    );
  }
}

extension $FarmResponseCopyWith on FarmResponse {
  /// Returns a callable class that can be used as follows: `instanceOfFarmResponse.copyWith(...)` or like so:`instanceOfFarmResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$FarmResponseCWProxy get copyWith => _$FarmResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

FarmResponse _$FarmResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'FarmResponse',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const [
            'id',
            'name',
            'location',
            'area_acres',
            'latitude',
            'longitude',
            'crop_history',
          ],
        );
        final val = FarmResponse(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          name: $checkedConvert('name', (v) => v as String?),
          location: $checkedConvert('location', (v) => v as String?),
          areaAcres: $checkedConvert('area_acres', (v) => v as num?),
          latitude: $checkedConvert('latitude', (v) => v as num?),
          longitude: $checkedConvert('longitude', (v) => v as num?),
          cropHistory: $checkedConvert(
            'crop_history',
            (v) => (v as List<dynamic>).map((e) => e as String).toList(),
          ),
          boundary: $checkedConvert(
            'boundary',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as Object),
            ),
          ),
          plots: $checkedConvert(
            'plots',
            (v) => (v as List<dynamic>?)
                ?.map((e) => PlotResponse.fromJson(e as Map<String, dynamic>))
                .toList(),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'areaAcres': 'area_acres',
        'cropHistory': 'crop_history',
      },
    );

Map<String, dynamic> _$FarmResponseToJson(FarmResponse instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'location': instance.location,
      'area_acres': instance.areaAcres,
      'latitude': instance.latitude,
      'longitude': instance.longitude,
      'crop_history': instance.cropHistory,
      'boundary': ?instance.boundary,
      'plots': ?instance.plots?.map((e) => e.toJson()).toList(),
    };
