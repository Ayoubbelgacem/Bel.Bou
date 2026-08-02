import 'package:flutter/material.dart';
import '../services/api_service.dart';
import '../models/code_result.dart';

class CodeProvider extends ChangeNotifier {
  String _code = '';
  bool _isLoading = false;
  CodeResult? _result;
  String _mode = 'vm';

  // ✅ Incrémenté uniquement lors d'un chargement externe (Exemples, Accueil,
  // Mes fichiers...) pour que l'EditorScreen sache qu'il doit rafraîchir son
  // CodeController.
  int _loadToken = 0;

  // ✅ Id du fichier (BouFile) actuellement ouvert dans l'éditeur, ou null
  // si le script en cours n'a jamais été sauvegardé / vient d'un exemple.
  String? _currentFileId;

  String get code => _code;
  bool get isLoading => _isLoading;
  CodeResult? get result => _result;
  String get mode => _mode;
  int get loadToken => _loadToken;
  String? get currentFileId => _currentFileId;

  /// Mise à jour normale (frappe utilisateur dans l'éditeur).
  /// Ne touche pas currentFileId : on continue d'éditer le même fichier.
  void updateCode(String newCode) {
    _code = newCode;
    notifyListeners();
  }

  /// Chargement externe d'un script (depuis Exemples, Accueil, Mes fichiers).
  /// fileId doit être fourni si le script correspond à un fichier sauvegardé,
  /// sinon laissez-le à null (ex: exemple, nouveau script vide).
  void loadCode(String newCode, {String? fileId}) {
    _code = newCode;
    _currentFileId = fileId;
    _loadToken++;
    notifyListeners();
  }

  void setCurrentFileId(String? id) {
    _currentFileId = id;
    notifyListeners();
  }

  void setMode(String newMode) {
    _mode = newMode;
    notifyListeners();
  }

  Future<void> runCode() async {
    if (_code.trim().isEmpty) {
      _result = CodeResult(
        success: false,
        output: '',
        error: 'Le code est vide',
      );
      notifyListeners();
      return;
    }

    _isLoading = true;
    _result = null;
    notifyListeners();

    try {
      final apiService = ApiService();
      _result = await apiService.executeCode(_code, mode: _mode);
    } catch (e) {
      _result = CodeResult(
        success: false,
        output: '',
        error: 'Erreur: $e',
      );
    }

    _isLoading = false;
    notifyListeners();
  }

  void clearResult() {
    _result = null;
    notifyListeners();
  }
}
