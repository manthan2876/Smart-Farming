import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../widgets/camera_guide_overlay.dart';

class CameraScreen extends StatelessWidget {
  const CameraScreen({super.key, required this.onCaptured});
  final ValueChanged<File> onCaptured;

  Future<void> _capture() async {
    final picked = await ImagePicker().pickImage(source: ImageSource.camera, imageQuality: 84, maxWidth: 1600);
    if (picked != null) onCaptured(File(picked.path));
  }

  @override
  Widget build(BuildContext context) => Scaffold(backgroundColor: const Color(0xff20312b), body: Stack(children: [const CameraGuideOverlay(), Align(alignment: Alignment.bottomCenter, child: Padding(padding: const EdgeInsets.all(28), child: FloatingActionButton.large(backgroundColor: const Color(0xffffd681), foregroundColor: const Color(0xff20312b), onPressed: _capture, child: const Icon(Icons.camera_alt))))]));
}
