import 'package:flutter/material.dart';
import '../../models/prediction.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class ResultDetailSheet extends StatefulWidget {
  const ResultDetailSheet({
    super.key,
    required this.prediction,
    required this.api,
    required this.onSpeak,
    required this.onFeedbackSubmitted,
  });

  final Prediction prediction;
  final ApiService api;
  final void Function(String text) onSpeak;
  final VoidCallback onFeedbackSubmitted;

  @override
  State<ResultDetailSheet> createState() => _ResultDetailSheetState();
}

class _ResultDetailSheetState extends State<ResultDetailSheet> {
  bool _submittingFeedback = false;
  bool _feedbackDone = false;
  final _noteCtrl = TextEditingController();

  @override
  void dispose() {
    _noteCtrl.dispose();
    super.dispose();
  }

  Future<void> _sendFeedback(bool correct) async {
    setState(() => _submittingFeedback = true);
    try {
      await widget.api.submitFeedback(widget.prediction.id, correct, _noteCtrl.text.trim());
      setState(() => _feedbackDone = true);
      widget.onFeedbackSubmitted();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Feedback submitted. Thank you!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Feedback error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _submittingFeedback = false);
    }
  }

  Future<void> _requestExpert() async {
    try {
      await widget.api.requestExpertReview(widget.prediction.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Expert review requested! Check Alerts for updates.')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to request expert review: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final pred = widget.prediction;
    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.85,
      maxChildSize: 0.95,
      minChildSize: 0.5,
      builder: (_, controller) => ListView(
        controller: controller,
        padding: const EdgeInsets.all(24),
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(color: Colors.grey.shade400, borderRadius: BorderRadius.circular(2)),
            ),
          ),
          const SizedBox(height: 18),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  '${pred.crop.toUpperCase()} DIAGNOSIS',
                  style: const TextStyle(letterSpacing: 1.5, color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 12),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              IconButton(
                onPressed: () => widget.onSpeak(pred.recommendation),
                icon: const Icon(Icons.volume_up_outlined, color: AppColors.primary),
                tooltip: 'Listen to advice',
              ),
            ],
          ),
          Text(pred.disease, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(8)),
                child: Text('${(pred.confidence * 100).round()}% AI Confidence', style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 12)),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(color: AppColors.warningBg, borderRadius: BorderRadius.circular(8)),
                child: Text('${pred.severity}% Severity', style: const TextStyle(color: AppColors.warning, fontWeight: FontWeight.bold, fontSize: 12)),
              ),
            ],
          ),
          const SizedBox(height: 24),
          // Immediate action & Treatment
          const Text('Actionable Recommendations', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: const Color(0xfff4f1e8), borderRadius: BorderRadius.circular(14)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (pred.immediateAction != null && pred.immediateAction!.isNotEmpty) ...[
                  const Text('Immediate Action:', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontSize: 13)),
                  const SizedBox(height: 4),
                  Text(pred.immediateAction!, style: const TextStyle(color: Color(0xff5d513f), height: 1.4)),
                  const SizedBox(height: 12),
                ],
                if (pred.treatment != null && pred.treatment!.isNotEmpty) ...[
                  const Text('Treatment Guidance:', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontSize: 13)),
                  const SizedBox(height: 4),
                  Text(pred.treatment!, style: const TextStyle(color: Color(0xff5d513f), height: 1.4)),
                  const SizedBox(height: 12),
                ],
                if (pred.prevention != null && pred.prevention!.isNotEmpty) ...[
                  const Text('Prevention Strategy:', style: TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontSize: 13)),
                  const SizedBox(height: 4),
                  Text(pred.prevention!, style: const TextStyle(color: Color(0xff5d513f), height: 1.4)),
                ],
              ],
            ),
          ),
          const SizedBox(height: 24),
          // Farmer Accuracy Feedback
          const Text('Was this diagnosis accurate?', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          if (_feedbackDone)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(8)),
              child: const Row(
                children: [
                  Icon(Icons.check_circle, color: AppColors.primary, size: 18),
                  SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Thank you for confirming your feedback!',
                      style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            )
          else ...[
            TextField(
              controller: _noteCtrl,
              decoration: const InputDecoration(
                hintText: 'Optional note for agronomy research...',
                border: OutlineInputBorder(),
                isDense: true,
              ),
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _submittingFeedback ? null : () => _sendFeedback(true),
                    icon: const Icon(Icons.thumb_up_outlined, size: 16, color: AppColors.primary),
                    label: const Text('Accurate', style: TextStyle(color: AppColors.primary)),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _submittingFeedback ? null : () => _sendFeedback(false),
                    icon: const Icon(Icons.thumb_down_outlined, size: 16, color: Colors.red),
                    label: const Text('Incorrect', style: TextStyle(color: Colors.red)),
                  ),
                ),
              ],
            ),
          ],
          const SizedBox(height: 24),
          // Expert Escalation
          OutlinedButton.icon(
            onPressed: _requestExpert,
            icon: const Icon(Icons.support_agent),
            label: const Text('Request Human Agronomist Review'),
            style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }
}

