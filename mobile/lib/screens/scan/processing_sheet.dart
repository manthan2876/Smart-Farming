import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import '../../models/prediction.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

class ProcessingSheet extends StatefulWidget {
  const ProcessingSheet({
    super.key,
    required this.predictionId,
    this.photoBytes,
    required this.api,
    required this.onComplete,
    required this.onRescan,
  });

  final int predictionId;
  final Uint8List? photoBytes;
  final ApiService api;
  final void Function(Prediction prediction) onComplete;
  final VoidCallback onRescan;

  @override
  State<ProcessingSheet> createState() => _ProcessingSheetState();
}

class _ProcessingSheetState extends State<ProcessingSheet> {
  final bool _preprocDone = true;
  bool _cropDone = false;
  bool _diseaseDone = false;
  bool _pestDone = false;
  bool _advisoryDone = false;
  bool _pipelineDone = false;

  Map<String, dynamic>? _detectedCrop;
  Map<String, dynamic>? _detectedDisease;
  List<String> _detectedPests = [];
  String _liveMessage = '';
  String? _failure;

  WebSocketChannel? _wsChannel;
  StreamSubscription? _wsSubscription;
  Timer? _pollTimer;
  bool _finished = false;

  @override
  void initState() {
    super.initState();
    _connectWs();
    _pollTimer = Timer.periodic(const Duration(milliseconds: 1500), (_) => _poll());
    _poll();
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    _wsSubscription?.cancel();
    _wsChannel?.sink.close();
    super.dispose();
  }

  void _connectWs() {
    try {
      final wsUrl = widget.api.getWebSocketUrl('/ws/predictions/${widget.predictionId}');
      _wsChannel = WebSocketChannel.connect(Uri.parse(wsUrl));
      _wsSubscription = _wsChannel!.stream.listen(
        (message) {
          if (!mounted) return;
          try {
            final data = jsonDecode(message.toString()) as Map<String, dynamic>;
            _handleEvent(data);
          } catch (_) {}
        },
        onError: (_) {},
        onDone: () {},
      );
    } catch (_) {}
  }

  void _handleEvent(Map<String, dynamic> data) {
    final stage = data['stage']?.toString() ?? '';
    final status = data['status']?.toString() ?? '';
    final msg = data['message']?.toString() ?? '';
    final payload = (data['data'] as Map?)?.cast<String, dynamic>() ?? {};

    if (stage == 'failed' || status == 'failed') {
      setState(() {
        _failure = data['error']?.toString() ?? (msg.isNotEmpty ? msg : 'Analysis failed. Please try again with a clearer leaf photo.');
      });
      _pollTimer?.cancel();
      return;
    }

    if (status == 'processing') {
      if (msg.isNotEmpty) setState(() => _liveMessage = msg);
      return;
    }

    if (payload['crop'] is Map && payload['crop']['label'] != null) {
      _detectedCrop = (payload['crop'] as Map).cast<String, dynamic>();
      _cropDone = true;
    }
    if (payload['disease'] is Map && payload['disease']['label'] != null) {
      _detectedDisease = (payload['disease'] as Map).cast<String, dynamic>();
      _diseaseDone = true;
      _cropDone = true;
    }
    if (payload['pests'] is List && (payload['pests'] as List).isNotEmpty) {
      _detectedPests = (payload['pests'] as List)
          .map((p) => (p as Map)['label']?.toString() ?? '')
          .where((s) => s.isNotEmpty)
          .toList();
      _pestDone = true;
      _diseaseDone = true;
      _cropDone = true;
    }

    final isCompleted = status == 'completed';
    if (stage == 'crop_identification' && isCompleted) {
      _cropDone = true;
    } else if (stage == 'disease_classification' && isCompleted) {
      _cropDone = true;
      _diseaseDone = true;
    } else if (stage == 'pest_detection' && isCompleted) {
      _cropDone = true;
      _diseaseDone = true;
      _pestDone = true;
    } else if ((stage == 'recommendation' || stage == 'llm_advisory') && isCompleted) {
      _advisoryDone = true;
    } else if (stage == 'completed' && isCompleted) {
      _completePipeline();
    }
    if (mounted) setState(() {});
  }

