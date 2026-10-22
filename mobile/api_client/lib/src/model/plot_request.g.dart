// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'plot_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PlotRequestCWProxy {
  PlotRequest name(String name);

  PlotRequest crop(String? crop);

  PlotRequest areaAcres(num? areaAcres);

  PlotRequest geometry(Map<String, Object>? geometry);

  PlotRequest resetGeometry(bool? resetGeometry);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PlotRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PlotRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  PlotRequest call({
    String name,
    String? crop,
    num? areaAcres,
    Map<String, Object>? geometry,
    bool? resetGeometry,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPlotRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPlotRequest.copyWith.fieldName(...)`
class _$PlotRequestCWProxyImpl implements _$PlotRequestCWProxy {
  const _$PlotRequestCWProxyImpl(this._value);

  final PlotRequest _value;

  @override
  PlotRequest name(String name) => this(name: name);

  @override
  PlotRequest crop(String? crop) => this(crop: crop);

  @override
  PlotRequest areaAcres(num? areaAcres) => this(areaAcres: areaAcres);

  @override
  PlotRequest geometry(Map<String, Object>? geometry) =>
      this(geometry: geometry);

  @override
  PlotRequest resetGeometry(bool? resetGeometry) =>
      this(resetGeometry: resetGeometry);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PlotRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PlotRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  PlotRequest call({
    Object? name = const $CopyWithPlaceholder(),
    Object? crop = const $CopyWithPlaceholder(),
    Object? areaAcres = const $CopyWithPlaceholder(),
    Object? geometry = const $CopyWithPlaceholder(),
    Object? resetGeometry = const $CopyWithPlaceholder(),
  }) {
    return PlotRequest(
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
      geometry: geometry == const $CopyWithPlaceholder()
          ? _value.geometry
          // ignore: cast_nullable_to_non_nullable
          : geometry as Map<String, Object>?,
      resetGeometry: resetGeometry == const $CopyWithPlaceholder()
          ? _value.resetGeometry
          // ignore: cast_nullable_to_non_nullable
          : resetGeometry as bool?,
    );
  }
}

extension $PlotRequestCopyWith on PlotRequest {
  /// Returns a callable class that can be used as follows: `instanceOfPlotRequest.copyWith(...)` or like so:`instanceOfPlotRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PlotRequestCWProxy get copyWith => _$PlotRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PlotRequest _$PlotRequestFromJson(Map<String, dynamic> json) => $checkedCreate(
  'PlotRequest',
  json,
  ($checkedConvert) {
    $checkKeys(json, requiredKeys: const ['name']);
    final val = PlotRequest(
      name: $checkedConvert('name', (v) => v as String),
      crop: $checkedConvert('crop', (v) => v as String?),
      areaAcres: $checkedConvert('area_acres', (v) => v as num?),
      geometry: $checkedConvert(
        'geometry',
        (v) => (v as Map<String, dynamic>?)?.map(
          (k, e) => MapEntry(k, e as Object),
        ),
      ),
      resetGeometry: $checkedConvert(
        'reset_geometry',
        (v) => v as bool? ?? false,
      ),
    );
    return val;
  },
  fieldKeyMap: const {
    'areaAcres': 'area_acres',
    'resetGeometry': 'reset_geometry',
  },
);

Map<String, dynamic> _$PlotRequestToJson(PlotRequest instance) =>
    <String, dynamic>{
      'name': instance.name,
      'crop': ?instance.crop,
      'area_acres': ?instance.areaAcres,
      'geometry': ?instance.geometry,
      'reset_geometry': ?instance.resetGeometry,
    };
