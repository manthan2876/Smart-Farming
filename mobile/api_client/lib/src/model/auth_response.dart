//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:smart_farming_api/src/model/token_response.dart';
import 'package:smart_farming_api/src/model/profile_response.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'auth_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AuthResponse {
  /// Returns a new [AuthResponse] instance.
  AuthResponse({required this.tokens, required this.user});

  @JsonKey(name: r'tokens', required: true, includeIfNull: false)
  final TokenResponse tokens;

  @JsonKey(name: r'user', required: true, includeIfNull: false)
  final ProfileResponse user;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is AuthResponse && other.tokens == tokens && other.user == user;

  @override
  int get hashCode => tokens.hashCode + user.hashCode;

  factory AuthResponse.fromJson(Map<String, dynamic> json) =>
      _$AuthResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AuthResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
