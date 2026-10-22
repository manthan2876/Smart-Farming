// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'alert_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$AlertResponseCWProxy {
  AlertResponse id(int id);

  AlertResponse predictionId(int? predictionId);

  AlertResponse kind(String kind);

  AlertResponse severity(String severity);

  AlertResponse title(String title);

  AlertResponse body(String body);

  AlertResponse isRead(bool isRead);

  AlertResponse createdAt(DateTime? createdAt);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AlertResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AlertResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AlertResponse call({
    int id,
    int? predictionId,
    String kind,
    String severity,
    String title,
    String body,
    bool isRead,
    DateTime? createdAt,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfAlertResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfAlertResponse.copyWith.fieldName(...)`
class _$AlertResponseCWProxyImpl implements _$AlertResponseCWProxy {
  const _$AlertResponseCWProxyImpl(this._value);

  final AlertResponse _value;

  @override
  AlertResponse id(int id) => this(id: id);

  @override
  AlertResponse predictionId(int? predictionId) =>
      this(predictionId: predictionId);

  @override
  AlertResponse kind(String kind) => this(kind: kind);

  @override
  AlertResponse severity(String severity) => this(severity: severity);

  @override
  AlertResponse title(String title) => this(title: title);

  @override
  AlertResponse body(String body) => this(body: body);

  @override
  AlertResponse isRead(bool isRead) => this(isRead: isRead);

  @override
  AlertResponse createdAt(DateTime? createdAt) => this(createdAt: createdAt);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `AlertResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// AlertResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  AlertResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? predictionId = const $CopyWithPlaceholder(),
    Object? kind = const $CopyWithPlaceholder(),
    Object? severity = const $CopyWithPlaceholder(),
    Object? title = const $CopyWithPlaceholder(),
    Object? body = const $CopyWithPlaceholder(),
    Object? isRead = const $CopyWithPlaceholder(),
    Object? createdAt = const $CopyWithPlaceholder(),
  }) {
    return AlertResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as int,
      predictionId: predictionId == const $CopyWithPlaceholder()
          ? _value.predictionId
          // ignore: cast_nullable_to_non_nullable
          : predictionId as int?,
      kind: kind == const $CopyWithPlaceholder()
          ? _value.kind
          // ignore: cast_nullable_to_non_nullable
          : kind as String,
      severity: severity == const $CopyWithPlaceholder()
          ? _value.severity
          // ignore: cast_nullable_to_non_nullable
          : severity as String,
      title: title == const $CopyWithPlaceholder()
          ? _value.title
          // ignore: cast_nullable_to_non_nullable
          : title as String,
      body: body == const $CopyWithPlaceholder()
          ? _value.body
          // ignore: cast_nullable_to_non_nullable
          : body as String,
      isRead: isRead == const $CopyWithPlaceholder()
          ? _value.isRead
          // ignore: cast_nullable_to_non_nullable
          : isRead as bool,
      createdAt: createdAt == const $CopyWithPlaceholder()
          ? _value.createdAt
          // ignore: cast_nullable_to_non_nullable
          : createdAt as DateTime?,
    );
  }
}

extension $AlertResponseCopyWith on AlertResponse {
  /// Returns a callable class that can be used as follows: `instanceOfAlertResponse.copyWith(...)` or like so:`instanceOfAlertResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$AlertResponseCWProxy get copyWith => _$AlertResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

AlertResponse _$AlertResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'AlertResponse',
      json,
      ($checkedConvert) {
        $checkKeys(
          json,
          requiredKeys: const [
            'id',
            'kind',
            'severity',
            'title',
            'body',
            'is_read',
          ],
        );
        final val = AlertResponse(
          id: $checkedConvert('id', (v) => (v as num).toInt()),
          predictionId: $checkedConvert(
            'prediction_id',
            (v) => (v as num?)?.toInt(),
          ),
          kind: $checkedConvert('kind', (v) => v as String),
          severity: $checkedConvert('severity', (v) => v as String),
          title: $checkedConvert('title', (v) => v as String),
          body: $checkedConvert('body', (v) => v as String),
          isRead: $checkedConvert('is_read', (v) => v as bool),
          createdAt: $checkedConvert(
            'created_at',
            (v) => v == null ? null : DateTime.parse(v as String),
          ),
        );
        return val;
      },
      fieldKeyMap: const {
        'predictionId': 'prediction_id',
        'isRead': 'is_read',
        'createdAt': 'created_at',
      },
    );

Map<String, dynamic> _$AlertResponseToJson(AlertResponse instance) =>
    <String, dynamic>{
      'id': instance.id,
      'prediction_id': ?instance.predictionId,
      'kind': instance.kind,
      'severity': instance.severity,
      'title': instance.title,
      'body': instance.body,
      'is_read': instance.isRead,
      'created_at': ?instance.createdAt?.toIso8601String(),
    };
