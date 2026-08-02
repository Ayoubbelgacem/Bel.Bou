import 'dart:io';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:file_picker/file_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';
import '../models/bou_file.dart';
import '../providers/file_provider.dart';
import '../providers/code_provider.dart';

class FilesScreen extends StatelessWidget {
  final void Function(int tabIndex) onNavigateToTab;

  const FilesScreen({super.key, required this.onNavigateToTab});

  Future<String?> _promptName(
    BuildContext context, {
    String initialValue = '',
    required String title,
  }) {
    final controller = TextEditingController(text: initialValue);
    return showDialog<String>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: Text(title),
        content: TextField(
          controller: controller,
          autofocus: true,
          decoration: const InputDecoration(hintText: 'Nom du fichier'),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Annuler'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, controller.text.trim()),
            child: const Text('Valider'),
          ),
        ],
      ),
    );
  }

  Future<void> _createNewFile(BuildContext context) async {
    final name = await _promptName(
      context,
      title: 'Nouveau fichier',
      initialValue: 'Mon script',
    );
    if (name == null || name.isEmpty) return;
    if (!context.mounted) return;
    final file = await context.read<FileProvider>().createFile(
          name,
          '# ${name}\n\n',
        );
    if (!context.mounted) return;
    context.read<CodeProvider>().loadCode(file.code, fileId: file.id);
    onNavigateToTab(1);
  }

  Future<void> _openFile(BuildContext context, BouFile file) async {
    context.read<CodeProvider>().loadCode(file.code, fileId: file.id);
    onNavigateToTab(1);
  }

  Future<void> _renameFile(BuildContext context, BouFile file) async {
    final name = await _promptName(
      context,
      title: 'Renommer',
      initialValue: file.name,
    );
    if (name == null || name.isEmpty) return;
    if (!context.mounted) return;
    await context.read<FileProvider>().updateFile(file.id, name: name);
  }

  Future<void> _deleteFile(BuildContext context, BouFile file) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Supprimer ?'),
        content: Text('Supprimer définitivement "${file.name}" ?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Annuler'),
          ),
          FilledButton(
            style: FilledButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Supprimer'),
          ),
        ],
      ),
    );
    if (confirmed != true) return;
    if (!context.mounted) return;
    final codeProvider = context.read<CodeProvider>();
    await context.read<FileProvider>().deleteFile(file.id);
    // Si le fichier supprimé était ouvert dans l'éditeur, on détache le lien.
    if (codeProvider.currentFileId == file.id) {
      codeProvider.setCurrentFileId(null);
    }
  }

  Future<void> _exportFile(BuildContext context, BouFile file) async {
    try {
      final dir = await getTemporaryDirectory();
      final safeName = file.name.replaceAll(RegExp(r'[^\w\-]'), '_');
      final path = '${dir.path}/$safeName.bou';
      await File(path).writeAsString(file.code);
      await Share.shareXFiles(
        [XFile(path)],
        text: 'Script TounsiLang : ${file.name}',
      );
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur export: $e')),
      );
    }
  }

  Future<void> _importFile(BuildContext context) async {
    final result = await FilePicker.platform.pickFiles(
      type: FileType.custom,
      allowedExtensions: ['bou', 'txt'],
    );
    if (result == null) return;
    final pickedPath = result.files.single.path;
    if (pickedPath == null) return;

    try {
      final content = await File(pickedPath).readAsString();
      final rawName = result.files.single.name;
      final name = rawName.replaceAll(RegExp(r'\.(bou|txt)$'), '');
      if (!context.mounted) return;
      await context.read<FileProvider>().createFile(name, content);
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('"$name" importé')),
      );
    } catch (e) {
      if (!context.mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur import: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final fileProvider = context.watch<FileProvider>();
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final Color cardBg = isDark ? const Color(0xFF1E1E1E) : Colors.white;
    final Color cardBorder =
        isDark ? Colors.grey.shade800 : Colors.grey.shade300;
    final Color mutedText =
        isDark ? Colors.grey.shade500 : Colors.grey.shade600;

    if (!fileProvider.isLoaded) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final files = fileProvider.files;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mes fichiers',
            style: TextStyle(fontWeight: FontWeight.bold)),
        actions: [
          IconButton(
            icon: const Icon(Icons.file_upload_outlined),
            tooltip: 'Importer un fichier .bou',
            onPressed: () => _importFile(context),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () => _createNewFile(context),
        icon: const Icon(Icons.add),
        label: const Text('Nouveau'),
      ),
      body: files.isEmpty
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.folder_open, size: 56, color: mutedText),
                    const SizedBox(height: 16),
                    Text(
                      'Aucun fichier sauvegardé.\nCrée un nouveau script ou sauvegarde\nun script depuis l\'éditeur (icône 💾).',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: mutedText),
                    ),
                  ],
                ),
              ),
            )
          : ListView.separated(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 90),
              itemCount: files.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final file = files[index];
                return Card(
                  color: cardBg,
                  elevation: 0,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14),
                    side: BorderSide(color: cardBorder),
                  ),
                  child: ListTile(
                    contentPadding: const EdgeInsets.symmetric(
                      horizontal: 14,
                      vertical: 4,
                    ),
                    leading: const Icon(Icons.description_outlined),
                    title: Text(
                      file.name,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    subtitle: Text(
                      'Modifié le ${file.formattedDate}',
                      style: TextStyle(color: mutedText, fontSize: 12),
                    ),
                    onTap: () => _openFile(context, file),
                    trailing: PopupMenuButton<String>(
                      onSelected: (action) {
                        switch (action) {
                          case 'open':
                            _openFile(context, file);
                            break;
                          case 'rename':
                            _renameFile(context, file);
                            break;
                          case 'duplicate':
                            context.read<FileProvider>().duplicateFile(file.id);
                            break;
                          case 'export':
                            _exportFile(context, file);
                            break;
                          case 'delete':
                            _deleteFile(context, file);
                            break;
                        }
                      },
                      itemBuilder: (context) => const [
                        PopupMenuItem(
                          value: 'open',
                          child: Text('Ouvrir'),
                        ),
                        PopupMenuItem(
                          value: 'rename',
                          child: Text('Renommer'),
                        ),
                        PopupMenuItem(
                          value: 'duplicate',
                          child: Text('Dupliquer'),
                        ),
                        PopupMenuItem(
                          value: 'export',
                          child: Text('Exporter (.bou)'),
                        ),
                        PopupMenuItem(
                          value: 'delete',
                          child: Text(
                            'Supprimer',
                            style: TextStyle(color: Colors.red),
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
