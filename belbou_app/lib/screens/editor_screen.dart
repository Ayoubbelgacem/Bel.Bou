import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:provider/provider.dart';
import 'package:share_plus/share_plus.dart';
import 'package:flutter_code_editor/flutter_code_editor.dart';
import '../providers/code_provider.dart';
import '../providers/theme_provider.dart';
import '../providers/file_provider.dart';
import '../languages/tounsilang.dart' as tounsi;
import '../theme/editor_themes.dart';
import '../data/examples.dart';

class EditorScreen extends StatefulWidget {
  const EditorScreen({super.key});

  @override
  State<EditorScreen> createState() => _EditorScreenState();
}

class _EditorScreenState extends State<EditorScreen> {
  late CodeController _codeController;
  int _lastLoadToken = 0;

  @override
  void initState() {
    super.initState();
    _codeController = CodeController(
      text: '''
# Bou.Bel example

ikteb("Salam Ayoub");

khdem age = 25;

ken age > 18 a3mel {
    ikteb("Kbir");
}

dallel somme(a,b) {
    rejje a + b;
}
''',
      language: tounsi.tounsilang,
    );

    _codeController.addListener(() {
      final provider = Provider.of<CodeProvider>(context, listen: false);
      if (_codeController.text != provider.code) {
        provider.updateCode(_codeController.text);
      }
    });

    WidgetsBinding.instance.addPostFrameCallback((_) {
      final provider = Provider.of<CodeProvider>(context, listen: false);
      _lastLoadToken = provider.loadToken;
    });
  }

  @override
  void dispose() {
    _codeController.dispose();
    super.dispose();
  }

  void _loadExample(CodeExample example) {
    Provider.of<CodeProvider>(context, listen: false).loadCode(example.code);
  }

