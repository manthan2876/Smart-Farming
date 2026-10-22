//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'feedback_request.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class FeedbackRequest {
  /// Returns a new [FeedbackRequest] instance.
  FeedbackRequest({
    required this.predictionId,

    required this.isCorrect,

    this.farmerNote,
  });

  // minimum: 0
  @JsonKey(name: r'prediction_id', required: true, includeIfNull: false)
  final int predictionId;

  @JsonKey(name: r'is_correct', required: true, includeIfNull: false)
  final bool isCorrect;

  @JsonKey(name: r'farmer_note', required: false, includeIfNull: false)
  final String? farmerNote;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FeedbackRequest &&
          other.predictionId == predictionId &&
          other.isCorrect == isCorrect &&
          other.farmerNote == farmerNote;

  @override
  int get hashCode =>
      predictionId.hashCode +
      isCorrect.hashCode +
      (farmerNote == null ? 0 : farmerNote.hashCode);

  factory FeedbackRequest.fromJson(Map<String, dynamic> json) =>
      _$FeedbackRequestFromJson(json);

  Map<String, dynamic> toJson() => _$FeedbackRequestToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
