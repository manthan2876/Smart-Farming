import 'package:flutter/material.dart';
import '../../models/prediction.dart';
import '../../providers/locale_provider.dart';
import '../../services/api_service.dart';
import '../../services/tts_service.dart';
import '../../theme/app_theme.dart';

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
  final TtsService _ttsService = TtsService.instance;
  late Prediction _pred;

  bool _submittingFeedback = false;
  bool _feedbackDone = false;
  bool _translating = false;
  final _noteCtrl = TextEditingController();

  @override
  void initState() {
    super.initState();
    _pred = widget.prediction;
    _ttsService.addListener(_onTtsStateChange);
  }

  void _onTtsStateChange() {
    if (mounted) setState(() {});
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _checkAndTranslate();
  }

  Future<void> _checkAndTranslate() async {
    final lang = context.loc.languageCode;
    if (lang == 'en') return;
    if (_pred.id <= 0) return;
    if (_pred.translations != null && _pred.translations![lang] != null) return;
    if (_translating) return;

    setState(() => _translating = true);
    try {
      final res = await widget.api.translatePrediction(_pred.id, lang);
      final rawTranslations = (res['translations'] as Map?)?.cast<String, dynamic>();
      final rec = res['recommendation'];
      final Map<String, dynamic> merged = rawTranslations != null
          ? Map<String, dynamic>.from(rawTranslations)
          : (rec != null ? {lang: rec} : {});

      if (merged.isNotEmpty && mounted) {
        setState(() {
          _pred = _pred.copyWithTranslations(merged);
        });
      }
    } catch (_) {
      // Fallback cleanly
    } finally {
      if (mounted) setState(() => _translating = false);
    }
  }

  @override
  void dispose() {
    _ttsService.removeListener(_onTtsStateChange);
    if (_ttsService.isItemPlaying('pred_${_pred.id}')) {
      _ttsService.stop();
    }
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

    await _ttsService.toggle(
      id: 'pred_${_pred.id}',
      text: text,
      langCode: langCode,
      api: widget.api,
    );
  }

  Future<void> _stopAudio() async {
    await _ttsService.stop();
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
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    onPressed: () => showLanguageSelectionSheet(context),
                    icon: const Icon(Icons.language, color: AppColors.primary, size: 24),
                    tooltip: context.tr('selectLanguage'),
                  ),
                  Builder(
                    builder: (_) {
                      final isPlaying = _ttsService.isItemPlaying('pred_${_pred.id}');
                      final isLoading = _ttsService.isItemLoading('pred_${_pred.id}');
                      if (isLoading) {
                        return const Padding(
                          padding: EdgeInsets.all(12),
                          child: SizedBox(
                            width: 20,
                            height: 20,
                            child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.primary),
                          ),
                        );
                      }
                      return IconButton(
                        onPressed: _togglePlayPause,
                        icon: Icon(
                          isPlaying ? Icons.stop_circle_outlined : Icons.volume_up_outlined,
                          color: isPlaying ? AppColors.warning : AppColors.primary,
                          size: 26,
                        ),
                        tooltip: isPlaying ? context.tr('pauseAudio') : context.tr('listenComplete'),
                      );
                    },
                  ),
                ],
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
          Builder(
            builder: (_) {
              final isPlaying = _ttsService.isItemPlaying('pred_${_pred.id}');
              final isLoading = _ttsService.isItemLoading('pred_${_pred.id}');
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: isPlaying ? AppColors.primaryLight : const Color(0xfff4f1e8),
                  borderRadius: BorderRadius.circular(14),
                  border: Border.all(
                    color: isPlaying ? AppColors.primaryBorder : AppColors.cardBorder,
                  ),
                ),
                child: Row(
                  children: [
                    IconButton.filled(
                      onPressed: _togglePlayPause,
                      style: IconButton.styleFrom(
                        backgroundColor: isPlaying ? AppColors.warning : AppColors.primary,
                        padding: const EdgeInsets.all(10),
                      ),
                      icon: isLoading
                          ? const SizedBox(
                              width: 22,
                              height: 22,
                              child: CircularProgressIndicator(strokeWidth: 2.2, color: Colors.white),
                            )
                          : Icon(
                              isPlaying ? Icons.stop : Icons.play_arrow,
                              color: Colors.white,
                              size: 22,
                            ),
                      tooltip: isPlaying ? context.tr('pauseAudio') : context.tr('playAudio'),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isLoading
                                ? context.tr('loading')
                                : (isPlaying
                                    ? context.tr('playingFullAudio')
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
                    if (isPlaying)
                      IconButton(
                        onPressed: _stopAudio,
                        icon: const Icon(Icons.stop_circle_outlined, color: Colors.grey),
                        tooltip: context.tr('stopAudio'),
                      ),
                  ],
                ),
              );
            },
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
