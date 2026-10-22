// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'crop_list_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$CropListResponseCWProxy {
  CropListResponse crops(List<String> crops);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CropListResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CropListResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  CropListResponse call({List<String> crops});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfCropListResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfCropListResponse.copyWith.fieldName(...)`
class _$CropListResponseCWProxyImpl implements _$CropListResponseCWProxy {
  const _$CropListResponseCWProxyImpl(this._value);

  final CropListResponse _value;

  @override
  CropListResponse crops(List<String> crops) => this(crops: crops);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `CropListResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// CropListResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  CropListResponse call({Object? crops = const $CopyWithPlaceholder()}) {
    return CropListResponse(
      crops: crops == const $CopyWithPlaceholder()
          ? _value.crops
          // ignore: cast_nullable_to_non_nullable
          : crops as List<String>,
    );
  }
}

extension $CropListResponseCopyWith on CropListResponse {
  /// Returns a callable class that can be used as follows: `instanceOfCropListResponse.copyWith(...)` or like so:`instanceOfCropListResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$CropListResponseCWProxy get copyWith => _$CropListResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

CropListResponse _$CropListResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('CropListResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['crops']);
      final val = CropListResponse(
        crops: $checkedConvert(
          'crops',
          (v) => (v as List<dynamic>).map((e) => e as String).toList(),
        ),
      );
      return val;
    });

Map<String, dynamic> _$CropListResponseToJson(CropListResponse instance) =>
    <String, dynamic>{'crops': instance.crops};
