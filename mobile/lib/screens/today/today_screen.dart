import 'dart:typed_data';
import 'package:flutter/material.dart';
import '../../models/prediction.dart';
import '../../theme/app_theme.dart';

class TodayScreen extends StatelessWidget {
  const TodayScreen({
    super.key,
    required this.userProfile,
    required this.weather,
    required this.pendingCount,
    required this.latestPrediction,
    required this.photoBytes,
    required this.onScanLeaf,
    required this.onSelectPrediction,
    required this.onSeeTrail,
    required this.onLogout,
  });

  final Map<String, dynamic> userProfile;
  final Map<String, dynamic>? weather;
  final int pendingCount;
  final Prediction? latestPrediction;
  final Uint8List? photoBytes;
  final VoidCallback onScanLeaf;
  final ValueChanged<Prediction> onSelectPrediction;
  final VoidCallback onSeeTrail;
  final VoidCallback onLogout;

  Widget _stat(String value, String label) => Expanded(
        child: Container(
          margin: const EdgeInsets.only(right: 7),
          padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
          decoration: BoxDecoration(
            color: AppColors.cardBg,
            border: Border.all(color: AppColors.cardBorder),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                value,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              const SizedBox(height: 3),
              Text(
                label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: AppColors.textMuted, fontSize: 10),
              ),
            ],
          ),
        ),
      );

  Widget _readingCard() {
    if (latestPrediction == null) {
      return Card(
        elevation: 0,
        color: AppColors.cardBg,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
          side: const BorderSide(color: AppColors.cardBorder),
        ),
        child: const Padding(
          padding: EdgeInsets.all(24),
          child: Center(
            child: Text(
              'No scans yet. Capture a leaf photo to diagnose crop health.',
              style: TextStyle(color: AppColors.textMuted),
            ),
          ),
        ),
      );
    }

    return InkWell(
      onTap: () => onSelectPrediction(latestPrediction!),
      borderRadius: BorderRadius.circular(18),
      child: Card(
        elevation: 0,
        color: AppColors.cardBg,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(18),
          side: const BorderSide(color: AppColors.cardBorder),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Row(
            children: [
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: photoBytes != null
                    ? Image.memory(photoBytes!, width: 72, height: 72, fit: BoxFit.cover)
                    : Container(
                        width: 72,
                        height: 72,
                        color: const Color(0xffdbe8d8),
                        child: const Icon(Icons.eco_outlined, size: 32, color: AppColors.primary),
                      ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      latestPrediction!.crop.toUpperCase(),
                      style: const TextStyle(
                        letterSpacing: 1.4,
                        color: AppColors.textSubtle,
                        fontSize: 9,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      latestPrediction!.disease,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                    ),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 4,
                      children: [
                        Text(
                          '${(latestPrediction!.confidence * 100).round()}% confidence',
                          style: const TextStyle(
                            color: AppColors.primary,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        Text(
                          '${latestPrediction!.severity}% affected',
                          style: const TextStyle(
                            color: AppColors.warning,
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final temp = weather?['temperature_celsius'] != null ? '${weather!['temperature_celsius']}°C' : '--';
    final cond = weather?['condition']?.toString() ?? 'Telemetry ready';
    final hum = weather?['humidity_percent'] != null ? '${weather!['humidity_percent']}%' : '--';
    final farmLoc = userProfile['location']?.toString().toUpperCase() ?? 'MY FARM';

    return ListView(
      padding: const EdgeInsets.fromLTRB(22, 22, 22, 30),
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'FIELDNOTE · FARMER',
                    style: TextStyle(
                      letterSpacing: 2,
                      fontWeight: FontWeight.bold,
                      fontSize: 12,
                      color: AppColors.primary,
                    ),
                  ),
                  const SizedBox(height: 5),
                  Text(
                    'Welcome, ${userProfile['name'] ?? 'Farmer'}',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w600),
                  ),
                ],
              ),
            ),
            IconButton(
              onPressed: onLogout,
              icon: const Icon(Icons.logout, color: Colors.grey),
              tooltip: 'Sign Out',
            ),
          ],
        ),
        const SizedBox(height: 22),
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: AppColors.primary,
            borderRadius: BorderRadius.circular(22),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                farmLoc,
                style: const TextStyle(
                  color: AppColors.primaryBorder,
                  letterSpacing: 1.5,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              const Text(
                'A clear leaf photo\nstarts a better decision.',
                style: TextStyle(
                  color: Colors.white,
                  fontSize: 25,
                  height: 1.1,
                  fontWeight: FontWeight.w500,
                ),
              ),
              const SizedBox(height: 18),
              FilledButton.icon(
                onPressed: onScanLeaf,
                icon: const Icon(Icons.camera_alt_outlined),
                label: const Text('Scan a leaf'),
                style: FilledButton.styleFrom(
                  backgroundColor: AppColors.accent,
                  foregroundColor: AppColors.textPrimary,
                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                ),
              ),
            ],
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            _stat(temp, cond),
            _stat(hum, 'humidity'),
            _stat('$pendingCount', 'pending sync'),
          ],
        ),
        const SizedBox(height: 25),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Expanded(
              child: Text(
                'Latest reading',
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
              ),
            ),
            TextButton(
              onPressed: onSeeTrail,
              child: const Text('See trail'),
            ),
          ],
        ),
        _readingCard(),
      ],
    );
  }
}

