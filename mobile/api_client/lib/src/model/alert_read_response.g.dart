// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'alert_read_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AlertReadResponseCWProxy {
  AlertReadResponse status(String status);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AlertReadResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AlertReadResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AlertReadResponse call({String status});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAlertReadResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAlertReadResponse.copyWith.fieldName(...)`
class _$AlertReadResponseCWProxyImpl implements _$AlertReadResponseCWProxy {
  const _$AlertReadResponseCWProxyImpl(this._value);

  final AlertReadResponse _value;

  @override
  AlertReadResponse status(String status) => this(status: status);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AlertReadResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AlertReadResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AlertReadResponse call({Object? status = const $CopyWithPlaceholder()}) {
    return AlertReadResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String,
    );
  }
}

extension $AlertReadResponseCopyWith on AlertReadResponse {
  /// Returns a callable class that can be used as follows: `instanceOfAlertReadResponse.copyWith(...)` or like so:`instanceOfAlertReadResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AlertReadResponseCWProxy get copyWith =>
      _$AlertReadResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AlertReadResponse _$AlertReadResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('AlertReadResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['status']);
      final val = AlertReadResponse(
        status: $checkedConvert('status', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$AlertReadResponseToJson(AlertReadResponse instance) =>
    <String, dynamic>{'status': instance.status};
