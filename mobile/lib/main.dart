import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_tts/flutter_tts.dart';
import 'package:image_picker/image_picker.dart';
import 'models/prediction.dart';
import 'services/api_service.dart';
import 'services/sync_service.dart';

void main() => runApp(const FieldnoteApp());

class FieldnoteApp extends StatelessWidget {
  const FieldnoteApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
        debugShowCheckedModeBanner: false,
        title: 'Fieldnote',
        theme: ThemeData(
          useMaterial3: true,
          scaffoldBackgroundColor: const Color(0xfff4f1e8),
          colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xff276b52), brightness: Brightness.light),
          fontFamily: 'sans',
        ),
        home: const FieldHome(),
      );
}

class FieldHome extends StatefulWidget {
  const FieldHome({super.key});
  @override
  State<FieldHome> createState() => _FieldHomeState();
}

class _FieldHomeState extends State<FieldHome> {
  final _picker = ImagePicker();
  final _tts = FlutterTts();
  final _api = ApiService();
  late final SyncService _sync = SyncService(_api);
  int _tab = 0;
  File? _photo;
  bool _busy = false;
  int _pending = 0;
  Prediction _latest = const Prediction(id: 204, crop: 'Tomato', disease: 'Aphids', confidence: .88, severity: 37, recommendation: 'Inspect new growth every 48 hours and remove heavily affected leaves.');
  final _history = <Prediction>[];

  @override
  void initState() { super.initState(); _refreshQueue(); _loadHistory(); }
  Future<void> _refreshQueue() async { final count = await _sync.pendingCount(); if (mounted) setState(() => _pending = count); }
  Future<void> _loadHistory() async { try { _history.addAll(await _api.history()); if (mounted) setState(() {}); } catch (_) {} }
  Future<void> _capture() async {
    final picked = await _picker.pickImage(source: ImageSource.camera, imageQuality: 84, maxWidth: 1600);
    if (picked == null) return;
    setState(() { _photo = File(picked.path); _busy = true; });
    try { final result = await _api.predict(_photo!); setState(() { _latest = result; _history.insert(0, result); }); }
    catch (_) { await _sync.enqueue(_photo!); await _refreshQueue(); }
    finally { if (mounted) setState(() => _busy = false); }
  }
  Future<void> _speak() async { await _tts.setLanguage('en-US'); await _tts.speak(_latest.recommendation); }

  @override
  Widget build(BuildContext context) => Scaffold(
        body: SafeArea(child: IndexedStack(index: _tab, children: [_home(), _historyPage(), _profile()])),
        bottomNavigationBar: NavigationBar(selectedIndex: _tab, onDestinationSelected: (index) => setState(() => _tab = index), backgroundColor: const Color(0xfffbfaf5), destinations: const [NavigationDestination(icon: Icon(Icons.wb_sunny_outlined), selectedIcon: Icon(Icons.wb_sunny), label: 'Today'), NavigationDestination(icon: Icon(Icons.timeline_outlined), selectedIcon: Icon(Icons.timeline), label: 'History'), NavigationDestination(icon: Icon(Icons.person_outline), selectedIcon: Icon(Icons.person), label: 'Farm')]),
      );

