//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'feedback_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class FeedbackResponse {
  /// Returns a new [FeedbackResponse] instance.
  FeedbackResponse({
    required this.id,

    required this.predictionId,

    required this.isCorrect,

    required this.farmerNote,
  });

  @JsonKey(name: r'id', required: true, includeIfNull: false)
  final int id;

  @JsonKey(name: r'prediction_id', required: true, includeIfNull: false)
  final int predictionId;

  @JsonKey(name: r'is_correct', required: true, includeIfNull: false)
  final bool isCorrect;

  @JsonKey(name: r'farmer_note', required: true, includeIfNull: true)
  final String? farmerNote;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is FeedbackResponse &&
          other.id == id &&
          other.predictionId == predictionId &&
          other.isCorrect == isCorrect &&
          other.farmerNote == farmerNote;

  @override
  int get hashCode =>
      id.hashCode +
      predictionId.hashCode +
      isCorrect.hashCode +
      (farmerNote == null ? 0 : farmerNote.hashCode);

  factory FeedbackResponse.fromJson(Map<String, dynamic> json) =>
      _$FeedbackResponseFromJson(json);

  Map<String, dynamic> toJson() => _$FeedbackResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
