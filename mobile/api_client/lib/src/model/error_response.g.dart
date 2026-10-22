// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'error_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ErrorResponseCWProxy {
  ErrorResponse detail(String detail);

  ErrorResponse status(String? status);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ErrorResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ErrorResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ErrorResponse call({String detail, String? status});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfErrorResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfErrorResponse.copyWith.fieldName(...)`
class _$ErrorResponseCWProxyImpl implements _$ErrorResponseCWProxy {
  const _$ErrorResponseCWProxyImpl(this._value);

  final ErrorResponse _value;

  @override
  ErrorResponse detail(String detail) => this(detail: detail);

  @override
  ErrorResponse status(String? status) => this(status: status);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ErrorResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ErrorResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  ErrorResponse call({
    Object? detail = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
  }) {
    return ErrorResponse(
      detail: detail == const $CopyWithPlaceholder()
          ? _value.detail
          // ignore: cast_nullable_to_non_nullable
          : detail as String,
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String?,
    );
  }
}

extension $ErrorResponseCopyWith on ErrorResponse {
  /// Returns a callable class that can be used as follows: `instanceOfErrorResponse.copyWith(...)` or like so:`instanceOfErrorResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ErrorResponseCWProxy get copyWith => _$ErrorResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ErrorResponse _$ErrorResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('ErrorResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['detail']);
      final val = ErrorResponse(
        detail: $checkedConvert('detail', (v) => v as String),
        status: $checkedConvert('status', (v) => v as String?),
      );
      return val;
    });

Map<String, dynamic> _$ErrorResponseToJson(ErrorResponse instance) =>
    <String, dynamic>{'detail': instance.detail, 'status': ?instance.status};
