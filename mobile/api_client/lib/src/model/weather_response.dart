//
// AUTO-GENERATED FILE, DO NOT MODIFY!
//

// ignore_for_file: unused_element
import 'package:copy_with_extension/copy_with_extension.dart';
import 'package:json_annotation/json_annotation.dart';

part 'weather_response.g.dart';

@CopyWith()
@JsonSerializable(
  checked: true,
  createToJson: true,
  disallowUnrecognizedKeys: false,
  explicitToJson: true,
)
class WeatherResponse {
  /// Returns a new [WeatherResponse] instance.
  WeatherResponse({
    this.temperatureCelsius,

    this.humidityPercent,

    this.condition,

    this.windSpeedMps,

    this.pressureHpa,

    this.cloudinessPercent,

    this.advisory,

    this.translatedAdvisory,

    this.translations,

    this.cached,

    this.timestamp,
  });

  @JsonKey(name: r'temperature_celsius', required: false, includeIfNull: false)
  final num? temperatureCelsius;

  @JsonKey(name: r'humidity_percent', required: false, includeIfNull: false)
  final num? humidityPercent;

  @JsonKey(name: r'condition', required: false, includeIfNull: false)
  final String? condition;

  @JsonKey(name: r'wind_speed_mps', required: false, includeIfNull: false)
  final num? windSpeedMps;

  @JsonKey(name: r'pressure_hpa', required: false, includeIfNull: false)
  final num? pressureHpa;

  @JsonKey(name: r'cloudiness_percent', required: false, includeIfNull: false)
  final num? cloudinessPercent;

  @JsonKey(name: r'advisory', required: false, includeIfNull: false)
  final String? advisory;

  @JsonKey(name: r'translated_advisory', required: false, includeIfNull: false)
  final String? translatedAdvisory;

  @JsonKey(name: r'translations', required: false, includeIfNull: false)
  final Map<String, String>? translations;

  @JsonKey(name: r'cached', required: false, includeIfNull: false)
  final bool? cached;

  @JsonKey(name: r'timestamp', required: false, includeIfNull: false)
  final num? timestamp;

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is WeatherResponse &&
          other.temperatureCelsius == temperatureCelsius &&
          other.humidityPercent == humidityPercent &&
          other.condition == condition &&
          other.windSpeedMps == windSpeedMps &&
          other.pressureHpa == pressureHpa &&
          other.cloudinessPercent == cloudinessPercent &&
          other.advisory == advisory &&
          other.translatedAdvisory == translatedAdvisory &&
          other.translations == translations &&
          other.cached == cached &&
          other.timestamp == timestamp;

  @override
  int get hashCode =>
      (temperatureCelsius == null ? 0 : temperatureCelsius.hashCode) +
      (humidityPercent == null ? 0 : humidityPercent.hashCode) +
      (condition == null ? 0 : condition.hashCode) +
      (windSpeedMps == null ? 0 : windSpeedMps.hashCode) +
      (pressureHpa == null ? 0 : pressureHpa.hashCode) +
      (cloudinessPercent == null ? 0 : cloudinessPercent.hashCode) +
      (advisory == null ? 0 : advisory.hashCode) +
      (translatedAdvisory == null ? 0 : translatedAdvisory.hashCode) +
      translations.hashCode +
      (cached == null ? 0 : cached.hashCode) +
      (timestamp == null ? 0 : timestamp.hashCode);

  factory WeatherResponse.fromJson(Map<String, dynamic> json) =>
      _$WeatherResponseFromJson(json);

  Map<String, dynamic> toJson() => _$WeatherResponseToJson(this);

  @override
  String toString() {
    return toJson().toString();
  }
}
