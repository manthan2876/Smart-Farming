// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'weather_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$WeatherResponseCWProxy {
  WeatherResponse temperatureCelsius(num? temperatureCelsius);

  WeatherResponse humidityPercent(num? humidityPercent);

  WeatherResponse condition(String? condition);

  WeatherResponse windSpeedMps(num? windSpeedMps);

  WeatherResponse pressureHpa(num? pressureHpa);

  WeatherResponse cloudinessPercent(num? cloudinessPercent);

  WeatherResponse advisory(String? advisory);

  WeatherResponse translatedAdvisory(String? translatedAdvisory);

  WeatherResponse translations(Map<String, String>? translations);

  WeatherResponse cached(bool? cached);

  WeatherResponse timestamp(num? timestamp);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WeatherResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WeatherResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  WeatherResponse call({
    num? temperatureCelsius,
    num? humidityPercent,
    String? condition,
    num? windSpeedMps,
    num? pressureHpa,
    num? cloudinessPercent,
    String? advisory,
    String? translatedAdvisory,
    Map<String, String>? translations,
    bool? cached,
    num? timestamp,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfWeatherResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfWeatherResponse.copyWith.fieldName(...)`
class _$WeatherResponseCWProxyImpl implements _$WeatherResponseCWProxy {
  const _$WeatherResponseCWProxyImpl(this._value);

  final WeatherResponse _value;

  @override
  WeatherResponse temperatureCelsius(num? temperatureCelsius) =>
      this(temperatureCelsius: temperatureCelsius);

  @override
  WeatherResponse humidityPercent(num? humidityPercent) =>
      this(humidityPercent: humidityPercent);

  @override
  WeatherResponse condition(String? condition) => this(condition: condition);

  @override
  WeatherResponse windSpeedMps(num? windSpeedMps) =>
      this(windSpeedMps: windSpeedMps);

  @override
  WeatherResponse pressureHpa(num? pressureHpa) =>
      this(pressureHpa: pressureHpa);

  @override
  WeatherResponse cloudinessPercent(num? cloudinessPercent) =>
      this(cloudinessPercent: cloudinessPercent);

  @override
  WeatherResponse advisory(String? advisory) => this(advisory: advisory);

  @override
  WeatherResponse translatedAdvisory(String? translatedAdvisory) =>
      this(translatedAdvisory: translatedAdvisory);

  @override
  WeatherResponse translations(Map<String, String>? translations) =>
      this(translations: translations);

  @override
  WeatherResponse cached(bool? cached) => this(cached: cached);

  @override
  WeatherResponse timestamp(num? timestamp) => this(timestamp: timestamp);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `WeatherResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// WeatherResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  WeatherResponse call({
    Object? temperatureCelsius = const $CopyWithPlaceholder(),
    Object? humidityPercent = const $CopyWithPlaceholder(),
    Object? condition = const $CopyWithPlaceholder(),
    Object? windSpeedMps = const $CopyWithPlaceholder(),
    Object? pressureHpa = const $CopyWithPlaceholder(),
    Object? cloudinessPercent = const $CopyWithPlaceholder(),
    Object? advisory = const $CopyWithPlaceholder(),
    Object? translatedAdvisory = const $CopyWithPlaceholder(),
    Object? translations = const $CopyWithPlaceholder(),
    Object? cached = const $CopyWithPlaceholder(),
    Object? timestamp = const $CopyWithPlaceholder(),
  }) {
    return WeatherResponse(
      temperatureCelsius: temperatureCelsius == const $CopyWithPlaceholder()
          ? _value.temperatureCelsius
          // ignore: cast_nullable_to_non_nullable
          : temperatureCelsius as num?,
      humidityPercent: humidityPercent == const $CopyWithPlaceholder()
          ? _value.humidityPercent
          // ignore: cast_nullable_to_non_nullable
          : humidityPercent as num?,
      condition: condition == const $CopyWithPlaceholder()
          ? _value.condition
          // ignore: cast_nullable_to_non_nullable
          : condition as String?,
      windSpeedMps: windSpeedMps == const $CopyWithPlaceholder()
          ? _value.windSpeedMps
          // ignore: cast_nullable_to_non_nullable
          : windSpeedMps as num?,
      pressureHpa: pressureHpa == const $CopyWithPlaceholder()
          ? _value.pressureHpa
          // ignore: cast_nullable_to_non_nullable
          : pressureHpa as num?,
      cloudinessPercent: cloudinessPercent == const $CopyWithPlaceholder()
          ? _value.cloudinessPercent
          // ignore: cast_nullable_to_non_nullable
          : cloudinessPercent as num?,
      advisory: advisory == const $CopyWithPlaceholder()
          ? _value.advisory
          // ignore: cast_nullable_to_non_nullable
          : advisory as String?,
      translatedAdvisory: translatedAdvisory == const $CopyWithPlaceholder()
          ? _value.translatedAdvisory
          // ignore: cast_nullable_to_non_nullable
          : translatedAdvisory as String?,
      translations: translations == const $CopyWithPlaceholder()
          ? _value.translations
          // ignore: cast_nullable_to_non_nullable
          : translations as Map<String, String>?,
      cached: cached == const $CopyWithPlaceholder()
          ? _value.cached
          // ignore: cast_nullable_to_non_nullable
          : cached as bool?,
      timestamp: timestamp == const $CopyWithPlaceholder()
          ? _value.timestamp
          // ignore: cast_nullable_to_non_nullable
          : timestamp as num?,
    );
  }
}

