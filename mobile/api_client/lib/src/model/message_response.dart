//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'message_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class MessageResponse {
  /// Returns a new [MessageResponse] instance.
  MessageResponse({this.status = 'success', required this.message});

  @JsonKey(
    defaultValue: 'success',
    name: r'status',
    required: false,
    includeIfNull: false,
  )
  final String? status;

  @JsonKey(name: r'message', required: true, includeIfNull: false)
  final String message;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is MessageResponse &&
          other.status == status &&
          other.message == message;

  @override
  int get hashCode => status.hashCode + message.hashCode;

  factory MessageResponse.fromJson(Map<String, dynamic> json) =>
      _$MessageResponseFromJson(json);

  Map<String, dynamic> toJson() => _$MessageResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