  Future<void> _poll() async {
    if (_finished) return;
    try {
      final raw = await widget.api.getPredictionRaw(widget.predictionId);
      if (!mounted) return;

      final target = (raw['follow_up'] as Map?)?.cast<String, dynamic>() ?? raw;
      final st = target['status'];

      if (st == 'failed' || (st is Map && st['pipeline'] == 'failed')) {
        setState(() {
          _failure = target['error']?.toString() ?? 'Analysis failed. Please try again with a clearer leaf photo.';
        });
        _pollTimer?.cancel();
        return;
      }

      if (target['crop'] is Map && target['crop']['label'] != null) {
        _detectedCrop = (target['crop'] as Map).cast<String, dynamic>();
        _cropDone = true;
      }
      if (target['disease'] is Map && target['disease']['label'] != null) {
        _detectedDisease = (target['disease'] as Map).cast<String, dynamic>();
        _diseaseDone = true;
        _cropDone = true;
      }
      if (target['pests'] is List && (target['pests'] as List).isNotEmpty) {
        _detectedPests = (target['pests'] as List)
            .map((p) => (p as Map)['label']?.toString() ?? '')
            .where((s) => s.isNotEmpty)
            .toList();
        _pestDone = true;
      }

      final pipeStatus = st is Map ? st['pipeline']?.toString() : st?.toString();
      if (st is Map) {
        if (st['crop_identification'] == 'completed') _cropDone = true;
        if (st['disease_classification'] == 'completed') _diseaseDone = true;
        if (st['pest_detection'] == 'completed') _pestDone = true;
        if (st['recommendation'] == 'completed') _advisoryDone = true;
      }

      if (pipeStatus == 'completed' || pipeStatus == 'ready') {
        _completePipeline();
      } else {
        setState(() {});
      }
    } catch (_) {}
  }

  Future<void> _completePipeline() async {
    if (_finished) return;
    _finished = true;
    _pollTimer?.cancel();
    setState(() {
      _cropDone = true;
      _diseaseDone = true;
      _pestDone = true;
      _advisoryDone = true;
      _pipelineDone = true;
      _liveMessage = '';
    });

    try {
      final finalPred = await widget.api.getPrediction(widget.predictionId);
      await Future.delayed(const Duration(milliseconds: 900));
      if (mounted) {
        widget.onComplete(finalPred);
      }
    } catch (_) {}
  }

