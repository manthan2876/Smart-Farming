import 'package:flutter/material.dart';

class CameraGuideOverlay extends StatelessWidget {
  const CameraGuideOverlay({super.key});

  @override
  Widget build(BuildContext context) => IgnorePointer(child: CustomPaint(painter: _GuidePainter(), child: const SizedBox.expand()));
}

class _GuidePainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = const Color(0xffffd681)..style = PaintingStyle.stroke..strokeWidth = 2;
    final rect = Rect.fromCenter(center: size.center(Offset.zero), width: size.width * .74, height: size.height * .58);
    canvas.drawRRect(RRect.fromRectAndRadius(rect, const Radius.circular(26)), paint);
  }
  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
