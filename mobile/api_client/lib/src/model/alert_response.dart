//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'alert_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AlertResponse {
  /// Returns a new [AlertResponse] instance.
  AlertResponse({

    required  this.id,

     this.predictionId,

    required  this.kind,

    required  this.severity,

    required  this.title,

    required  this.body,

    required  this.isRead,

     this.createdAt,
  });

  @JsonKey(
    
    name: r'id',
    required: true,
    includeIfNull: false,
  )


  final int id;



  @JsonKey(
    
    name: r'prediction_id',
    required: false,
    includeIfNull: false,
  )


  final int? predictionId;



  @JsonKey(
    
    name: r'kind',
    required: true,
    includeIfNull: false,
  )


  final String kind;



  @JsonKey(
    
    name: r'severity',
    required: true,
    includeIfNull: false,
  )


  final String severity;



  @JsonKey(
    
    name: r'title',
    required: true,
    includeIfNull: false,
  )


  final String title;



  @JsonKey(
    
    name: r'body',
    required: true,
    includeIfNull: false,
  )


  final String body;



  @JsonKey(
    
    name: r'is_read',
    required: true,
    includeIfNull: false,
  )


  final bool isRead;



  @JsonKey(
    
    name: r'created_at',
    required: false,
    includeIfNull: false,
  )


  final DateTime? createdAt;





    @override
    bool operator ==(Object other) => identical(this, other) || other is AlertResponse &&
      other.id == id &&
      other.predictionId == predictionId &&
      other.kind == kind &&
      other.severity == severity &&
      other.title == title &&
      other.body == body &&
      other.isRead == isRead &&
      other.createdAt == createdAt;

    @override
    int get hashCode =>
        id.hashCode +
        (predictionId == null ? 0 : predictionId.hashCode) +
        kind.hashCode +
        severity.hashCode +
        title.hashCode +
        body.hashCode +
        isRead.hashCode +
        (createdAt == null ? 0 : createdAt.hashCode);

  factory AlertResponse.fromJson(Map<String, dynamic> json) => _$AlertResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AlertResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

