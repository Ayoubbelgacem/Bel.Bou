import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../models/bou_file.dart';

class FileProvider extends ChangeNotifier {
  static const _key = 'bou_files';

  List<BouFile> _files = [];
  bool _isLoaded = false;

  /// Triés du plus récent au plus ancien.
  List<BouFile> get files {
    final sorted = [..._files];
    sorted.sort((a, b) => b.updatedAt.compareTo(a.updatedAt));
    return sorted;
  }

  bool get isLoaded => _isLoaded;

  FileProvider() {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_key);
    if (raw != null && raw.isNotEmpty) {
      final list = jsonDecode(raw) as List;
      _files = list
          .map((e) => BouFile.fromJson(e as Map<String, dynamic>))
          .toList();
    }
    _isLoaded = true;
    notifyListeners();
  }

  Future<void> _persist() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(
      _key,
      jsonEncode(_files.map((f) => f.toJson()).toList()),
    );
  }

  Future<BouFile> createFile(String name, String code) async {
    final file = BouFile(
      id: DateTime.now().microsecondsSinceEpoch.toString(),
      name: name.isEmpty ? 'Sans titre' : name,
      code: code,
      updatedAt: DateTime.now().millisecondsSinceEpoch,
    );
    _files.add(file);
    await _persist();
    notifyListeners();
    return file;
  }

  Future<void> updateFile(String id, {String? name, String? code}) async {
    final index = _files.indexWhere((f) => f.id == id);
    if (index == -1) return;
    _files[index] = _files[index].copyWith(
      name: name,
      code: code,
      updatedAt: DateTime.now().millisecondsSinceEpoch,
    );
    await _persist();
    notifyListeners();
  }

  Future<void> deleteFile(String id) async {
    _files.removeWhere((f) => f.id == id);
    await _persist();
    notifyListeners();
  }

  Future<BouFile> duplicateFile(String id) async {
    final original = _files.firstWhere((f) => f.id == id);
    return createFile('${original.name} (copie)', original.code);
  }

  BouFile? getFile(String id) {
    for (final f in _files) {
      if (f.id == id) return f;
    }
    return null;
  }
}
