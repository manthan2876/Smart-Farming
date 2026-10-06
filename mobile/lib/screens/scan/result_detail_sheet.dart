import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:image_picker/image_picker.dart';
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
  bool _isRescanning = false;
  int _visualTab = 0; // 0 = Original, 1 = GradCAM
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
      setState(() {
        _pred = _pred.copyWith(expertReviewStatus: 'pending');
      });
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

  Future<void> _handleRescan(ImageSource source) async {
    final picker = ImagePicker();
    try {
      final picked = await picker.pickImage(source: source, imageQuality: 85, maxWidth: 1600);
      if (picked == null) return;
      setState(() => _isRescanning = true);
      final bytes = await picked.readAsBytes();
      final res = await widget.api.rescanBytes(_pred.id, bytes, picked.name);
      final updated = Prediction.fromJson(res);
      setState(() {
        _pred = updated;
        _visualTab = 1; // switch to heatmap view
      });
      widget.onFeedbackSubmitted();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Follow-up scan completed and updated!')),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Rescan error: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isRescanning = false);
    }
  }

  void _copyReportSummary() {
    final langCode = context.loc.languageCode;
    final summary = '''
${context.tr('reportSummaryTitle')}
${context.tr('scanReference')}: #${_pred.id}
${context.tr('primaryCropLabel')}: ${context.loc.crop(_pred.crop)}
${context.tr('cropDiagnosis')}: ${context.loc.disease(_pred.disease)}
${context.tr('aiConfidence')}: ${(_pred.confidence * 100).round()}%
${context.tr('severity')}: ${_pred.severity}% (${context.loc.severityPercent(_pred.severity)})

${context.tr('actionPlan')}:
1. ${context.tr('immediate')}: ${_pred.localizedImmediateAction(langCode) ?? context.tr('standardPrecautions')}
2. ${context.tr('treatment')}: ${_pred.localizedTreatment(langCode) ?? context.tr('referLocalGuidelines')}
3. ${context.tr('prevention')}: ${_pred.localizedPrevention(langCode) ?? context.tr('maintainFieldHygiene')}

${context.tr('reportGeneratedBy')}
''';
    Clipboard.setData(ClipboardData(text: summary.trim()));
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(context.tr('reportCopied'))),
    );
  }

  void _showImageDialog(String imageUrl, String title) {
    showDialog(
      context: context,
      builder: (ctx) => Dialog(
        backgroundColor: Colors.black87,
        insetPadding: const EdgeInsets.all(12),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(title, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white),
                    onPressed: () => Navigator.pop(ctx),
                  ),
                ],
              ),
            ),
            Flexible(
              child: InteractiveViewer(
                clipBehavior: Clip.none,
                child: Image.network(
                  imageUrl,
                  fit: BoxFit.contain,
                  errorBuilder: (_, __, ___) => const Padding(
                    padding: EdgeInsets.all(32),
                    child: Icon(Icons.broken_image, color: Colors.white54, size: 48),
                  ),
                ),
              ),
            ),
            const SizedBox(height: 12),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final langCode = context.loc.languageCode;
    final translatedCrop = context.loc.crop(_pred.crop);
    final translatedDisease = context.loc.disease(_pred.disease);
    final severityLevel = _pred.severityBucket != null
        ? context.loc.severity(_pred.severityBucket)
        : context.loc.severityPercent(_pred.severity);

    final immAction = _pred.localizedImmediateAction(langCode);
    final treatment = _pred.localizedTreatment(langCode);
    final prevention = _pred.localizedPrevention(langCode);
    final monitoring = _pred.localizedMonitoring(langCode);
    final fallbackRec = _pred.localizedRecommendation(langCode);

    final rawImgUrl = (_pred.rawPath != null && _pred.rawPath!.isNotEmpty)
        ? widget.api.getAssetUrl(_pred.rawPath)
        : (_pred.rawUrl != null && _pred.rawUrl!.isNotEmpty ? _pred.rawUrl! : null);

    final procImgUrl = (_pred.processedPath != null && _pred.processedPath!.isNotEmpty)
        ? widget.api.getAssetUrl(_pred.processedPath)
        : (_pred.processedUrl != null && _pred.processedUrl!.isNotEmpty
            ? _pred.processedUrl!
            : (_pred.imagePath != null && _pred.imagePath!.isNotEmpty ? widget.api.getAssetUrl(_pred.imagePath) : null));

    final hasImages = rawImgUrl != null || procImgUrl != null;
    final activeImgUrl = _visualTab == 0 ? (rawImgUrl ?? procImgUrl) : (procImgUrl ?? rawImgUrl);

    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.88,
      maxChildSize: 0.96,
      minChildSize: 0.5,
      builder: (_, controller) => ListView(
        controller: controller,
        padding: const EdgeInsets.all(22),
        children: [
          Center(
            child: Container(
              width: 42,
              height: 4,
              decoration: BoxDecoration(color: Colors.grey.shade400, borderRadius: BorderRadius.circular(2)),
            ),
          ),
          const SizedBox(height: 16),

          // Header Row
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  '${translatedCrop.toUpperCase()} ${context.tr('cropDiagnosis')}  #${_pred.id}',
                  style: const TextStyle(letterSpacing: 1.5, color: AppColors.primary, fontWeight: FontWeight.bold, fontSize: 12),
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  IconButton(
                    onPressed: _copyReportSummary,
                    icon: const Icon(Icons.share_outlined, color: AppColors.primary, size: 22),
                    tooltip: context.tr('shareReport'),
                  ),
                  IconButton(
                    onPressed: () => showLanguageSelectionSheet(context),
                    icon: const Icon(Icons.language, color: AppColors.primary, size: 22),
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

          Text(translatedDisease, style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
          const SizedBox(height: 10),

          // Diagnostic Metrics Badges
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
              if (_pred.isFallback)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(color: const Color(0xfffff3cd), borderRadius: BorderRadius.circular(8)),
                  child: Text(
                    context.tr('standardFallback'),
                    style: const TextStyle(color: Color(0xff856404), fontWeight: FontWeight.bold, fontSize: 11),
                  ),
                ),
              if (_pred.expertReviewStatus == 'pending')
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(color: const Color(0xffe8eaf6), borderRadius: BorderRadius.circular(8)),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.hourglass_top, size: 14, color: Color(0xff3f51b5)),
                      SizedBox(width: 4),
                      Text('Review Pending', style: TextStyle(color: Color(0xff3f51b5), fontWeight: FontWeight.bold, fontSize: 11)),
                    ],
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

          // Tentative Low Confidence Warning Banner
          if (_pred.isUncertain) ...[
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xfffff8e1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xffffe082)),
              ),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Icon(Icons.warning_amber_rounded, color: Color(0xfff57f17), size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      context.tr('tentativeWarning'),
                      style: const TextStyle(color: Color(0xfff57f17), fontSize: 12, height: 1.35, fontWeight: FontWeight.w500),
                    ),
                  ),
                ],
              ),
            ),
          ],

          const SizedBox(height: 18),

          // ── Visual Pathology Analysis (Original Leaf vs GradCAM Heatmap) ──────
          if (hasImages && activeImgUrl != null) ...[
            Container(
              decoration: BoxDecoration(
                color: AppColors.cardBg,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Padding(
                    padding: const EdgeInsets.fromLTRB(16, 12, 16, 8),
                    child: Wrap(
                      alignment: WrapAlignment.spaceBetween,
                      runSpacing: 8,
                      crossAxisAlignment: WrapCrossAlignment.center,
                      children: [
                        Text(
                          context.tr('visualAnalysis'),
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                        // Segmented Toggle
                        Container(
                          padding: const EdgeInsets.all(3),
                          decoration: BoxDecoration(
                            color: const Color(0xffedeae1),
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              GestureDetector(
                                onTap: () => setState(() => _visualTab = 0),
                                child: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                                  decoration: BoxDecoration(
                                    color: _visualTab == 0 ? Colors.white : Colors.transparent,
                                    borderRadius: BorderRadius.circular(8),
                                    boxShadow: _visualTab == 0 ? [const BoxShadow(color: Colors.black12, blurRadius: 3)] : null,
                                  ),
                                  child: Text(
                                    context.tr('originalLeaf'),
                                    style: TextStyle(
                                      fontSize: 11,
                                      fontWeight: _visualTab == 0 ? FontWeight.bold : FontWeight.normal,
                                      color: _visualTab == 0 ? AppColors.primary : AppColors.textMuted,
                                    ),
                                  ),
                                ),
                              ),
                              if (procImgUrl != null)
                                GestureDetector(
                                  onTap: () => setState(() => _visualTab = 1),
                                  child: Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                                    decoration: BoxDecoration(
                                      color: _visualTab == 1 ? Colors.white : Colors.transparent,
                                      borderRadius: BorderRadius.circular(8),
                                      boxShadow: _visualTab == 1 ? [const BoxShadow(color: Colors.black12, blurRadius: 3)] : null,
                                    ),
                                    child: Text(
                                      context.tr('gradcamHeatmap'),
                                      style: TextStyle(
                                        fontSize: 11,
                                        fontWeight: _visualTab == 1 ? FontWeight.bold : FontWeight.normal,
                                        color: _visualTab == 1 ? AppColors.primary : AppColors.textMuted,
                                      ),
                                    ),
                                  ),
                                ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  GestureDetector(
                    onTap: () => _showImageDialog(
                      activeImgUrl,
                      _visualTab == 0 ? context.tr('originalLeaf') : context.tr('gradcamHeatmap'),
                    ),
                    child: Container(
                      height: 200,
                      margin: const EdgeInsets.fromLTRB(12, 0, 12, 12),
                      decoration: BoxDecoration(
                        color: Colors.black,
                        borderRadius: BorderRadius.circular(12),
                      ),
                      clipBehavior: Clip.antiAlias,
                      child: Stack(
                        fit: StackFit.expand,
                        children: [
                          Image.network(
                            activeImgUrl,
                            fit: BoxFit.cover,
                            errorBuilder: (_, __, ___) => const Center(
                              child: Icon(Icons.broken_image, color: Colors.white54, size: 40),
                            ),
                          ),
                          Positioned(
                            right: 8,
                            bottom: 8,
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                              decoration: BoxDecoration(
                                color: Colors.black54,
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: const Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  Icon(Icons.zoom_in, color: Colors.white, size: 14),
                                  SizedBox(width: 4),
                                  Text('Tap to zoom', style: TextStyle(color: Colors.white, fontSize: 10)),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 18),
          ],

          // ── Interactive Full Audio Player Bar ────────────────────────────────
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

          // ── Specialist Verified Advisory OR Masked Advisory ─────────────────
          if (_pred.isMasked) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xfffbe9e7),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xffffccbc)),
              ),
              child: Column(
                children: [
                  const Icon(Icons.shield_outlined, color: Color(0xffd84315), size: 32),
                  const SizedBox(height: 8),
                  Text(context.tr('advisoryMasked'), style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xffd84315), fontSize: 15)),
                  const SizedBox(height: 6),
                  Text(
                    context.tr('advisoryMaskedDesc'),
                    textAlign: TextAlign.center,
                    style: const TextStyle(color: Color(0xffbf360c), fontSize: 12, height: 1.4),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
          ] else if (_pred.expertGuidance != null && _pred.expertGuidance!.isNotEmpty) ...[
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: const Color(0xffe0f2f1),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(color: const Color(0xff80cbc4)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.verified, color: Color(0xff00897b), size: 20),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          context.tr('specialistVerified'),
                          style: const TextStyle(color: Color(0xff00695c), fontWeight: FontWeight.bold, fontSize: 14),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    _pred.expertGuidance!,
                    style: const TextStyle(color: Color(0xff004d40), fontSize: 13, height: 1.45),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
          ],

          // ── Actionable Recommendations ──────────────────────────────────────
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
          const SizedBox(height: 16),

          // ── Agricultural Safety Disclaimer ──────────────────────────────────
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: const Color(0xffffebee),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: const Color(0xffffcdd2)),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.info_outline, color: Colors.red, size: 18),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    context.tr('safetyDisclaimer'),
                    style: const TextStyle(color: Color(0xffc62828), fontSize: 11, height: 1.35),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 20),

          // ── Weather Context Snapshot (if recorded during scan) ───────────────
          if (_pred.weatherTemp != null || _pred.weatherCondition != null) ...[
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppColors.cardBg,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Row(
                children: [
                  const Icon(Icons.cloud_outlined, color: AppColors.primary, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      '${context.tr('weatherSnapshot')}: ${_pred.weatherTemp ?? "--"}°C · ${_pred.weatherHumidity ?? "--"}% humidity (${context.loc.weather(_pred.weatherCondition)})',
                      style: const TextStyle(fontSize: 12, color: AppColors.textMuted),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
          ],

          // ── Disease Progression Timeline ────────────────────────────────────
          if (_pred.historicalImages.isNotEmpty) ...[
            Text(context.tr('diseaseTimeline'), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            SizedBox(
              height: 80,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _pred.historicalImages.length + 1,
                separatorBuilder: (_, __) => const SizedBox(width: 10),
                itemBuilder: (_, index) {
                  if (index < _pred.historicalImages.length) {
                    final item = _pred.historicalImages[index];
                    final date = item['created_at'] != null ? item['created_at'].toString().split('T').first : 'Past';
                    final sev = item['severity_pct'] ?? item['severity'] ?? '--';
                    return Container(
                      width: 120,
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.cardBg,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: AppColors.cardBorder),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Text(date, style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
                          const SizedBox(height: 2),
                          Text('${context.tr('severity')}: $sev%', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
                        ],
                      ),
                    );
                  } else {
                    // Latest scan tile
                    return Container(
                      width: 120,
                      padding: const EdgeInsets.all(10),
                      decoration: BoxDecoration(
                        color: AppColors.primaryLight,
                        borderRadius: BorderRadius.circular(10),
                        border: Border.all(color: AppColors.primaryBorder),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Text('Latest Scan', style: TextStyle(fontSize: 10, color: AppColors.primary, fontWeight: FontWeight.bold)),
                          const SizedBox(height: 2),
                          Text('${context.tr('severity')}: ${_pred.severity}%', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: AppColors.primary)),
                        ],
                      ),
                    );
                  }
                },
              ),
            ),
            const SizedBox(height: 24),
          ],

          // ── Model & Provenance Telemetry Footer ──────────────────────────────
          if (_pred.modelUsed != null || _pred.durationMs != null) ...[
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4),
              child: Wrap(
                alignment: WrapAlignment.spaceBetween,
                spacing: 8,
                runSpacing: 4,
                children: [
                  Text('Model: ${_pred.modelUsed ?? "EfficientNet"}', style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
                  if (_pred.durationMs != null)
                    Text('Latency: ${_pred.durationMs}ms', style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
                  Text('Schema: v${_pred.schemaVersion ?? "2.0"}', style: const TextStyle(fontSize: 10, color: AppColors.textMuted)),
                ],
              ),
            ),
            const SizedBox(height: 18),
          ],

          // ── Farmer Accuracy Feedback ─────────────────────────────────────────
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

          // ── Follow-Up Rescan & Expert Escalation Actions ─────────────────────
          Row(
            children: [
              Expanded(
                child: FilledButton.icon(
                  onPressed: _isRescanning ? null : () => _handleRescan(ImageSource.camera),
                  style: FilledButton.styleFrom(
                    backgroundColor: AppColors.primary,
                    padding: const EdgeInsets.symmetric(vertical: 14),
                  ),
                  icon: _isRescanning
                      ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.add_a_photo_outlined, size: 18),
                  label: Text(_isRescanning ? context.tr('rescanning') : context.tr('rescanFollowUp'), style: const TextStyle(fontSize: 13)),
                ),
              ),
              const SizedBox(width: 10),
              OutlinedButton(
                onPressed: _requestExpert,
                style: OutlinedButton.styleFrom(padding: const EdgeInsets.all(14)),
                child: const Icon(Icons.support_agent, color: AppColors.primary),
              ),
            ],
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}
