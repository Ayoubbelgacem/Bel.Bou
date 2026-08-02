import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/code_provider.dart';
import '../data/examples.dart';

/// Écran d'accueil. onNavigateToTab permet de basculer vers un autre onglet
/// de la BottomNavigationBar.
/// Index: 0=Accueil, 1=Éditeur, 2=Fichiers, 3=Exemples, 4=Réglages.
class HomeScreen extends StatelessWidget {
  final void Function(int tabIndex) onNavigateToTab;

  const HomeScreen({super.key, required this.onNavigateToTab});

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final Color accent = isDark ? Colors.blue.shade400 : Colors.blue.shade700;
    final Color cardBg = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final Color cardBorder =
        isDark ? Colors.grey.shade800 : Colors.grey.shade300;
    final Color mutedText =
        isDark ? Colors.grey.shade500 : Colors.grey.shade600;

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'TounsiLang',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [accent, accent.withOpacity(0.7)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '🐪 Bienvenue sur Bou.Bel',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  'Le langage de programmation tunisien.\nÉcris, exécute, apprends.',
                  style: TextStyle(color: Colors.white70, fontSize: 14),
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  onPressed: () => onNavigateToTab(1),
                  icon: const Icon(Icons.play_arrow),
                  label: const Text('Ouvrir l\'éditeur'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.white,
                    foregroundColor: accent,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(30),
                    ),
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          Text(
            'ACCÈS RAPIDE',
            style: TextStyle(
              color: mutedText,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.add_circle_outline,
                  label: 'Nouveau',
                  bg: cardBg,
                  border: cardBorder,
                  accent: accent,
                  onTap: () {
                    context.read<CodeProvider>().loadCode('');
                    onNavigateToTab(1);
                  },
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.folder_outlined,
                  label: 'Fichiers',
                  bg: cardBg,
                  border: cardBorder,
                  accent: accent,
                  onTap: () => onNavigateToTab(2),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: _QuickActionCard(
                  icon: Icons.menu_book,
                  label: 'Exemples',
                  bg: cardBg,
                  border: cardBorder,
                  accent: accent,
                  onTap: () => onNavigateToTab(3),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),
          Text(
            'EXEMPLES POPULAIRES',
            style: TextStyle(
              color: mutedText,
              fontSize: 12,
              fontWeight: FontWeight.bold,
              letterSpacing: 1.2,
            ),
          ),
          const SizedBox(height: 12),
          ...tounsiExamples.take(3).map(
                (e) => Card(
                  color: cardBg,
                  margin: const EdgeInsets.only(bottom: 10),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                    side: BorderSide(color: cardBorder),
                  ),
                  child: ListTile(
                    title: Text(e.title),
                    trailing: const Icon(Icons.chevron_right),
                    onTap: () {
                      context.read<CodeProvider>().loadCode(e.code);
                      onNavigateToTab(1);
                    },
                  ),
                ),
              ),
        ],
      ),
    );
  }
}

class _QuickActionCard extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color bg;
  final Color border;
  final Color accent;
  final VoidCallback onTap;

  const _QuickActionCard({
    required this.icon,
    required this.label,
    required this.bg,
    required this.border,
    required this.accent,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 18),
        decoration: BoxDecoration(
          color: bg,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: border),
        ),
        child: Column(
          children: [
            Icon(icon, color: accent, size: 26),
            const SizedBox(height: 6),
            Text(
              label,
              style: const TextStyle(
                fontWeight: FontWeight.w600,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
