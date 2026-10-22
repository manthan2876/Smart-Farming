// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'feedback_request.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$FeedbackRequestCWProxy {
  FeedbackRequest predictionId(int predictionId);

  FeedbackRequest isCorrect(bool isCorrect);

  FeedbackRequest farmerNote(String? farmerNote);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `FeedbackRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// FeedbackRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  FeedbackRequest call({int predictionId, bool isCorrect, String? farmerNote});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfFeedbackRequest.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfFeedbackRequest.copyWith.fieldName(...)`
class _$FeedbackRequestCWProxyImpl implements _$FeedbackRequestCWProxy {
  const _$FeedbackRequestCWProxyImpl(this._value);

  final FeedbackRequest _value;

  @override
  FeedbackRequest predictionId(int predictionId) =>
      this(predictionId: predictionId);

  @override
  FeedbackRequest isCorrect(bool isCorrect) => this(isCorrect: isCorrect);

  @override
  FeedbackRequest farmerNote(String? farmerNote) =>
      this(farmerNote: farmerNote);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `FeedbackRequest(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// FeedbackRequest(...).copyWith(id: 12, name: "My name")
  /// ````
  FeedbackRequest call({
    Object? predictionId = const $CopyWithPlaceholder(),
    Object? isCorrect = const $CopyWithPlaceholder(),
    Object? farmerNote = const $CopyWithPlaceholder(),
  }) {
    return FeedbackRequest(
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

extension $FeedbackRequestCopyWith on FeedbackRequest {
  /// Returns a callable class that can be used as follows: `instanceOfFeedbackRequest.copyWith(...)` or like so:`instanceOfFeedbackRequest.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$FeedbackRequestCWProxy get copyWith => _$FeedbackRequestCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

FeedbackRequest _$FeedbackRequestFromJson(Map<String, dynamic> json) =>
    $checkedCreate(
      'FeedbackRequest',
      json,
      ($checkedConvert) {
        $checkKeys(json, requiredKeys: const ['prediction_id', 'is_correct']);
        final val = FeedbackRequest(
          predictionId: $checkedConvert(
            'prediction_id',
            (v) => (v as num).toInt(),
          ),
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

Map<String, dynamic> _$FeedbackRequestToJson(FeedbackRequest instance) =>
    <String, dynamic>{
      'prediction_id': instance.predictionId,
      'is_correct': instance.isCorrect,
      'farmer_note': ?instance.farmerNote,
    };
