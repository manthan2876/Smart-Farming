//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
// ignore: unused_import
import 'package:smart_farming_api/src/model/prediction_status_response.dart';
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'status.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class Status {
  /// Returns a new [Status] instance.
  Status({this.pipeline, this.preprocessing, this.expertReview});

  @JsonKey(name: r'pipeline', required: false, includeIfNull: false)
  final String? pipeline;

  @JsonKey(name: r'preprocessing', required: false, includeIfNull: false)
  final String? preprocessing;

  @JsonKey(name: r'expert_review', required: false, includeIfNull: false)
  final String? expertReview;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Status &&
          other.pipeline == pipeline &&
          other.preprocessing == preprocessing &&
          other.expertReview == expertReview;

  @override
  int get hashCode =>
      (pipeline == null ? 0 : pipeline.hashCode) +
      (preprocessing == null ? 0 : preprocessing.hashCode) +
      (expertReview == null ? 0 : expertReview.hashCode);

  factory Status.fromJson(Map<String, dynamic> json) => _$StatusFromJson(json);

  Map<String, dynamic> toJson() => _$StatusToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
