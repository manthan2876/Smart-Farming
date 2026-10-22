//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'tts_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class TTSResponse {
  /// Returns a new [TTSResponse] instance.
  TTSResponse({
    required this.audioContent,

    required this.format,

    required this.cached,
  });

  @JsonKey(name: r'audioContent', required: true, includeIfNull: false)
  final String audioContent;

  @JsonKey(name: r'format', required: true, includeIfNull: false)
  final String format;

  @JsonKey(name: r'cached', required: true, includeIfNull: false)
  final bool cached;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is TTSResponse &&
          other.audioContent == audioContent &&
          other.format == format &&
          other.cached == cached;

  @override
  int get hashCode => audioContent.hashCode + format.hashCode + cached.hashCode;

  factory TTSResponse.fromJson(Map<String, dynamic> json) =>
      _$TTSResponseFromJson(json);

  Map<String, dynamic> toJson() => _$TTSResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
