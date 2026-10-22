//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'crop_list_response.g.dart';


@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class CropListResponse {
  /// Returns a new [CropListResponse] instance.
  CropListResponse({

    required  this.crops,
  });

  @JsonKey(
    
    name: r'crops',
    required: true,
    includeIfNull: false,
  )


  final List<String> crops;





    @override
    bool operator ==(Object other) => identical(this, other) || other is CropListResponse &&
      other.crops == crops;

    @override
    int get hashCode =>
        crops.hashCode;

  factory CropListResponse.fromJson(Map<String, dynamic> json) => _$CropListResponseFromJson(json);

  Map<String, dynamic> toJson() => _$CropListResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }

}

