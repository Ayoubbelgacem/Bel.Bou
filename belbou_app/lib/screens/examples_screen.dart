import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/code_provider.dart';
import '../data/examples.dart';

class ExamplesScreen extends StatelessWidget {
  final void Function(int tabIndex) onNavigateToTab;

  const ExamplesScreen({super.key, required this.onNavigateToTab});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final Color cardBg = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final Color cardBorder =
        isDark ? Colors.grey.shade800 : Colors.grey.shade300;
    final Color mutedText =
        isDark ? Colors.grey.shade500 : Colors.grey.shade600;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Exemples', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: ListView.separated(
        padding: const EdgeInsets.all(16),
        itemCount: tounsiExamples.length,
        separatorBuilder: (_, __) => const SizedBox(height: 10),
        itemBuilder: (context, index) {
          final example = tounsiExamples[index];
          final previewLines = example.code.trim().split('\n');
          final preview = previewLines.length > 3
              ? '${previewLines.take(3).join('\n')}\n…'
              : previewLines.join('\n');

          return Card(
            color: cardBg,
            elevation: 0,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
              side: BorderSide(color: cardBorder),
            ),
            child: ListTile(
              contentPadding: const EdgeInsets.all(14),
              title: Text(
                example.title,
                style: const TextStyle(fontWeight: FontWeight.bold),
              ),
              subtitle: Padding(
                padding: const EdgeInsets.only(top: 6),
                child: Text(
                  preview,
                  maxLines: 3,
                  overflow: TextOverflow.ellipsis,
                  style: TextStyle(
                    fontFamily: 'monospace',
                    fontSize: 12,
                    color: mutedText,
                  ),
                ),
              ),
              trailing: const Icon(Icons.play_circle_outline),
              onTap: () {
                context.read<CodeProvider>().loadCode(example.code);
                onNavigateToTab(1);
              },
            ),
          );
        },
      ),
    );
  }
}
