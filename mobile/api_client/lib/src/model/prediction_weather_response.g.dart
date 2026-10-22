// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'prediction_weather_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$PredictionWeatherResponseCWProxy {
  PredictionWeatherResponse temperatureCelsius(num? temperatureCelsius);

  PredictionWeatherResponse humidityPercent(num? humidityPercent);

  PredictionWeatherResponse condition(String? condition);

  PredictionWeatherResponse status(String? status);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionWeatherResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionWeatherResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionWeatherResponse call({
    num? temperatureCelsius,
    num? humidityPercent,
    String? condition,
    String? status,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfPredictionWeatherResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfPredictionWeatherResponse.copyWith.fieldName(...)`
class _$PredictionWeatherResponseCWProxyImpl
    implements _$PredictionWeatherResponseCWProxy {
  const _$PredictionWeatherResponseCWProxyImpl(this._value);

  final PredictionWeatherResponse _value;

  @override
  PredictionWeatherResponse temperatureCelsius(num? temperatureCelsius) =>
      this(temperatureCelsius: temperatureCelsius);

  @override
  PredictionWeatherResponse humidityPercent(num? humidityPercent) =>
      this(humidityPercent: humidityPercent);

  @override
  PredictionWeatherResponse condition(String? condition) =>
      this(condition: condition);

  @override
  PredictionWeatherResponse status(String? status) => this(status: status);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `PredictionWeatherResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// PredictionWeatherResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  PredictionWeatherResponse call({
    Object? temperatureCelsius = const $CopyWithPlaceholder(),
    Object? humidityPercent = const $CopyWithPlaceholder(),
    Object? condition = const $CopyWithPlaceholder(),
    Object? status = const $CopyWithPlaceholder(),
  }) {
    return PredictionWeatherResponse(
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
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String?,
    );
  }
}

extension $PredictionWeatherResponseCopyWith on PredictionWeatherResponse {
  /// Returns a callable class that can be used as follows: `instanceOfPredictionWeatherResponse.copyWith(...)` or like so:`instanceOfPredictionWeatherResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$PredictionWeatherResponseCWProxy get copyWith =>
      _$PredictionWeatherResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

PredictionWeatherResponse _$PredictionWeatherResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'PredictionWeatherResponse',
  json,
  ($checkedConvert) {
    final val = PredictionWeatherResponse(
      temperatureCelsius: $checkedConvert(
        'temperature_celsius',
        (v) => v as num?,
      ),
      humidityPercent: $checkedConvert('humidity_percent', (v) => v as num?),
      condition: $checkedConvert('condition', (v) => v as String?),
      status: $checkedConvert('status', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'temperatureCelsius': 'temperature_celsius',
    'humidityPercent': 'humidity_percent',
  },
);

Map<String, dynamic> _$PredictionWeatherResponseToJson(
  PredictionWeatherResponse instance,
) => <String, dynamic>{
  'temperature_celsius': ?instance.temperatureCelsius,
  'humidity_percent': ?instance.humidityPercent,
  'condition': ?instance.condition,
  'status': ?instance.status,
};
