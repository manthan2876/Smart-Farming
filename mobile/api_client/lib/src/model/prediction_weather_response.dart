//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'prediction_weather_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class PredictionWeatherResponse {
  /// Returns a new [PredictionWeatherResponse] instance.
  PredictionWeatherResponse({
    this.temperatureCelsius,

    this.humidityPercent,

    this.condition,

    this.status,
  });

  @JsonKey(name: r'temperature_celsius', required: false, includeIfNull: false)
  final num? temperatureCelsius;

  @JsonKey(name: r'humidity_percent', required: false, includeIfNull: false)
  final num? humidityPercent;

  @JsonKey(name: r'condition', required: false, includeIfNull: false)
  final String? condition;

  @JsonKey(name: r'status', required: false, includeIfNull: false)
  final String? status;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is PredictionWeatherResponse &&
          other.temperatureCelsius == temperatureCelsius &&
          other.humidityPercent == humidityPercent &&
          other.condition == condition &&
          other.status == status;

  @override
  int get hashCode =>
      (temperatureCelsius == null ? 0 : temperatureCelsius.hashCode) +
      (humidityPercent == null ? 0 : humidityPercent.hashCode) +
      (condition == null ? 0 : condition.hashCode) +
      (status == null ? 0 : status.hashCode);

  factory PredictionWeatherResponse.fromJson(Map<String, dynamic> json) =>
      _$PredictionWeatherResponseFromJson(json);

  Map<String, dynamic> toJson() => _$PredictionWeatherResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
