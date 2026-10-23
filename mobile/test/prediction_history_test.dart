import 'package:flutter_test/flutter_test.dart';
import 'package:smart_farming_mobile/models/prediction.dart';
import 'package:smart_farming_mobile/utils/app_logger.dart';

void main() {
  group('Prediction Parsing and History Unit Tests', () {
    test('Correctly parses full structured prediction record from backend', () {
      final json = {
        'prediction_id': 51,
        'crop': {'label': 'Cotton', 'confidence': 0.99},
        'disease': {'label': 'Bacterial Blight', 'confidence': 0.95},
        'severity': {'percent': 63.27, 'bucket': 'Severe'},
        'recommendation': {
          'immediate_action': 'Prune affected leaves immediately.',
          'treatment': 'Apply copper-based bactericide.',
          'prevention': 'Ensure proper plant spacing.',
          'monitoring': 'Inspect every 48 hours.',
        },
        'image': {
          'raw_path': 'data/uploads/cotton_51.jpg',
          'processed_path': 'data/processed/cotton_51_overlay.jpg',
        },
        'status': {'pipeline': 'ready'},
        'created_at': '2026-09-22T10:00:00Z',
      };

      final pred = Prediction.fromJson(json);
      expect(pred.id, 51);
      expect(pred.crop, 'Cotton');
      expect(pred.disease, 'Bacterial Blight');
      expect(pred.confidence, 0.95);
      expect(pred.severity, 63);
      expect(pred.imagePath, 'data/processed/cotton_51_overlay.jpg');
      expect(pred.immediateAction, 'Prune affected leaves immediately.');
      expect(pred.treatment, 'Apply copper-based bactericide.');

      AppLogger.info('UnitTest', 'Parsed valid prediction #${pred.id}: ${pred.crop} - ${pred.disease}');
    });

    test('Correctly parses legacy / flat string crop & disease without throwing TypeError', () {
      final legacyJson = {
        'prediction_id': 52,
        'crop': 'Cotton', // String instead of Map
        'disease': 'Curl Virus', // String instead of Map
        'severity': 33.5, // num instead of Map
        'image': 'data/uploads/cotton_52.jpg', // String instead of Map
        'status': 'completed',
      };

      final pred = Prediction.fromJson(legacyJson);
      expect(pred.id, 52);
      expect(pred.crop, 'Cotton');
      expect(pred.disease, 'Curl Virus');
      expect(pred.severity, 34);

      AppLogger.info('UnitTest', 'Parsed legacy prediction #${pred.id}: ${pred.crop} - ${pred.disease}');
    });

    test('Correctly parses failed scan record without crashing', () {
      final failedJson = {
        'prediction_id': 43,
        'status': {'pipeline': 'failed'},
        'error': 'Image quality check failed. Leaf not centered.',
      };

      final pred = Prediction.fromJson(failedJson);
      expect(pred.id, 43);
      expect(pred.crop, 'Unknown crop');
      expect(pred.disease, 'Unknown condition');
      expect(pred.severity, 0);
      expect(pred.recommendation, 'Image quality check failed. Leaf not centered.');

      AppLogger.info('UnitTest', 'Parsed failed scan #${pred.id}: ${pred.status}');
    });

    test('Correctly parses expert review findings and verifies prediction', () {
      final reviewedJson = {
        'prediction_id': 55,
        'crop': {'label': 'Cotton', 'confidence': 0.88},
        'disease': {'label': 'Bacterial Blight', 'confidence': 0.72},
        'severity': {'percent': 45.0, 'bucket': 'Moderate'},
        'recommendation': {
          'immediate_action': 'Hold spraying.',
        },
        'status': {
          'pipeline': 'verified',
          'expert_review': 'verified',
          'mask_advisory': false,
        },
        'expert_review_data': {
          'decision': 'Override / Correct Findings',
          'corrected_disease': 'Alternaria Leaf Spot',
          'corrected_severity': 38.0,
          'farmer_guidance': 'This is early Alternaria, not Bacterial Blight. Apply Mancozeb 2g/L.',
          'status': 'verified',
        },
      };

      final pred = Prediction.fromJson(reviewedJson);
      expect(pred.id, 55);
      expect(pred.isVerified, isTrue);
      expect(pred.isMasked, isFalse);
      expect(pred.expertDecision, 'Override / Correct Findings');
      expect(pred.correctedDisease, 'Alternaria Leaf Spot');
      expect(pred.correctedSeverity, 38);
      expect(pred.expertGuidance, contains('Apply Mancozeb 2g/L'));
      expect(pred.expertReviewStatus, 'verified');
      expect(pred.localizedAudioText('en'), contains('Specialist verified advisory:'));
    });
  });
}

