//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'prediction_label_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PredictionLabelResponse {
  /// Returns a new [PredictionLabelResponse] instance.
  PredictionLabelResponse({this.label, this.confidence, this.modelUsed});

  @JsonKey(name: r'label', required: false, includeIfNull: false)
  final String? label;

  @JsonKey(name: r'confidence', required: false, includeIfNull: false)
  final num? confidence;

  @JsonKey(name: r'model_used', required: false, includeIfNull: false)
  final String? modelUsed;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PredictionLabelResponse &&
          other.label == label &&
          other.confidence == confidence &&
          other.modelUsed == modelUsed;

  @override
  int get hashCode =>
      (label == null ? 0 : label.hashCode) +
      (confidence == null ? 0 : confidence.hashCode) +
      (modelUsed == null ? 0 : modelUsed.hashCode);

  factory PredictionLabelResponse.fromJson(Map<String, dynamic> json) =>
      _$PredictionLabelResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PredictionLabelResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
