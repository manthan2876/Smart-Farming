//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'alert_read_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class AlertReadResponse {
  /// Returns a new [AlertReadResponse] instance.
  AlertReadResponse({

    required  this.status,
  });

  @JsonKey(
    
    name: r'status',
    required: true,
    includeIfNull: false,
  )


  final String status;





    @override
    bool operator ==(Object other) => identical(this, other) || other is AlertReadResponse &&
      other.status == status;

    @override
    int get hashCode =>
        status.hashCode;

  factory AlertReadResponse.fromJson(Map<String, dynamic> json) => _$AlertReadResponseFromJson(json);

  Map<String, dynamic> toJson() => _$AlertReadResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

