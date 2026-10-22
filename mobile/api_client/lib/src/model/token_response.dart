//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'token_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class TokenResponse {
  /// Returns a new [TokenResponse] instance.
  TokenResponse({
    required this.accessToken,

    required this.refreshToken,

    this.tokenType = 'bearer',

    this.expiresIn = 3600,

    this.verificationRequired,
  });

  @JsonKey(name: r'access_token', required: true, includeIfNull: false)
  final String accessToken;

  @JsonKey(name: r'refresh_token', required: true, includeIfNull: false)
  final String refreshToken;

  @JsonKey(
    defaultValue: 'bearer',
    name: r'token_type',
    required: false,
    includeIfNull: false,
  )
  final String? tokenType;

  @JsonKey(
    defaultValue: 3600,
    name: r'expires_in',
    required: false,
    includeIfNull: false,
  )
  final int? expiresIn;

  @JsonKey(
    name: r'verification_required',
    required: false,
    includeIfNull: false,
  )
  final bool? verificationRequired;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is TokenResponse &&
          other.accessToken == accessToken &&
          other.refreshToken == refreshToken &&
          other.tokenType == tokenType &&
          other.expiresIn == expiresIn &&
          other.verificationRequired == verificationRequired;

  @override
  int get hashCode =>
      accessToken.hashCode +
      refreshToken.hashCode +
      tokenType.hashCode +
      expiresIn.hashCode +
      (verificationRequired == null ? 0 : verificationRequired.hashCode);

  factory TokenResponse.fromJson(Map<String, dynamic> json) =>
      _$TokenResponseFromJson(json);

  Map<String, dynamic> toJson() => _$TokenResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