  Widget _home() => ListView(padding: const EdgeInsets.fromLTRB(22, 22, 22, 30), children: [
        Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('FIELDNOTE', style: TextStyle(letterSpacing: 2, fontWeight: FontWeight.bold, fontSize: 12, color: Color(0xff276b52))), SizedBox(height: 5), Text('Your field, in focus.', style: TextStyle(fontSize: 26, fontWeight: FontWeight.w600))]), Container(padding: const EdgeInsets.all(10), decoration: BoxDecoration(color: const Color(0xffe5eee2), borderRadius: BorderRadius.circular(30)), child: const Icon(Icons.notifications_none, color: Color(0xff276b52)))]),
        const SizedBox(height: 22),
        Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(color: const Color(0xff276b52), borderRadius: BorderRadius.circular(22)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [const Text('NORTH PLOT  ·  ANAND', style: TextStyle(color: Color(0xffb8d3b7), letterSpacing: 1.5, fontSize: 10, fontWeight: FontWeight.bold)), const SizedBox(height: 12), const Text('A clear leaf photo\nstarts a better decision.', style: TextStyle(color: Colors.white, fontSize: 25, height: 1.1, fontWeight: FontWeight.w500)), const SizedBox(height: 18), FilledButton.icon(onPressed: _busy ? null : _capture, icon: _busy ? const SizedBox(width: 16, height: 16, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.camera_alt_outlined), label: Text(_busy ? 'Reading leaf...' : 'Scan a leaf'), style: FilledButton.styleFrom(backgroundColor: const Color(0xffffd681), foregroundColor: const Color(0xff20312b), padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 13)))])),
        const SizedBox(height: 16),
        Row(children: [_stat('27°', 'clear skies'), _stat('68%', 'humidity'), _stat('${_pending}', 'waiting sync')]),
        const SizedBox(height: 25),
        Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [const Text('Latest reading', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w600)), TextButton(onPressed: () => setState(() => _tab = 1), child: const Text('See trail'))]),
        _readingCard(),
        const SizedBox(height: 17),
        Container(padding: const EdgeInsets.all(18), decoration: BoxDecoration(color: const Color(0xffffe8c6), borderRadius: BorderRadius.circular(18)), child: Row(crossAxisAlignment: CrossAxisAlignment.start, children: [const Icon(Icons.spa_outlined, color: Color(0xffd66d43)), const SizedBox(width: 12), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [const Text('Next best action', style: TextStyle(color: Color(0xff866b47), fontSize: 11, fontWeight: FontWeight.bold)), const SizedBox(height: 5), Text(_latest.recommendation, style: const TextStyle(color: Color(0xff5d513f), height: 1.4)), TextButton.icon(onPressed: _speak, icon: const Icon(Icons.volume_up_outlined, size: 16), label: const Text('Listen'))]))]))
      ]);

  Widget _stat(String value, String label) => Expanded(child: Container(margin: const EdgeInsets.only(right: 7), padding: const EdgeInsets.symmetric(vertical: 14, horizontal: 9), decoration: BoxDecoration(color: const Color(0xfffbfaf5), border: Border.all(color: const Color(0xffdddcd1)), borderRadius: BorderRadius.circular(12)), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(value, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)), const SizedBox(height: 3), Text(label, style: const TextStyle(color: Color(0xff728079), fontSize: 10))])));
  Widget _readingCard() => Card(elevation: 0, color: const Color(0xfffbfaf5), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(18), side: const BorderSide(color: Color(0xffdddcd1))), child: Padding(padding: const EdgeInsets.all(13), child: Row(children: [ClipRRect(borderRadius: BorderRadius.circular(12), child: _photo != null ? Image.file(_photo!, width: 84, height: 84, fit: BoxFit.cover) : Container(width: 84, height: 84, color: const Color(0xffdbe8d8), child: const Icon(Icons.eco_outlined, size: 36, color: Color(0xff276b52)))), const SizedBox(width: 14), Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(_latest.crop.toUpperCase(), style: const TextStyle(letterSpacing: 1.4, color: Color(0xff8c968c), fontSize: 9, fontWeight: FontWeight.bold)), const SizedBox(height: 5), Text(_latest.disease, style: const TextStyle(fontSize: 21, fontWeight: FontWeight.w600)), const SizedBox(height: 9), Row(children: [Text('${(_latest.confidence * 100).round()}% sure', style: const TextStyle(color: Color(0xff276b52), fontSize: 11, fontWeight: FontWeight.bold)), const Spacer(), Text('${_latest.severity}% affected', style: const TextStyle(color: Color(0xffd66d43), fontSize: 11))])]))]));
  Widget _historyPage() => ListView(padding: const EdgeInsets.all(22), children: [const Text('FIELD ARCHIVE', style: TextStyle(letterSpacing: 2, color: Color(0xff8c968c), fontSize: 10, fontWeight: FontWeight.bold)), const SizedBox(height: 8), const Text('Your scan trail', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w600)), const SizedBox(height: 22), ...[_latest, ..._history].take(8).map((item) => ListTile(contentPadding: const EdgeInsets.symmetric(vertical: 4), leading: CircleAvatar(backgroundColor: const Color(0xffe5eee2), child: const Icon(Icons.eco_outlined, color: Color(0xff276b52))), title: Text(item.disease, style: const TextStyle(fontWeight: FontWeight.w600)), subtitle: Text('${item.crop}  ·  ${item.severity}% affected'), trailing: Text('${(item.confidence * 100).round()}%', style: const TextStyle(color: Color(0xff276b52), fontWeight: FontWeight.bold)))];
  Widget _profile() => ListView(padding: const EdgeInsets.all(22), children: [const Text('FARM PROFILE', style: TextStyle(letterSpacing: 2, color: Color(0xff8c968c), fontSize: 10, fontWeight: FontWeight.bold)), const SizedBox(height: 8), const Text('Manthan Patel', style: TextStyle(fontSize: 29, fontWeight: FontWeight.w600)), const Text('North plot · Anand, Gujarat', style: TextStyle(color: Color(0xff728079))), const SizedBox(height: 30), _profileTile(Icons.location_on_outlined, 'Farm location', 'Anand, Gujarat'), _profileTile(Icons.language, 'Advice language', 'English'), _profileTile(Icons.grass, 'Crops in rotation', 'Tomato · Cotton · Potato')]);
  Widget _profileTile(IconData icon, String title, String value) => ListTile(contentPadding: const EdgeInsets.symmetric(vertical: 8), leading: CircleAvatar(backgroundColor: const Color(0xffffe8c6), child: Icon(icon, color: const Color(0xffd66d43))), title: Text(title, style: const TextStyle(fontSize: 11, color: Color(0xff8c968c))), subtitle: Text(value, style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 15)));
}
