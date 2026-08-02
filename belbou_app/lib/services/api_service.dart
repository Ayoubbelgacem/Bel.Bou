import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/code_result.dart';

class ApiService {
  // ✅ Modifiable depuis l'écran Paramètres (persisté via SettingsProvider).
  // Valeur par défaut :
  // - Windows / Chrome local : http://localhost:8000
  // - Émulateur Android : http://10.0.2.2:8000
  // - Appareil réel (même réseau) : http://<IP_DE_TA_MACHINE>:8000
  static String baseUrl = 'http://localhost:8000';

  Future<CodeResult> executeCode(String code, {String mode = 'vm'}) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/run'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'code': code,
          'mode': mode,
          'debug': false,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return CodeResult.fromJson(data);
      } else {
        return CodeResult(
          success: false,
          output: '',
          error: 'Erreur serveur: ${response.statusCode}',
        );
      }
    } catch (e) {
      return CodeResult(
        success: false,
        output: '',
        error: 'Erreur de connexion: $e',
      );
    }
  }

  Future<bool> testConnection() async {
    try {
      final response = await http
          .get(Uri.parse('$baseUrl/health'))
          .timeout(const Duration(seconds: 4));
      return response.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}