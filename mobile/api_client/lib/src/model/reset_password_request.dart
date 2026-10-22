//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'reset_password_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class ResetPasswordRequest {
  /// Returns a new [ResetPasswordRequest] instance.
  ResetPasswordRequest({required this.token, required this.newPassword});

  @JsonKey(name: r'token', required: true, includeIfNull: false)
  final String token;

  @JsonKey(name: r'new_password', required: true, includeIfNull: false)
  final String newPassword;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ResetPasswordRequest &&
          other.token == token &&
          other.newPassword == newPassword;

  @override
  int get hashCode => token.hashCode + newPassword.hashCode;

  factory ResetPasswordRequest.fromJson(Map<String, dynamic> json) =>
      _$ResetPasswordRequestFromJson(json);

  Map<String, dynamic> toJson() => _$ResetPasswordRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
