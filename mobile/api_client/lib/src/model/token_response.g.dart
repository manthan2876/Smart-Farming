// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'token_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$TokenResponseCWProxy {
  TokenResponse accessToken(String accessToken);

  TokenResponse refreshToken(String refreshToken);

  TokenResponse tokenType(String? tokenType);

  TokenResponse expiresIn(int? expiresIn);

  TokenResponse verificationRequired(bool? verificationRequired);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TokenResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TokenResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  TokenResponse call({
    String accessToken,
    String refreshToken,
    String? tokenType,
    int? expiresIn,
    bool? verificationRequired,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfTokenResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfTokenResponse.copyWith.fieldName(...)`
class _$TokenResponseCWProxyImpl implements _$TokenResponseCWProxy {
  const _$TokenResponseCWProxyImpl(this._value);

  final TokenResponse _value;

  @override
  TokenResponse accessToken(String accessToken) =>
      this(accessToken: accessToken);

  @override
  TokenResponse refreshToken(String refreshToken) =>
      this(refreshToken: refreshToken);

  @override
  TokenResponse tokenType(String? tokenType) => this(tokenType: tokenType);

  @override
  TokenResponse expiresIn(int? expiresIn) => this(expiresIn: expiresIn);

  @override
  TokenResponse verificationRequired(bool? verificationRequired) =>
      this(verificationRequired: verificationRequired);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `TokenResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// TokenResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  TokenResponse call({
    Object? accessToken = const $CopyWithPlaceholder(),
    Object? refreshToken = const $CopyWithPlaceholder(),
    Object? tokenType = const $CopyWithPlaceholder(),
    Object? expiresIn = const $CopyWithPlaceholder(),
    Object? verificationRequired = const $CopyWithPlaceholder(),
  }) {
    return TokenResponse(
      accessToken: accessToken == const $CopyWithPlaceholder()
          ? _value.accessToken
          // ignore: cast_nullable_to_non_nullable
          : accessToken as String,
      refreshToken: refreshToken == const $CopyWithPlaceholder()
          ? _value.refreshToken
          // ignore: cast_nullable_to_non_nullable
          : refreshToken as String,
      tokenType: tokenType == const $CopyWithPlaceholder()
          ? _value.tokenType
          // ignore: cast_nullable_to_non_nullable
          : tokenType as String?,
      expiresIn: expiresIn == const $CopyWithPlaceholder()
          ? _value.expiresIn
          // ignore: cast_nullable_to_non_nullable
          : expiresIn as int?,
      verificationRequired: verificationRequired == const $CopyWithPlaceholder()
          ? _value.verificationRequired
          // ignore: cast_nullable_to_non_nullable
          : verificationRequired as bool?,
    );
  }
}

extension $TokenResponseCopyWith on TokenResponse {
  /// Returns a callable class that can be used as follows: `instanceOfTokenResponse.copyWith(...)` or like so:`instanceOfTokenResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$TokenResponseCWProxy get copyWith => _$TokenResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

TokenResponse _$TokenResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'TokenResponse',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['access_token', 'refresh_token']);
        final val = TokenResponse(
          accessToken: $checkedConvert('access_token', (v) => v as String),
          refreshToken: $checkedConvert('refresh_token', (v) => v as String),
          tokenType: $checkedConvert(
            'token_type',
            (v) => v as String? ?? 'bearer',
          ),
          expiresIn: $checkedConvert(
            'expires_in',
            (v) => (v as num?)?.toInt() ?? 3600,
          ),
          verificationRequired: $checkedConvert(
            'verification_required',
            (v) => v as bool?,
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'accessToken': 'access_token',
        'refreshToken': 'refresh_token',
        'tokenType': 'token_type',
        'expiresIn': 'expires_in',
        'verificationRequired': 'verification_required',
      },
    );

Map<String, dynamic> _$TokenResponseToJson(TokenResponse instance) =>
    <String, dynamic>{
      'access_token': instance.accessToken,
      'refresh_token': instance.refreshToken,
      'token_type': ?instance.tokenType,
      'expires_in': ?instance.expiresIn,
      'verification_required': ?instance.verificationRequired,
    };
