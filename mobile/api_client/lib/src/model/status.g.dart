// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'status.dart';

// **************************************************************************
// CopyWithGenerator
// **************************************************************************

abstract class _$StatusCWProxy {
  Status pipeline(String? pipeline);

  Status preprocessing(String? preprocessing);

  Status expertReview(String? expertReview);

  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `Status(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// Status(...).copyWith(id: 12, name: "My name")
  /// ````
  Status call({String? pipeline, String? preprocessing, String? expertReview});
}

/// Proxy class for `copyWith` functionality. This is a callable class and can be used as follows: `instanceOfStatus.copyWith(...)`. Additionally contains functions for specific fields e.g. `instanceOfStatus.copyWith.fieldName(...)`
class _$StatusCWProxyImpl implements _$StatusCWProxy {
  const _$StatusCWProxyImpl(this._value);

  final Status _value;

  @override
  Status pipeline(String? pipeline) => this(pipeline: pipeline);

  @override
  Status preprocessing(String? preprocessing) =>
      this(preprocessing: preprocessing);

  @override
  Status expertReview(String? expertReview) => this(expertReview: expertReview);

  @override
  /// This function **does support** nullification of nullable fields. All `null` values passed to `non-nullable` fields will be ignored. You can also use `Status(...).copyWith.fieldName(...)` to override fields one at a time with nullification support.
  ///
  /// Usage
  /// ```dart
  /// Status(...).copyWith(id: 12, name: "My name")
  /// ````
  Status call({
    Object? pipeline = const $CopyWithPlaceholder(),
    Object? preprocessing = const $CopyWithPlaceholder(),
    Object? expertReview = const $CopyWithPlaceholder(),
  }) {
    return Status(
      pipeline: pipeline == const $CopyWithPlaceholder()
          ? _value.pipeline
          // ignore: cast_nullable_to_non_nullable
          : pipeline as String?,
      preprocessing: preprocessing == const $CopyWithPlaceholder()
          ? _value.preprocessing
          // ignore: cast_nullable_to_non_nullable
          : preprocessing as String?,
      expertReview: expertReview == const $CopyWithPlaceholder()
          ? _value.expertReview
          // ignore: cast_nullable_to_non_nullable
          : expertReview as String?,
    );
  }
}

extension $StatusCopyWith on Status {
  /// Returns a callable class that can be used as follows: `instanceOfStatus.copyWith(...)` or like so:`instanceOfStatus.copyWith.fieldName(...)`.
  // ignore: library_private_types_in_public_api
  _$StatusCWProxy get copyWith => _$StatusCWProxyImpl(this);
}

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Status _$StatusFromJson(Map<String, dynamic> json) =>
    $checkedCreate('Status', json, ($checkedConvert) {
      final val = Status(
        pipeline: $checkedConvert('pipeline', (v) => v as String?),
        preprocessing: $checkedConvert('preprocessing', (v) => v as String?),
        expertReview: $checkedConvert('expert_review', (v) => v as String?),
      );
      return val;
    }, fieldKeyMap: const {'expertReview': 'expert_review'});

Map<String, dynamic> _$StatusToJson(Status instance) => <String, dynamic>{
  'pipeline': ?instance.pipeline,
  'preprocessing': ?instance.preprocessing,
  'expert_review': ?instance.expertReview,
};
