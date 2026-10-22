//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'prediction_severity_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PredictionSeverityResponse {
  /// Returns a new [PredictionSeverityResponse] instance.
  PredictionSeverityResponse({this.percent, this.bucket});

  @JsonKey(name: r'percent', required: false, includeIfNull: false)
  final num? percent;

  @JsonKey(name: r'bucket', required: false, includeIfNull: false)
  final String? bucket;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PredictionSeverityResponse &&
          other.percent == percent &&
          other.bucket == bucket;

  @override
  int get hashCode =>
      (percent == null ? 0 : percent.hashCode) +
      (bucket == null ? 0 : bucket.hashCode);

  factory PredictionSeverityResponse.fromJson(Map<String, dynamic> json) =>
      _$PredictionSeverityResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PredictionSeverityResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
