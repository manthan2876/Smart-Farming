// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'plot_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PlotResponseCWProxy {
  PlotResponse id(int id);

  PlotResponse name(String name);

  PlotResponse crop(String? crop);

  PlotResponse areaAcres(num? areaAcres);

  PlotResponse status(String status);

  PlotResponse geometry(Map<String, Object>? geometry);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PlotResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PlotResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PlotResponse call({
    int id,
    String name,
    String? crop,
    num? areaAcres,
    String status,
    Map<String, Object>? geometry,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPlotResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPlotResponse.copyWith.fieldName(...)`
class _$PlotResponseCWProxyImpl implements _$PlotResponseCWProxy {
  const _$PlotResponseCWProxyImpl(this._value);

  final PlotResponse _value;

  @override
  PlotResponse id(int id) => this(id: id);

  @override
  PlotResponse name(String name) => this(name: name);

  @override
  PlotResponse crop(String? crop) => this(crop: crop);

  @override
  PlotResponse areaAcres(num? areaAcres) => this(areaAcres: areaAcres);

  @override
  PlotResponse status(String status) => this(status: status);

  @override
  PlotResponse geometry(Map<String, Object>? geometry) =>
      this(geometry: geometry);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PlotResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PlotResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PlotResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? name = const $CopyWithPlaceholder(),
    Object? crop = const $CopyWithPlaceholder(),
    Object? areaAcres = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
    Object? geometry = const $CopyWithPlaceholder(),
  }) {
    return PlotResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as int,
      name: name == const $CopyWithPlaceholder()
          ? _value.name
          // ignore: cast_nullable_to_non_nullable
          : name as String,
      crop: crop == const $CopyWithPlaceholder()
          ? _value.crop
          // ignore: cast_nullable_to_non_nullable
          : crop as String?,
      areaAcres: areaAcres == const $CopyWithPlaceholder()
          ? _value.areaAcres
          // ignore: cast_nullable_to_non_nullable
          : areaAcres as num?,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
      geometry: geometry == const $CopyWithPlaceholder()
          ? _value.geometry
          // ignore: cast_nullable_to_non_nullable
          : geometry as Map<String, Object>?,
    );
  }
}

extension $PlotResponseCopyWith on PlotResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPlotResponse.copyWith(...)` or like so:`instanceOfPlotResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PlotResponseCWProxy get copyWith => _$PlotResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PlotResponse _$PlotResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('PlotResponse', json, ($checkedConvert) {
      $checkKeys(
        json,
        requiredKeys: const ['id', 'name', 'crop', 'area_acres', 'status'],
      );
      final val = PlotResponse(
        id: $checkedConvert('id', (v) => (v as num).toInt()),
        name: $checkedConvert('name', (v) => v as String),
        crop: $checkedConvert('crop', (v) => v as String?),
        areaAcres: $checkedConvert('area_acres', (v) => v as num?),
        status: $checkedConvert('status', (v) => v as String),
        geometry: $checkedConvert(
          'geometry',
          (v) => (v as Map<String, dynamic>?)?.map(
            (k, e) => MapEntry(k, e as Object),
          ),
        ),
      );
      return val;
    }, fieldKeyMap: const {'areaAcres': 'area_acres'});

Map<String, dynamic> _$PlotResponseToJson(PlotResponse instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'crop': instance.crop,
      'area_acres': instance.areaAcres,
      'status': instance.status,
      'geometry': ?instance.geometry,
    };
