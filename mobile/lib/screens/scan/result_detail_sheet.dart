import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../../models/prediction.dart';
import '../../providers/locale_provider.dart';
import '../../services/api_service.dart';
import '../../theme/app_theme.dart';

enum AudioPlaybackState { stopped, playing, paused }

class ResultDetailSheet extends StatefulWidget {
  const ResultDetailSheet({
    super.key,
    required this.prediction,
    required this.api,
    this.onSpeak,
    required this.onFeedbackSubmitted,
  });

  final Prediction prediction;
  final ApiService api;
  final void Function(String text)? onSpeak;
  final VoidCallback onFeedbackSubmitted;

  @override
  State<ResultDetailSheet> createState() => _ResultDetailSheetState();
}

class _ResultDetailSheetState extends State<ResultDetailSheet> {
  final FlutterTts _tts = FlutterTts();
  late Prediction _pred;
  AudioPlaybackState _playbackState = AudioPlaybackState.stopped;

  bool _submittingFeedback = false;
  bool _feedbackDone = false;
  bool _translating = false;
  final _noteCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _pred = widget.prediction;
    _initTts();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _checkAndTranslate();
  }

  void _initTts() {
    _tts.setStartHandler(() {
      if (mounted) setState(() => _playbackState = AudioPlaybackState.playing);
    });
    _tts.setCompletionHandler(() {
      if (mounted) setState(() => _playbackState = AudioPlaybackState.stopped);
    });
    _tts.setPauseHandler(() {
      if (mounted) setState(() => _playbackState = AudioPlaybackState.paused);
    });
    _tts.setContinueHandler(() {
      if (mounted) setState(() => _playbackState = AudioPlaybackState.playing);
    });
    _tts.setErrorHandler((msg) {
      if (mounted) setState(() => _playbackState = AudioPlaybackState.stopped);
    });
  }

  Future<void> _checkAndTranslate() async {
    final lang = context.loc.languageCode;
    if (lang == 'en') return;
    if (_pred.translations != null && _pred.translations![lang] != null) return;
    if (_translating) return;

    setState(() => _translating = true);
    try {
      final res = await widget.api.translatePrediction(_pred.id, lang);
      final translations = (res['translations'] as Map?)?.cast<String, dynamic>();
      if (translations != null && mounted) {
        setState(() {
          _pred = _pred.copyWithTranslations(translations);
        });
      }
    } catch (_) {
      // Fallback cleanly to English if network fails
    } finally {
      if (mounted) setState(() => _translating = false);
    }
  }

  @override
  void dispose() {
    _tts.stop();
    _noteCtrl.dispose();
    super.dispose();
  }

  Future<void> _togglePlayPause() async {
    final langCode = context.loc.languageCode;
    final text = _pred.localizedAudioText(
      langCode,
      localizedCropName: context.loc.crop(_pred.crop),
      localizedDiseaseName: context.loc.disease(_pred.disease),
    );

    if (_playbackState == AudioPlaybackState.playing) {
      await _tts.pause();
      if (mounted) setState(() => _playbackState = AudioPlaybackState.paused);
    } else if (_playbackState == AudioPlaybackState.paused) {
      await _tts.speak(text);
      if (mounted) setState(() => _playbackState = AudioPlaybackState.playing);
    } else {
      final ttsLang = langCode == 'hi' ? 'hi-IN' : (langCode == 'gu' ? 'gu-IN' : 'en-US');
      await _tts.setLanguage(ttsLang);
      await _tts.setSpeechRate(0.48);
      await _tts.speak(text);
      if (mounted) setState(() => _playbackState = AudioPlaybackState.playing);
    }
  }

  Future<void> _stopAudio() async {
    await _tts.stop();
    if (mounted) setState(() => _playbackState = AudioPlaybackState.stopped);
  }

  Future<void> _sendFeedback(bool correct) async {
    setState(() => _submittingFeedback = true);
    try {
      await widget.api.submitFeedback(_pred.id, correct, _noteCtrl.text.trim());
      setState(() => _feedbackDone = true);
      widget.onFeedbackSubmitted();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.tr('feedbackConfirmed'))),
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
      await widget.api.requestExpertReview(_pred.id);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.tr('expertRequested'))),
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
    final langCode = context.loc.languageCode;
    final translatedCrop = context.loc.crop(_pred.crop);
    final translatedDisease = context.loc.disease(_pred.disease);
    final severityLevel = context.loc.severityPercent(_pred.severity);

    final immAction = _pred.localizedImmediateAction(langCode);
    final treatment = _pred.localizedTreatment(langCode);
    final prevention = _pred.localizedPrevention(langCode);
    final monitoring = _pred.localizedMonitoring(langCode);
    final fallbackRec = _pred.localizedRecommendation(langCode);

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
                  '${translatedCrop.toUpperCase()} ${context.tr('cropDiagnosis')}',
                  style: const TextStyle(letterSpacing: 1.5, color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 12),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              IconButton(
                onPressed: _togglePlayPause,
                icon: Icon(
                  _playbackState == AudioPlaybackState.playing
                      ? Icons.pause_circle_filled
                      : (_playbackState == AudioPlaybackState.paused
                          ? Icons.play_circle_filled
                          : Icons.volume_up_outlined),
                  color: _playbackState == AudioPlaybackState.paused ? AppColors.warning : AppColors.primary,
                  size: 26,
                ),
                tooltip: _playbackState == AudioPlaybackState.playing
                    ? context.tr('pauseAudio')
                    : (_playbackState == AudioPlaybackState.paused ? context.tr('resumeAudio') : context.tr('listenComplete')),
              ),
            ],
          ),
          Text(translatedDisease, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(8)),
                child: Text(
                  '${(_pred.confidence * 100).round()}% ${context.tr('aiConfidence')}',
                  style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 12),
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                decoration: BoxDecoration(color: AppColors.warningBg, borderRadius: BorderRadius.circular(8)),
                child: Text(
                  '${_pred.severity}% $severityLevel',
                  style: const TextStyle(color: AppColors.warning, fontWeight: FontWeight.bold, fontSize: 12),
                ),
              ),
            ],
          ),

          if (_translating) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(8)),
              child: Row(
                children: [
                  const SizedBox(width: 14, height: 14, child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary)),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      context.tr('translatingAdvisory'),
                      style: const TextStyle(fontSize: 12, color: AppColors.primary, fontWeight: FontWeight.w600),
                    ),
                  ),
                ],
              ),
            ),
          ],

          const SizedBox(height: 20),

          // Interactive Full Audio Player Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: _playbackState == AudioPlaybackState.playing
                  ? AppColors.primaryLight
                  : (_playbackState == AudioPlaybackState.paused ? AppColors.warningBg : const Color(0xfff4f1e8)),
              borderRadius: BorderRadius.circular(14),
              border: Border.all(
                color: _playbackState == AudioPlaybackState.playing
                    ? AppColors.primaryBorder
                    : (_playbackState == AudioPlaybackState.paused ? AppColors.warning : AppColors.cardBorder),
              ),
            ),
            child: Row(
              children: [
                IconButton.filled(
                  onPressed: _togglePlayPause,
                  style: IconButton.styleFrom(
                    backgroundColor: _playbackState == AudioPlaybackState.playing
                        ? AppColors.primary
                        : (_playbackState == AudioPlaybackState.paused ? AppColors.warning : AppColors.primary),
                    padding: const EdgeInsets.all(10),
                  ),
                  icon: Icon(
                    _playbackState == AudioPlaybackState.playing
                        ? Icons.pause
                        : Icons.play_arrow,
                    color: Colors.white,
                    size: 22,
                  ),
                  tooltip: _playbackState == AudioPlaybackState.playing
                      ? context.tr('pauseAudio')
                      : (_playbackState == AudioPlaybackState.paused ? context.tr('resumeAudio') : context.tr('playAudio')),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        _playbackState == AudioPlaybackState.playing
                            ? context.tr('playingFullAudio')
                            : (_playbackState == AudioPlaybackState.paused
                                ? context.tr('audioPaused')
                                : context.tr('listenComplete')),
                        style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 2),
                      Text(
                        context.tr('audioAdviceSubtitle'),
                        style: const TextStyle(color: AppColors.textMuted, fontSize: 11),
                        maxLines: 1,
                        overflow: TextOverflow.ellipsis,
                      ),
                    ],
                  ),
                ),
                if (_playbackState != AudioPlaybackState.stopped)
                  IconButton(
                    onPressed: _stopAudio,
                    icon: const Icon(Icons.stop_circle_outlined, color: Colors.grey),
                    tooltip: context.tr('stopAudio'),
                  ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // Immediate action & Treatment
          Text(
            context.tr('actionableRecommendations'),
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(color: const Color(0xfff4f1e8), borderRadius: BorderRadius.circular(14)),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (immAction != null && immAction.isNotEmpty) ...[
                  Text(context.tr('immediateAction'), style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontSize: 13)),
                  const SizedBox(height: 4),
                  Text(immAction, style: const TextStyle(color: Color(0xff5d513f), height: 1.4)),
                  const SizedBox(height: 12),
                ],
                if (treatment != null && treatment.isNotEmpty) ...[
                  Text(context.tr('treatmentGuidance'), style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontSize: 13)),
                  const SizedBox(height: 4),
                  Text(treatment, style: const TextStyle(color: Color(0xff5d513f), height: 1.4)),
                  const SizedBox(height: 12),
                ],
                if (prevention != null && prevention.isNotEmpty) ...[
                  Text(context.tr('preventionStrategy'), style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontSize: 13)),
                  const SizedBox(height: 4),
                  Text(prevention, style: const TextStyle(color: Color(0xff5d513f), height: 1.4)),
                  const SizedBox(height: 12),
                ],
                if (monitoring != null && monitoring.isNotEmpty) ...[
                  Text(context.tr('monitoringPlan'), style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary, fontSize: 13)),
                  const SizedBox(height: 4),
                  Text(monitoring, style: const TextStyle(color: Color(0xff5d513f), height: 1.4)),
                  const SizedBox(height: 12),
                ],
                if (immAction == null && treatment == null && prevention == null) ...[
                  Text(fallbackRec, style: const TextStyle(color: Color(0xff5d513f), height: 1.4)),
                ],
              ],
            ),
          ),
          const SizedBox(height: 24),

          // Farmer Accuracy Feedback
          Text(context.tr('wasDiagnosisAccurate'), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
          const SizedBox(height: 10),
          if (_feedbackDone)
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: AppColors.primaryLight, borderRadius: BorderRadius.circular(8)),
              child: Row(
                children: [
                  const Icon(Icons.check_circle, color: AppColors.primary, size: 18),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      context.tr('feedbackConfirmed'),
                      style: const TextStyle(color: AppColors.primary, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            )
          else ...[
            TextField(
              controller: _noteCtrl,
              decoration: InputDecoration(
                hintText: context.tr('optionalNoteHint'),
                border: const OutlineInputBorder(),
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
                    label: Text(context.tr('accurateBtn'), style: const TextStyle(color: AppColors.primary)),
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: OutlinedButton.icon(
                    onPressed: _submittingFeedback ? null : () => _sendFeedback(false),
                    icon: const Icon(Icons.thumb_down_outlined, size: 16, color: Colors.red),
                    label: Text(context.tr('incorrectBtn'), style: const TextStyle(color: Colors.red)),
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
            label: Text(context.tr('requestExpertReview')),
            style: OutlinedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 14)),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }
}
