// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'feedback_response.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$FeedbackResponseCWProxy {
  FeedbackResponse id(int id);

  FeedbackResponse predictionId(int predictionId);

  FeedbackResponse isCorrect(bool isCorrect);

  FeedbackResponse farmerNote(String? farmerNote);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `FeedbackResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// FeedbackResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  FeedbackResponse call({
    int id,
    int predictionId,
    bool isCorrect,
    String? farmerNote,
  });
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfFeedbackResponse.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfFeedbackResponse.copyWith.fieldName(...)`
class _$FeedbackResponseCWProxyImpl implements _$FeedbackResponseCWProxy {
  const _$FeedbackResponseCWProxyImpl(this._value);

  final FeedbackResponse _value;

  @override
  FeedbackResponse id(int id) => this(id: id);

  @override
  FeedbackResponse predictionId(int predictionId) =>
      this(predictionId: predictionId);

  @override
  FeedbackResponse isCorrect(bool isCorrect) => this(isCorrect: isCorrect);

  @override
  FeedbackResponse farmerNote(String? farmerNote) =>
      this(farmerNote: farmerNote);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `FeedbackResponse(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// FeedbackResponse(...).copyWith(id: 12, name: "My name")
  /// ````
  FeedbackResponse call({
    Object? id = const $CopyWithPlaceholder(),
    Object? predictionId = const $CopyWithPlaceholder(),
    Object? isCorrect = const $CopyWithPlaceholder(),
    Object? farmerNote = const $CopyWithPlaceholder(),
  }) {
    return FeedbackResponse(
      id: id == const $CopyWithPlaceholder()
          ? _value.id
          // ignore: cast_nullable_to_non_nullable
          : id as int,
      predictionId: predictionId == const $CopyWithPlaceholder()
          ? _value.predictionId
          // ignore: cast_nullable_to_non_nullable
          : predictionId as int,
      isCorrect: isCorrect == const $CopyWithPlaceholder()
          ? _value.isCorrect
          // ignore: cast_nullable_to_non_nullable
          : isCorrect as bool,
      farmerNote: farmerNote == const $CopyWithPlaceholder()
          ? _value.farmerNote
          // ignore: cast_nullable_to_non_nullable
          : farmerNote as String?,
    );
  }
}

extension $FeedbackResponseCopyWith on FeedbackResponse {
  /// Returns a callable class that can be used as follows: `instanceOfFeedbackResponse.copyWith(...)` or like so:`instanceOfFeedbackResponse.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$FeedbackResponseCWProxy get copyWith => _$FeedbackResponseCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

FeedbackResponse _$FeedbackResponseFromJson(
  Map<String, dynamic> json,
) => $checkedCreate(
  'FeedbackResponse',
  json,
  ($checkedConvert) {
    $checkKeys(
      json,
      requiredKeys: const ['id', 'prediction_id', 'is_correct', 'farmer_note'],
    );
    final val = FeedbackResponse(
      id: $checkedConvert('id', (v) => (v as num).toInt()),
      predictionId: $checkedConvert('prediction_id', (v) => (v as num).toInt()),
      isCorrect: $checkedConvert('is_correct', (v) => v as bool),
      farmerNote: $checkedConvert('farmer_note', (v) => v as String?),
    );
    return val;
  },
  fieldKeyMap: const {
    'predictionId': 'prediction_id',
    'isCorrect': 'is_correct',
    'farmerNote': 'farmer_note',
  },
);

Map<String, dynamic> _$FeedbackResponseToJson(FeedbackResponse instance) =>
    <String, dynamic>{
      'id': instance.id,
      'prediction_id': instance.predictionId,
      'is_correct': instance.isCorrect,
      'farmer_note': instance.farmerNote,
    };
