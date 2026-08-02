import 'package:flutter/material.dart';

class AboutScreen extends StatelessWidget {
  const AboutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final Color cardBg = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final Color cardBorder =
        isDark ? Colors.grey.shade800 : Colors.grey.shade300;

    final keywords = <String, String>{
      'khdem': 'déclarer une variable',
      'dallel / fonction': 'déclarer une fonction',
      'rejje / retourner': 'return',
      'ken / sinon / sinon_ken': 'if / else / elif',
      'men ... 7ata / hatta': 'boucle for (de ... à)',
      'tawa': 'while',
      'class / toroth': 'classe / hérite de',
      'hetha': 'this',
      'jdid': 'constructeur',
      'new': 'instancier une classe',
      '7awel / ebsed / akhir': 'try / catch / finally',
      'jib': 'importer un module',
      'wakaf / tkhata': 'break / continue',
      'ikteb': 'afficher (print)',
      'iqra': 'lecture utilisateur (input)',
      's7i7 / ghalet': 'true / false',
    };

    return Scaffold(
      appBar: AppBar(
        title: const Text('À propos', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Center(
            child: Column(
              children: [
                const Text('🐪', style: TextStyle(fontSize: 56)),
                const SizedBox(height: 8),
                const Text(
                  'TounsiLang (Bou.Bel)',
                  style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 4),
                Text(
                  'Tunisian Arabic Programming Language',
                  style: TextStyle(
                    color: isDark ? Colors.grey.shade400 : Colors.grey.shade600,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'MOTS-CLÉS',
            style: TextStyle(
              color: isDark ? Colors.grey.shade500 : Colors.grey.shade600,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            decoration: BoxDecoration(
              color: cardBg,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: cardBorder),
            ),
            child: Column(
              children: keywords.entries.map((entry) {
                return ListTile(
                  title: Text(
                    entry.key,
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  subtitle: Text(entry.value),
                  dense: true,
                );
              }).toList(),
            ),
          ),
          const SizedBox(height: 24),
          Center(
            child: Text(
              'Version 1.0.0',
              style: TextStyle(
                color: isDark ? Colors.grey.shade600 : Colors.grey.shade500,
                fontSize: 12,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
