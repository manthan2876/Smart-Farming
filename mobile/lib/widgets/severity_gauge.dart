import 'package:flutter/material.dart';

class SeverityGauge extends StatelessWidget {
  const SeverityGauge({super.key, required this.value});
  final int value;

  @override
  Widget build(BuildContext context) => SizedBox(width: 74, height: 74, child: Stack(alignment: Alignment.center, children: [CircularProgressIndicator(value: value / 100, strokeWidth: 8, backgroundColor: const Color(0xffe4e4d9), color: value > 60 ? const Color(0xffc56a59) : value > 30 ? const Color(0xffd66d43) : const Color(0xff7eae7b)), Text('$value%', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15))]));
}
