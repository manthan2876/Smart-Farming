import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../../providers/locale_provider.dart';
import '../../services/api_service.dart';
import '../../services/sync_service.dart';
import '../../theme/app_theme.dart';

class CreatePredictionSheet extends StatefulWidget {
  const CreatePredictionSheet({
    super.key,
    required this.api,
    required this.sync,
    required this.user,
    required this.farm,
    this.initialBytes,
    this.initialName,
    required this.onStarted,
  });

  final ApiService api;
  final SyncService sync;
  final Map<String, dynamic> user;
  final Map<String, dynamic>? farm;
  final Uint8List? initialBytes;
  final String? initialName;
  final void Function(int predictionId, Uint8List bytes, String filename) onStarted;

  @override
  State<CreatePredictionSheet> createState() => _CreatePredictionSheetState();
}

class _CreatePredictionSheetState extends State<CreatePredictionSheet> {
  final _picker = ImagePicker();
  Uint8List? _bytes;
  String _fileName = 'leaf.jpg';
  int? _selectedPlotId;
  late final TextEditingController _locationCtrl;
  late final TextEditingController _latCtrl;
  late final TextEditingController _lonCtrl;
  String? _language;
  bool _submitting = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _bytes = widget.initialBytes;
    _fileName = widget.initialName ?? 'leaf.jpg';
    _locationCtrl = TextEditingController(text: widget.user['location']?.toString() ?? 'Anand, Gujarat');
    _latCtrl = TextEditingController(text: widget.user['latitude']?.toString() ?? '21.7645');
    _lonCtrl = TextEditingController(text: widget.user['longitude']?.toString() ?? '72.1519');
    _language = null;
  }

  @override
  void dispose() {
    _locationCtrl.dispose();
    _latCtrl.dispose();
    _lonCtrl.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final picked = await _picker.pickImage(source: source, imageQuality: 85, maxWidth: 1600);
      if (picked == null) return;
      final bytes = await picked.readAsBytes();
      setState(() {
        _bytes = bytes;
        _fileName = picked.name.isNotEmpty ? picked.name : 'leaf.jpg';
        _error = null;
      });
    } catch (e) {
      setState(() => _error = 'Failed to select photo: $e');
    }
  }

  Future<void> _submit() async {
    if (_bytes == null) {
      setState(() => _error = context.tr('photoRequiredError'));
      return;
    }

    setState(() {
      _submitting = true;
      _error = null;
    });

    final loc = _locationCtrl.text.trim().isNotEmpty ? _locationCtrl.text.trim() : 'My Farm';
    final lat = double.tryParse(_latCtrl.text.trim()) ?? 21.7645;
    final lon = double.tryParse(_lonCtrl.text.trim()) ?? 72.1519;
    final targetLang = _language ?? context.loc.currentLanguage;

    final connectivity = await Connectivity().checkConnectivity();
    if (connectivity.contains(ConnectivityResult.none)) {
      await widget.sync.enqueueBytes(
        _bytes!,
        _fileName,
        location: loc,
        language: targetLang,
      );
      if (mounted) {
        Navigator.pop(context);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(context.tr('offlineQueuedBanner'))),
        );
      }
      return;
    }

    try {
      final res = await widget.api.predictBytes(
        _bytes!,
        _fileName,
        location: loc,
        language: targetLang,
        plotId: _selectedPlotId,
        lat: lat,
        lon: lon,
      );
      final pid = (res['prediction_id'] as num?)?.toInt() ?? (res['id'] as num?)?.toInt() ?? 0;
      if (pid > 0 && mounted) {
        widget.onStarted(pid, _bytes!, _fileName);
      } else {
        throw Exception('Prediction ID not received from server');
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _submitting = false;
          _error = e.toString().replaceAll('Exception: ', '');
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final plots = (widget.farm?['plots'] as List?) ?? [];
    final currentAppLanguage = context.loc.currentLanguage;
    final activeLanguage = _language ?? currentAppLanguage;

    return DraggableScrollableSheet(
      expand: false,
      initialChildSize: 0.9,
      maxChildSize: 0.96,
      minChildSize: 0.5,
      builder: (_, scrollCtrl) => ListView(
        controller: scrollCtrl,
        padding: const EdgeInsets.fromLTRB(20, 16, 20, 32),
        children: [
          Center(
            child: Container(
              width: 44,
              height: 4,
              decoration: BoxDecoration(color: Colors.grey.shade300, borderRadius: BorderRadius.circular(2)),
            ),
          ),
          const SizedBox(height: 18),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      context.tr('leafScannerHeader'),
                      style: const TextStyle(letterSpacing: 1.5, color: AppColors.primary, fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      context.tr('diagnoseCropLeaf'),
                      style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
                    ),
                  ],
                ),
              ),
              IconButton(onPressed: () => Navigator.pop(context), icon: const Icon(Icons.close)),
            ],
          ),
          const SizedBox(height: 6),
          Text(
            context.tr('leafScanDesc'),
            style: const TextStyle(color: AppColors.textMuted, fontSize: 13, height: 1.4),
          ),
          if (_error != null) ...[
            const SizedBox(height: 14),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(color: const Color(0xffffebee), borderRadius: BorderRadius.circular(10), border: Border.all(color: Colors.red.shade200)),
              child: Row(
                children: [
                  const Icon(Icons.error_outline, color: Colors.red, size: 18),
                  const SizedBox(width: 8),
                  Expanded(child: Text(_error!, style: TextStyle(color: Colors.red.shade900, fontSize: 12))),
                ],
              ),
            ),
          ],
          const SizedBox(height: 18),

          // Leaf photo preview or picker
          if (_bytes == null)
            Container(
              padding: const EdgeInsets.symmetric(vertical: 36, horizontal: 20),
              decoration: BoxDecoration(
                color: const Color(0xfff2f7f0),
                borderRadius: BorderRadius.circular(18),
                border: Border.all(color: AppColors.primaryBorder, width: 1.5),
              ),
              child: Column(
                children: [
                  const CircleAvatar(
                    radius: 32,
                    backgroundColor: AppColors.primaryLight,
                    child: Icon(Icons.add_a_photo_outlined, size: 32, color: AppColors.primary),
                  ),
                  const SizedBox(height: 14),
                  Text(
                    context.tr('selectLeafImage'),
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w600),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    context.tr('leafImageFormats'),
                    style: const TextStyle(fontSize: 12, color: AppColors.textMuted),
                  ),
                  const SizedBox(height: 20),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      ElevatedButton.icon(
                        onPressed: () => _pickImage(ImageSource.camera),
                        icon: const Icon(Icons.camera_alt),
                        label: Text(context.tr('takePhoto')),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primary,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        ),
                      ),
                      const SizedBox(width: 12),
                      OutlinedButton.icon(
                        onPressed: () => _pickImage(ImageSource.gallery),
                        icon: const Icon(Icons.photo_library),
                        label: Text(context.tr('browseFiles')),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            )
          else
            Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: Container(
                    height: 220,
                    color: Colors.black12,
                    child: Image.memory(_bytes!, fit: BoxFit.cover),
                  ),
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _pickImage(ImageSource.camera),
                        icon: const Icon(Icons.camera_alt, size: 16),
                        label: Text(context.tr('retakePhoto')),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: OutlinedButton.icon(
                        onPressed: () => _pickImage(ImageSource.gallery),
                        icon: const Icon(Icons.photo_library, size: 16),
                        label: Text(context.tr('gallery')),
                      ),
                    ),
                  ],
                ),
              ],
            ),

          const SizedBox(height: 22),

          // Diagnostic Telemetry Card
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: AppColors.primaryDark,
              borderRadius: BorderRadius.circular(18),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.tune, color: AppColors.accent, size: 18),
                    const SizedBox(width: 8),
                    Text(
                      context.tr('diagnosticTelemetry'),
                      style: const TextStyle(color: AppColors.accent, fontWeight: FontWeight.bold, letterSpacing: 1.2, fontSize: 12),
                    ),
                  ],
                ),
                const SizedBox(height: 16),

                // Plot selector
                Text(
                  context.tr('selectPlot'),
                  style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 6),
                DropdownButtonFormField<int?>(
                  initialValue: _selectedPlotId,
                  dropdownColor: AppColors.primaryDark,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    filled: true,
                    fillColor: Colors.white.withValues(alpha: 0.08),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2))),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2))),
                  ),
                  items: [
                    DropdownMenuItem<int?>(
                      value: null,
                      child: Text(context.tr('noPlotGeneralScan'), style: const TextStyle(color: Colors.white)),
                    ),
                    ...plots.map((p) {
                      final rawCrop = p['crop']?.toString() ?? 'Crop';
                      final cropName = context.loc.crop(rawCrop);
                      return DropdownMenuItem<int?>(
                        value: p['id'] as int?,
                        child: Text('${p['name']} ($cropName)', style: const TextStyle(color: Colors.white)),
                      );
                    }),
                  ],
                  onChanged: (val) => setState(() => _selectedPlotId = val),
                ),
                const SizedBox(height: 14),

                // Location field
                Text(
                  context.tr('locationField'),
                  style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 6),
                TextField(
                  controller: _locationCtrl,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    prefixIcon: const Icon(Icons.location_on_outlined, color: Colors.white70, size: 18),
                    filled: true,
                    fillColor: Colors.white.withValues(alpha: 0.08),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2))),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2))),
                  ),
                ),
                const SizedBox(height: 14),

                // Lat / Lon
                Row(
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            context.tr('latitude'),
                            style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _latCtrl,
                            keyboardType: TextInputType.number,
                            style: const TextStyle(color: Colors.white),
                            decoration: InputDecoration(
                              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                              filled: true,
                              fillColor: Colors.white.withValues(alpha: 0.08),
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2))),
                              enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2))),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            context.tr('longitude'),
                            style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w600),
                          ),
                          const SizedBox(height: 6),
                          TextField(
                            controller: _lonCtrl,
                            keyboardType: TextInputType.number,
                            style: const TextStyle(color: Colors.white),
                            decoration: InputDecoration(
                              contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                              filled: true,
                              fillColor: Colors.white.withValues(alpha: 0.08),
                              border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2))),
                              enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2))),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 14),

                // Language
                Text(
                  context.tr('recLanguage'),
                  style: const TextStyle(color: Colors.white70, fontSize: 12, fontWeight: FontWeight.w600),
                ),
                const SizedBox(height: 6),
                DropdownButtonFormField<String>(
                  initialValue: activeLanguage,
                  dropdownColor: AppColors.primaryDark,
                  style: const TextStyle(color: Colors.white),
                  decoration: InputDecoration(
                    contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    prefixIcon: const Icon(Icons.language, color: Colors.white70, size: 18),
                    filled: true,
                    fillColor: Colors.white.withValues(alpha: 0.08),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2))),
                    enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(8), borderSide: BorderSide(color: Colors.white.withValues(alpha: 0.2))),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'English', child: Text('English', style: TextStyle(color: Colors.white))),
                    DropdownMenuItem(value: 'Gujarati', child: Text('ગુજરાતી (Gujarati)', style: TextStyle(color: Colors.white))),
                    DropdownMenuItem(value: 'Hindi', child: Text('हिन्दी (Hindi)', style: TextStyle(color: Colors.white))),
                  ],
                  onChanged: (val) {
                    if (val != null) setState(() => _language = val);
                  },
                ),
              ],
            ),
          ),

          const SizedBox(height: 22),

          FilledButton.icon(
            onPressed: _submitting || _bytes == null ? null : _submit,
            icon: _submitting
                ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                : const Icon(Icons.auto_awesome),
            label: Text(
              _submitting ? context.tr('submitting') : context.tr('submitScan'),
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            style: FilledButton.styleFrom(
              backgroundColor: AppColors.primary,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
            ),
          ),
        ],
      ),
    );
  }
}