  Widget _stageRow({
    required int number,
    required String title,
    required bool isUnlocked,
    required bool isDone,
    required Widget? activeIndicator,
    required Widget detail,
  }) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 10),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 38,
            height: 38,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isDone
                  ? AppColors.primary
                  : isUnlocked
                      ? AppColors.warningBg
                      : const Color(0xffe8e6dc),
            ),
            child: Center(
              child: isDone
                  ? const Icon(Icons.check, color: Colors.white, size: 20)
                  : activeIndicator ??
                      Text(
                        '$number',
                        style: TextStyle(
                          fontWeight: FontWeight.bold,
                          color: isUnlocked ? AppColors.warningText : Colors.grey,
                        ),
                      ),
            ),
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  '$number. $title',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                    color: isUnlocked ? AppColors.textPrimary : Colors.grey,
                  ),
                ),
                const SizedBox(height: 3),
                detail,
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final cropLabel = _detectedCrop?['label']?.toString();
    final cropConf = (_detectedCrop?['confidence'] as num?)?.toDouble();
    final cropStr = cropLabel != null
        ? '$cropLabel${cropConf != null ? ' (${(cropConf * 100).round()}%)' : ''}'
        : (_cropDone ? 'Identified' : 'Scanning species...');

    final diseaseLabel = _detectedDisease?['label']?.toString();
    final diseaseConf = (_detectedDisease?['confidence'] as num?)?.toDouble();
    final diseaseStr = diseaseLabel != null
        ? '$diseaseLabel${diseaseConf != null ? ' (${(diseaseConf * 100).round()}%)' : ''}'
        : (_diseaseDone ? 'Identified' : 'Analyzing pathology...');

    final pestStr = _detectedPests.isNotEmpty
        ? _detectedPests.join(', ')
        : (_pestDone ? 'No Pests Detected' : 'Scanning for insects...');

    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.88,
      maxChildSize: 0.95,
      minChildSize: 0.5,
      builder: (_, scrollCtrl) => ListView(
        controller: scrollCtrl,
        padding: const EdgeInsets.all(22),
        children: [
          Center(
            child: Container(
              width: 44,
              height: 4,
              decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2)),
            ),
          ),
          const SizedBox(height: 16),

          if (widget.photoBytes != null)
            ClipRRect(
              borderRadius: BorderRadius.circular(16),
              child: Image.memory(widget.photoBytes!, height: 140, width: double.infinity, fit: BoxFit.cover),
            ),
          const SizedBox(height: 18),

          if (_failure != null) ...[
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: const Color(0xffffebee),
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: Colors.red.shade200),
              ),
              child: Column(
                children: [
                  const Icon(Icons.error_outline, color: Colors.red, size: 48),
                  const SizedBox(height: 12),
                  const Text('Analysis Rejection / Failed', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: Color(0xffc62828))),
                  const SizedBox(height: 6),
                  Text(_failure!, textAlign: TextAlign.center, style: const TextStyle(color: Color(0xff5d513f), height: 1.4, fontSize: 13)),
                  const SizedBox(height: 18),
                  FilledButton.icon(
                    onPressed: widget.onRescan,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Try Again / Re-scan'),
                    style: FilledButton.styleFrom(backgroundColor: AppColors.primary),
                  ),
                ],
              ),
            ),
          ] else ...[
            Column(
              children: [
                if (!_pipelineDone)
                  const SizedBox(
                    width: 32,
                    height: 32,
                    child: CircularProgressIndicator(strokeWidth: 3, color: AppColors.primary),
                  )
                else
                  const Icon(Icons.check_circle, size: 40, color: AppColors.primary),
                const SizedBox(height: 12),
                Text(
                  _pipelineDone ? 'Diagnostic Pipeline Complete' : 'Running AI Pipeline',
                  style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                ),
                const SizedBox(height: 4),
                const Text(
                  'Analyzing your crop and generating diagnostics in real-time...',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: AppColors.textMuted, fontSize: 13),
                ),
                if (_liveMessage.isNotEmpty && !_pipelineDone) ...[
                  const SizedBox(height: 10),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(8)),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.bolt, size: 16, color: AppColors.primary),
                        const SizedBox(width: 6),
                        Flexible(
                          child: Text(
                            _liveMessage,
                            style: const TextStyle(color: AppColors.primary, fontSize: 12, fontWeight: FontWeight.bold),
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ],
            ),
            const SizedBox(height: 24),

            // 5 stages
            _stageRow(
              number: 1,
              title: 'Image Preprocessing',
              isUnlocked: true,
              isDone: _preprocDone,
              activeIndicator: null,
              detail: const Text('Verified leaf presence and optical clarity.', style: TextStyle(color: AppColors.textMuted, fontSize: 13)),
            ),
            _stageRow(
              number: 2,
              title: 'Crop Identification',
              isUnlocked: true,
              isDone: _cropDone,
              activeIndicator: const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xff866b47))),
              detail: _cropDone
                  ? Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(6)),
                      child: Text('Detected: $cropStr', style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 12)),
                    )
                  : const Text('Scanning crop species...', style: TextStyle(color: AppColors.textMuted, fontSize: 13)),
            ),
            _stageRow(
              number: 3,
              title: 'Disease Classification',
              isUnlocked: _cropDone || _diseaseDone,
              isDone: _diseaseDone,
              activeIndicator: _cropDone ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xff866b47))) : null,
              detail: _diseaseDone
                  ? Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(6)),
                      child: Text('Identified: $diseaseStr', style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 12)),
                    )
                  : Text(_cropDone ? 'Analyzing foliar pathology...' : 'Waiting for crop identification...', style: const TextStyle(color: AppColors.textMuted, fontSize: 13)),
            ),
            _stageRow(
              number: 4,
              title: 'Pest & Parasite Detection',
              isUnlocked: _diseaseDone || _pestDone,
              isDone: _pestDone,
              activeIndicator: _diseaseDone ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2, color: Color(0xff866b47))) : null,
              detail: _pestDone
                  ? Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(6)),
                      child: Text('Result: $pestStr', style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 12)),
                    )
                  : Text(_diseaseDone ? 'Scanning for insect symptoms...' : 'Waiting for disease classification...', style: const TextStyle(color: AppColors.textMuted, fontSize: 13)),
            ),
            _stageRow(
              number: 5,
              title: 'Advisory Generation',
              isUnlocked: _pestDone || _advisoryDone,
              isDone: _advisoryDone,
              activeIndicator: _pestDone ? const Icon(Icons.auto_awesome, size: 18, color: Color(0xff866b47)) : null,
              detail: _advisoryDone
                  ? Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(6)),
                      child: const Text('Advisory Ready.', style: TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 12)),
                    )
                  : Text(_pestDone ? 'Synthesizing expert recommendations...' : 'Waiting for pest detection...', style: const TextStyle(color: AppColors.textMuted, fontSize: 13)),
            ),
          ],
        ],
      ),
    );
  }
}

