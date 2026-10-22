import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../providers/locale_provider.dart';
import '../services/image_compressor.dart';
import '../widgets/camera_guide_overlay.dart';

class CameraScreen extends StatefulWidget {
  const CameraScreen({super.key, required this.onCaptured});
  final void Function(Uint8List bytes, String name) onCaptured;

  @override
  State<CameraScreen> createState() => _CameraScreenState();
}

class _CameraScreenState extends State<CameraScreen> {
  final _picker = ImagePicker();
  String? _qualityWarning;

  Future<void> _capture(ImageSource source) async {
    try {
      final picked = await _picker.pickImage(
        source: source,
        imageQuality: ImageCompressor.targetQuality,
        maxWidth: ImageCompressor.targetMaxDimension.toDouble(),
        maxHeight: ImageCompressor.targetMaxDimension.toDouble(),
      );
      if (picked != null) {
        final bytes = await picked.readAsBytes();
        final quality = ImageCompressor.evaluateQuality(bytes);
        if (!quality.isValid) {
          setState(() => _qualityWarning = quality.reason);
          return;
        }
        widget.onCaptured(bytes, picked.name.isNotEmpty ? picked.name : 'leaf.jpg');
      }
    } catch (e) {
      setState(() => _qualityWarning = 'Could not access camera: $e');
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: const Color(0xff20312b),
        body: Stack(
          children: [
            CameraGuideOverlay(
              showQualityWarning: _qualityWarning != null,
              warningText: _qualityWarning,
            ),
            Align(
              alignment: Alignment.bottomCenter,
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 28),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    // Gallery Picker button
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white12,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white24),
                      ),
                      child: IconButton(
                        iconSize: 28,
                        color: Colors.white,
                        icon: const Icon(Icons.photo_library_outlined),
                        onPressed: () => _capture(ImageSource.gallery),
                        tooltip: context.tr('cameraSelectGallery'),
                      ),
                    ),

                    // Primary Camera Shutter (Large Touch Target)
                    FloatingActionButton.large(
                      heroTag: 'camera_capture_btn',
                      backgroundColor: const Color(0xffffd681),
                      foregroundColor: const Color(0xff20312b),
                      elevation: 4,
                      onPressed: () => _capture(ImageSource.camera),
                      child: const Icon(Icons.camera_alt, size: 36),
                    ),

                    // Flash / Guidance Reset
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white12,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white24),
                      ),
                      child: IconButton(
                        iconSize: 28,
                        color: Colors.white,
                        icon: const Icon(Icons.refresh_rounded),
                        onPressed: () => setState(() => _qualityWarning = null),
                        tooltip: context.tr('cameraResetGuidance'),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      );
}