  void _copyOutput(String text) {
    Clipboard.setData(ClipboardData(text: text));
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Sortie copiee'),
        duration: Duration(seconds: 1),
      ),
    );
  }

  void _shareCode() {
    Share.share(_codeController.text, subject: 'Mon script TounsiLang');
  }

  Future<String?> _askFileName() {
    final controller = TextEditingController(text: 'Mon script');
    return showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Nom du fichier'),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(hintText: 'ex: mon_projet'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Annuler'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, controller.text.trim()),
            child: const Text('Enregistrer'),
          ),
        ],
      ),
    );
  }

  Future<void> _saveCode() async {
    final codeProvider = Provider.of<CodeProvider>(context, listen: false);
    final fileProvider = Provider.of<FileProvider>(context, listen: false);
    final currentId = codeProvider.currentFileId;

    if (currentId != null && fileProvider.getFile(currentId) != null) {
      // Fichier déjà associé : on met simplement à jour son contenu.
      await fileProvider.updateFile(currentId, code: _codeController.text);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Fichier mis à jour ✅'),
          duration: Duration(seconds: 1),
        ),
      );
      return;
    }

    // Pas encore de fichier associé : demander un nom et en créer un.
    final name = await _askFileName();
    if (name == null || name.isEmpty) return;
    if (!mounted) return;
    final file = await fileProvider.createFile(name, _codeController.text);
    if (!mounted) return;
    codeProvider.setCurrentFileId(file.id);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Fichier enregistré ✅'),
        duration: Duration(seconds: 1),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final provider = Provider.of<CodeProvider>(context);
    final themeProvider = Provider.of<ThemeProvider>(context);
    final isDark = Theme.of(context).brightness == Brightness.dark;

    if (provider.loadToken != _lastLoadToken) {
      _lastLoadToken = provider.loadToken;
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_codeController.text != provider.code) {
          _codeController.text = provider.code;
        }
      });
    }

    final Color accent = isDark ? Colors.blue.shade400 : Colors.blue.shade700;
    final Color panelBg = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final Color panelBorder =
        isDark ? Colors.grey.shade800 : Colors.grey.shade300;
    final Color mutedText =
        isDark ? Colors.grey.shade500 : Colors.grey.shade600;

    return Scaffold(
      backgroundColor: Theme.of(context).scaffoldBackgroundColor,
      appBar: AppBar(
        title: const Text(
          'TounsiLang',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.save_outlined, color: Colors.white),
            tooltip: 'Sauvegarder',
            onPressed: _saveCode,
          ),
          PopupMenuButton<CodeExample>(
            icon: const Icon(Icons.menu_book, color: Colors.white),
            tooltip: 'Exemples',
            onSelected: _loadExample,
            itemBuilder: (context) => tounsiExamples
                .map((e) => PopupMenuItem(value: e, child: Text(e.title)))
                .toList(),
          ),
          IconButton(
            icon: const Icon(Icons.share, color: Colors.white),
            tooltip: 'Partager le code',
            onPressed: _shareCode,
          ),
          IconButton(
            icon: Icon(
              isDark ? Icons.light_mode : Icons.dark_mode,
              color: Colors.white,
            ),
            onPressed: () => themeProvider.toggleTheme(),
            tooltip: 'Basculer le theme',
          ),
          Container(
            margin: const EdgeInsets.only(right: 12),
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.white.withOpacity(0.15),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(color: Colors.white.withOpacity(0.3)),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: provider.mode,
                dropdownColor:
                    isDark ? Colors.grey.shade900 : Colors.blue.shade700,
                style: const TextStyle(color: Colors.white),
                items: const [
                  DropdownMenuItem(value: 'vm', child: Text('VM')),
                  DropdownMenuItem(
                    value: 'interpreter',
                    child: Text('Interpreteur'),
                  ),
                ],
                onChanged: (value) {
                  if (value != null) provider.setMode(value);
                },
              ),
            ),
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            flex: 2,
            child: Container(
              margin: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: panelBg,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: panelBorder, width: 1),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(isDark ? 0.4 : 0.08),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(16),
                child: CodeTheme(
                  data: CodeThemeData(
                    styles: isDark ? tounsiDarkTheme : tounsiLightTheme,
                  ),
                  child: CodeField(
                    controller: _codeController,
                    expands: true,
                    maxLines: null,
                    wrap: true,
                    background: panelBg,
                    textStyle: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 16,
                      height: 1.5,
                    ),
                    gutterStyle: GutterStyle(
                      showLineNumbers: true,
                      textStyle: TextStyle(
                        color: isDark
                            ? Colors.grey.shade600
                            : Colors.grey.shade400,
                        fontSize: 6,
                        fontFamily: 'monospace',
                      ),
                      background: isDark
                          ? const Color(0xFF2A2A2A)
                          : const Color(0xFFF0F0F0),
                      width: 70,
                    ),
                  ),
                ),
              ),
            ),
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: ElevatedButton.icon(
              onPressed:
                  provider.isLoading ? null : () => provider.runCode(),
              icon: provider.isLoading
                  ? const SizedBox(
                      width: 24,
                      height: 24,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        color: Colors.white,
                      ),
                    )
                  : const Icon(Icons.play_arrow, size: 28),
              label: Text(
                provider.isLoading ? 'EXECUTION...' : 'EXECUTER',
                style: const TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: accent,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(30),
                ),
                minimumSize: const Size(double.infinity, 56),
                elevation: 4,
              ),
            ),
          ),
          Expanded(
            flex: 1,
            child: Container(
              margin: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: panelBg,
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: panelBorder, width: 1),
              ),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.terminal, color: mutedText, size: 18),
                        const SizedBox(width: 8),
                        Text(
                          'SORTIE',
                          style: TextStyle(
                            color: mutedText,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1.2,
                          ),
                        ),
                        const Spacer(),
                        if (provider.result?.success == true)
                          IconButton(
                            icon: Icon(Icons.copy,
                                size: 18, color: mutedText),
                            tooltip: 'Copier la sortie',
                            onPressed: () =>
                                _copyOutput(provider.result!.output),
                          ),
                      ],
                    ),
                    Divider(color: panelBorder, height: 20),
                    if (provider.result != null) ...[
                      if (provider.result!.success)
                        SelectableText(
                          provider.result!.output.isEmpty
                              ? '(Aucune sortie)'
                              : provider.result!.output,
                          style: TextStyle(
                            fontFamily: 'monospace',
                            fontSize: 15,
                            color: isDark
                                ? Colors.grey.shade100
                                : Colors.grey.shade900,
                            height: 1.4,
                          ),
                        ),
                      if (provider.result!.error != null)
                        Container(
                          padding: const EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: Colors.grey
                                .withOpacity(isDark ? 0.15 : 0.08),
                            borderRadius: BorderRadius.circular(8),
                            border: Border.all(
                              color: Colors.grey.withOpacity(0.4),
                            ),
                          ),
                          child: Row(
                            children: [
                              Icon(
                                Icons.error_outline,
                                color: isDark
                                    ? Colors.grey.shade300
                                    : Colors.grey.shade800,
                                size: 20,
                              ),
                              const SizedBox(width: 8),
                              Expanded(
                                child: SelectableText(
                                  provider.result!.error!,
                                  style: TextStyle(
                                    color: isDark
                                        ? Colors.grey.shade200
                                        : Colors.grey.shade900,
                                    fontFamily: 'monospace',
                                    fontSize: 14,
                                  ),
                                ),
                              ),
                            ],
                          ),
                        ),
                    ] else if (provider.isLoading) ...[
                      Row(
                        children: [
                          SizedBox(
                            width: 16,
                            height: 16,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              color: accent,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Text(
                            'Execution en cours...',
                            style: TextStyle(color: mutedText),
                          ),
                        ],
                      ),
                    ] else ...[
                      Text(
                        "Le resultat s'affichera ici.",
                        style: TextStyle(color: mutedText),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
