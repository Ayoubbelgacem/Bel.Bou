import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/settings_provider.dart';
import '../providers/theme_provider.dart';
import '../providers/code_provider.dart';
import '../services/api_service.dart';
import 'about_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _urlController;
  bool _testing = false;
  bool? _testResult;

  @override
  void initState() {
    super.initState();
    _urlController = TextEditingController(
      text: context.read<SettingsProvider>().serverUrl,
    );
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }

  Future<void> _testConnection() async {
    setState(() {
      _testing = true;
      _testResult = null;
    });
    final ok = await ApiService().testConnection();
    if (!mounted) return;
    setState(() {
      _testing = false;
      _testResult = ok;
    });
  }

  @override
  Widget build(BuildContext context) {
    final settings = context.watch<SettingsProvider>();
    final themeProvider = context.watch<ThemeProvider>();
    final codeProvider = context.watch<CodeProvider>();
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final Color cardBg = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final Color cardBorder =
        isDark ? Colors.grey.shade800 : Colors.grey.shade300;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Paramètres', style: TextStyle(fontWeight: FontWeight.bold)),
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _SectionTitle('SERVEUR'),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: cardBg,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: cardBorder),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('URL du serveur d\'exécution'),
                const SizedBox(height: 8),
                TextField(
                  controller: _urlController,
                  decoration: const InputDecoration(
                    hintText: 'http://localhost:8000',
                    border: OutlineInputBorder(),
                    isDense: true,
                  ),
                  keyboardType: TextInputType.url,
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton(
                        onPressed: () {
                          settings.updateServerUrl(_urlController.text.trim());
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(
                              content: Text('URL enregistrée'),
                              duration: Duration(seconds: 1),
                            ),
                          );
                        },
                        child: const Text('Enregistrer'),
                      ),
                    ),
                    const SizedBox(width: 10),
                    OutlinedButton(
                      onPressed: _testing ? null : _testConnection,
                      child: _testing
                          ? const SizedBox(
                              width: 16,
                              height: 16,
                              child: CircularProgressIndicator(strokeWidth: 2),
                            )
                          : const Text('Tester'),
                    ),
                  ],
                ),
                if (_testResult != null) ...[
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      Icon(
                        _testResult! ? Icons.check_circle : Icons.error,
                        color: _testResult! ? Colors.green : Colors.red,
                        size: 18,
                      ),
                      const SizedBox(width: 6),
                      Text(_testResult!
                          ? 'Connexion réussie'
                          : 'Impossible de joindre le serveur'),
                    ],
                  ),
                ],
              ],
            ),
          ),
          const SizedBox(height: 24),
          _SectionTitle('EXÉCUTION'),
          Container(
            decoration: BoxDecoration(
              color: cardBg,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: cardBorder),
            ),
            child: Column(
              children: [
                RadioListTile<String>(
                  title: const Text('🚀 VM (par défaut)'),
                  value: 'vm',
                  groupValue: settings.defaultMode,
                  onChanged: (v) {
                    if (v == null) return;
                    settings.updateDefaultMode(v);
                    codeProvider.setMode(v);
                  },
                ),
                RadioListTile<String>(
                  title: const Text('🐍 Interpréteur'),
                  value: 'interpreter',
                  groupValue: settings.defaultMode,
                  onChanged: (v) {
                    if (v == null) return;
                    settings.updateDefaultMode(v);
                    codeProvider.setMode(v);
                  },
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
          _SectionTitle('APPARENCE'),
          Container(
            decoration: BoxDecoration(
              color: cardBg,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: cardBorder),
            ),
            child: SwitchListTile(
              title: const Text('Thème sombre'),
              value: themeProvider.isDark,
              onChanged: (_) => themeProvider.toggleTheme(),
            ),
          ),
          const SizedBox(height: 24),
          _SectionTitle('À PROPOS'),
          Container(
            decoration: BoxDecoration(
              color: cardBg,
              borderRadius: BorderRadius.circular(14),
              border: Border.all(color: cardBorder),
            ),
            child: ListTile(
              leading: const Icon(Icons.info_outline),
              title: const Text('À propos de TounsiLang'),
              trailing: const Icon(Icons.chevron_right),
              onTap: () => Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const AboutScreen()),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _SectionTitle extends StatelessWidget {
  final String text;
  const _SectionTitle(this.text);

  @override
  Widget build(BuildContext context) {
    final mutedText = Theme.of(context).brightness == Brightness.dark
        ? Colors.grey.shade500
        : Colors.grey.shade600;
    return Padding(
      padding: const EdgeInsets.only(bottom: 10, left: 4),
      child: Text(
        text,
        style: TextStyle(
          color: mutedText,
          fontSize: 12,
          fontWeight: FontWeight.bold,
          letterSpacing: 1.2,
        ),
      ),
    );
  }
}