extension $WeatherResponseCopyWith on WeatherResponse {
  /// Returns a callable class that can be used as follows: `instanceOfWeatherResponse.copyWith(...)` or like so:`instanceOfWeatherResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$WeatherResponseCWProxy get copyWith => _$WeatherResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

WeatherResponse _$WeatherResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'WeatherResponse',
      json,
      ($checkedConvert) {
        final val = WeatherResponse(
          temperatureCelsius: $checkedConvert(
            'temperature_celsius',
            (v) => v as num?,
          ),
          humidityPercent: $checkedConvert(
            'humidity_percent',
            (v) => v as num?,
          ),
          condition: $checkedConvert('condition', (v) => v as String?),
          windSpeedMps: $checkedConvert('wind_speed_mps', (v) => v as num?),
          pressureHpa: $checkedConvert('pressure_hpa', (v) => v as num?),
          cloudinessPercent: $checkedConvert(
            'cloudiness_percent',
            (v) => v as num?,
          ),
          advisory: $checkedConvert('advisory', (v) => v as String?),
          translatedAdvisory: $checkedConvert(
            'translated_advisory',
            (v) => v as String?,
          ),
          translations: $checkedConvert(
            'translations',
            (v) => (v as Map<String, dynamic>?)?.map(
              (k, e) => MapEntry(k, e as String),
            ),
          ),
          cached: $checkedConvert('cached', (v) => v as bool?),
          timestamp: $checkedConvert('timestamp', (v) => v as num?),
        );
        return val;
      },
      fieldKeyMap: const {
        'temperatureCelsius': 'temperature_celsius',
        'humidityPercent': 'humidity_percent',
        'windSpeedMps': 'wind_speed_mps',
        'pressureHpa': 'pressure_hpa',
        'cloudinessPercent': 'cloudiness_percent',
        'translatedAdvisory': 'translated_advisory',
      },
    );

Map<String, dynamic> _$WeatherResponseToJson(WeatherResponse instance) =>
    <String, dynamic>{
      'temperature_celsius': ?instance.temperatureCelsius,
      'humidity_percent': ?instance.humidityPercent,
      'condition': ?instance.condition,
      'wind_speed_mps': ?instance.windSpeedMps,
      'pressure_hpa': ?instance.pressureHpa,
      'cloudiness_percent': ?instance.cloudinessPercent,
      'advisory': ?instance.advisory,
      'translated_advisory': ?instance.translatedAdvisory,
      'translations': ?instance.translations,
      'cached': ?instance.cached,
      'timestamp': ?instance.timestamp,
    };
