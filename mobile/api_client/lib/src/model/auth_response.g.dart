// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'auth_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AuthResponseCWProxy {
  AuthResponse tokens(TokenResponse tokens);

  AuthResponse user(ProfileResponse user);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AuthResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AuthResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AuthResponse call({TokenResponse tokens, ProfileResponse user});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAuthResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAuthResponse.copyWith.fieldName(...)`
class _$AuthResponseCWProxyImpl implements _$AuthResponseCWProxy {
  const _$AuthResponseCWProxyImpl(this._value);

  final AuthResponse _value;

  @override
  AuthResponse tokens(TokenResponse tokens) => this(tokens: tokens);

  @override
  AuthResponse user(ProfileResponse user) => this(user: user);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AuthResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AuthResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AuthResponse call({
    Object? tokens = const $CopyWithPlaceholder(),
    Object? user = const $CopyWithPlaceholder(),
  }) {
    return AuthResponse(
      tokens: tokens == const $CopyWithPlaceholder()
          ? _value.tokens
          // ignore: cast_nullable_to_non_nullable
          : tokens as TokenResponse,
      user: user == const $CopyWithPlaceholder()
          ? _value.user
          // ignore: cast_nullable_to_non_nullable
          : user as ProfileResponse,
    );
  }
}

extension $AuthResponseCopyWith on AuthResponse {
  /// Returns a callable class that can be used as follows: `instanceOfAuthResponse.copyWith(...)` or like so:`instanceOfAuthResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AuthResponseCWProxy get copyWith => _$AuthResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AuthResponse _$AuthResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('AuthResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['tokens', 'user']);
      final val = AuthResponse(
        tokens: $checkedConvert(
          'tokens',
          (v) => TokenResponse.fromJson(v as Map<String, dynamic>),
        ),
        user: $checkedConvert(
          'user',
          (v) => ProfileResponse.fromJson(v as Map<String, dynamic>),
        ),
      );
      return val;
    });

Map<String, dynamic> _$AuthResponseToJson(AuthResponse instance) =>
    <String, dynamic>{
      'tokens': instance.tokens.toJson(),
      'user': instance.user.toJson(),
    };
