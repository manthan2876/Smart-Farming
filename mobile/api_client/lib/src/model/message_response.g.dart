// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'message_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$MessageResponseCWProxy {
  MessageResponse status(String? status);

  MessageResponse message(String message);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `MessageResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// MessageResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  MessageResponse call({String? status, String message});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfMessageResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfMessageResponse.copyWith.fieldName(...)`
class _$MessageResponseCWProxyImpl implements _$MessageResponseCWProxy {
  const _$MessageResponseCWProxyImpl(this._value);

  final MessageResponse _value;

  @override
  MessageResponse status(String? status) => this(status: status);

  @override
  MessageResponse message(String message) => this(message: message);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `MessageResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// MessageResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  MessageResponse call({
    Object? status = const $CopyWithPlaceholder(),
    Object? message = const $CopyWithPlaceholder(),
  }) {
    return MessageResponse(
      status: status == const $CopyWithPlaceholder()
          ? _value.status
          // ignore: cast_nullable_to_non_nullable
          : status as String?,
      message: message == const $CopyWithPlaceholder()
          ? _value.message
          // ignore: cast_nullable_to_non_nullable
          : message as String,
    );
  }
}

extension $MessageResponseCopyWith on MessageResponse {
  /// Returns a callable class that can be used as follows: `instanceOfMessageResponse.copyWith(...)` or like so:`instanceOfMessageResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$MessageResponseCWProxy get copyWith => _$MessageResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

MessageResponse _$MessageResponseFromJson(Map<String, dynamic> json) =>
    $checkedCreate('MessageResponse', json, ($checkedConvert) {
      $checkKeys(json, requiredKeys: const ['message']);
      final val = MessageResponse(
        status: $checkedConvert('status', (v) => v as String? ?? 'success'),
        message: $checkedConvert('message', (v) => v as String),
      );
      return val;
    });

Map<String, dynamic> _$MessageResponseToJson(MessageResponse instance) =>
    <String, dynamic>{'status': ?instance.status, 'message': instance.message};
