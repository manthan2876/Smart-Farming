// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'refresh_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$RefreshRequestCWProxy {
  RefreshRequest refreshToken(String refreshToken);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `RefreshRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// RefreshRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  RefreshRequest call({String refreshToken});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfRefreshRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfRefreshRequest.copyWith.fieldName(...)`
class _$RefreshRequestCWProxyImpl implements _$RefreshRequestCWProxy {
  const _$RefreshRequestCWProxyImpl(this._value);

  final RefreshRequest _value;

  @override
  RefreshRequest refreshToken(String refreshToken) =>
      this(refreshToken: refreshToken);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `RefreshRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// RefreshRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  RefreshRequest call({Object? refreshToken = const $CopyWithPlaceholder()}) {
    return RefreshRequest(
      refreshToken: refreshToken == const $CopyWithPlaceholder()
          ? _value.refreshToken
          // ignore: cast_nullable_to_non_nullable
          : refreshToken as String,
    );
  }
}

extension $RefreshRequestCopyWith on RefreshRequest {
  /// Returns a callable class that can be used as follows: `instanceOfRefreshRequest.copyWith(...)` or like so:`instanceOfRefreshRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$RefreshRequestCWProxy get copyWith => _$RefreshRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

RefreshRequest _$RefreshRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate('RefreshRequest', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['refresh_token']);
      final val = RefreshRequest(
        refreshToken: $checkedConvert('refresh_token', (v) => v as String),
      );
      return val;
    }, fieldKeyMap: const {'refreshToken': 'refresh_token'});

Map<String, dynamic> _$RefreshRequestToJson(RefreshRequest instance) =>
    <String, dynamic>{'refresh_token': instance.refreshToken};
