//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'tts_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class TTSRequest {
  /// Returns a new [TTSRequest] instance.
  TTSRequest({required this.text, this.language});

  @JsonKey(name: r'text', required: true, includeIfNull: false)
  final String text;

  @JsonKey(name: r'language', required: false, includeIfNull: false)
  final String? language;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is TTSRequest && other.text == text && other.language == language;

  @override
  int get hashCode =>
      text.hashCode + (language == null ? 0 : language.hashCode);

  factory TTSRequest.fromJson(Map<String, dynamic> json) =>
      _$TTSRequestFromJson(json);

  Map<String, dynamic> toJson() => _$TTSRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
