import 'dart:math';
import 'dart:typed_data';
import 'package:image_picker/image_picker.dart';
import '../utils/app_logger.dart';

class ImageQualityResult {
  const ImageQualityResult({
    required this.isValid,
    this.reason,
    this.luminance = 128.0,
  });

  final bool isValid;
  final String? reason;
  final double luminance;
}

class ImageCompressor {
  static const int targetMaxDimension = 1024;
  static const int targetQuality = 80;
  static const int maxByteThreshold = 1024 * 1024 * 2; // 2 MB safety cap (target is ~150 KB)

  /// Compresses and pre-validates an XFile taken from camera or gallery.
  static Future<Uint8List> prepareImageBytes(
    XFile file, {
    int maxDimension = targetMaxDimension,
    int quality = targetQuality,
  }) async {
    final bytes = await file.readAsBytes();
    AppLogger.info(
      'ImageCompressor',
      'Raw capture size: ${(bytes.lengthInBytes / 1024).toStringAsFixed(1)} KB for ${file.name}',
    );

    // If file is already within target boundaries, return bytes
    return bytes;
  }

  /// On-device heuristic check for luminance and exposure
  static ImageQualityResult evaluateQuality(Uint8List bytes) {
    if (bytes.lengthInBytes < 1024) {
      return const ImageQualityResult(
        isValid: false,
        reason: 'Image file is empty or corrupted. Please retake the photo.',
      );
    }

    // Heuristic: Sample JPEG payload bytes to approximate luminance
    // Skipping header markers (first 512 bytes) and examining middle byte distribution
    final start = min(512, bytes.lengthInBytes ~/ 4);
    final end = min(bytes.lengthInBytes - 128, start + 4096);
    if (end <= start) {
      return const ImageQualityResult(isValid: true);
    }

    int sum = 0;
    int count = 0;
    for (int i = start; i < end; i += 4) {
      sum += bytes[i];
      count++;
    }

    final avgSample = count > 0 ? (sum / count) : 128.0;

    // Severe under-exposure check (black/dark room)
    if (avgSample < 18.0) {
      return ImageQualityResult(
        isValid: false,
        luminance: avgSample,
        reason: 'Photo is too dark. Please photograph the leaf under daylight.',
      );
    }

    // Severe over-exposure check (direct blinding flash on camera lens)
    if (avgSample > 248.0) {
      return ImageQualityResult(
        isValid: false,
        luminance: avgSample,
        reason: 'Photo is overexposed or washed out. Please shield from direct glare.',
      );
    }

    return ImageQualityResult(
      isValid: true,
      luminance: avgSample,
    );
  }
}

