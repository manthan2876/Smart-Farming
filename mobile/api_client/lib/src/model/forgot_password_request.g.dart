// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'forgot_password_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$ForgotPasswordRequestCWProxy {
  ForgotPasswordRequest email(String email);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ForgotPasswordRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ForgotPasswordRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  ForgotPasswordRequest call({String email});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfForgotPasswordRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfForgotPasswordRequest.copyWith.fieldName(...)`
class _$ForgotPasswordRequestCWProxyImpl
    implements _$ForgotPasswordRequestCWProxy {
  const _$ForgotPasswordRequestCWProxyImpl(this._value);

  final ForgotPasswordRequest _value;

  @override
  ForgotPasswordRequest email(String email) => this(email: email);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `ForgotPasswordRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// ForgotPasswordRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  ForgotPasswordRequest call({Object? email = const $CopyWithPlaceholder()}) {
    return ForgotPasswordRequest(
      email: email == const $CopyWithPlaceholder()
          ? _value.email
          // ignore: cast_nullable_to_non_nullable
          : email as String,
    );
  }
}

extension $ForgotPasswordRequestCopyWith on ForgotPasswordRequest {
  /// Returns a callable class that can be used as follows: `instanceOfForgotPasswordRequest.copyWith(...)` or like so:`instanceOfForgotPasswordRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$ForgotPasswordRequestCWProxy get copyWith =>
      _$ForgotPasswordRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

ForgotPasswordRequest _$ForgotPasswordRequestFromJson(
  Map<String, dynamic> json,
) => $checkedCreate('ForgotPasswordRequest', json, ($checkedConvert) {
  $checkKeys(json, requiredKeys: const ['email']);
  final val = ForgotPasswordRequest(
    email: $checkedConvert('email', (v) => v as String),
  );
  return val;
});

Map<String, dynamic> _$ForgotPasswordRequestToJson(
  ForgotPasswordRequest instance,
) => <String, dynamic>{'email': instance.email};
