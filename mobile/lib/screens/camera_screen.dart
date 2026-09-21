import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../widgets/camera_guide_overlay.dart';

class CameraScreen extends StatelessWidget {
  const CameraScreen({super.key, required this.onCaptured});
  final void Function(Uint8List bytes, String name) onCaptured;

  Future<void> _capture() async {
    final picked = await ImagePicker().pickImage(source: ImageSource.camera, imageQuality: 84, maxWidth: 1600);
    if (picked != null) {
      final bytes = await picked.readAsBytes();
      onCaptured(bytes, picked.name);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
        backgroundColor: const Color(0xff20312b),
        body: Stack(
          children: [
            const CameraGuideOverlay(),
            Align(
              alignment: Alignment.bottomCenter,
              child: Padding(
                padding: const EdgeInsets.all(28),
                child: FloatingActionButton.large(
                  backgroundColor: const Color(0xffffd681),
                  foregroundColor: const Color(0xff20312b),
                  onPressed: _capture,
                  child: const Icon(Icons.camera_alt),
                ),
              ),
            ),
          ],
        ),
      );
}
