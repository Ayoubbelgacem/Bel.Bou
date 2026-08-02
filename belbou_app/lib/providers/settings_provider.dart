import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../services/api_service.dart';

class SettingsProvider extends ChangeNotifier {
  static const _keyServerUrl = 'server_url';
  static const _keyDefaultMode = 'default_mode';

  String _serverUrl = ApiService.baseUrl;
  String _defaultMode = 'vm';
  bool _isLoaded = false;

  String get serverUrl => _serverUrl;
  String get defaultMode => _defaultMode;
  bool get isLoaded => _isLoaded;

  SettingsProvider() {
    _load();
  }

  Future<void> _load() async {
    final prefs = await SharedPreferences.getInstance();
    _serverUrl = prefs.getString(_keyServerUrl) ?? ApiService.baseUrl;
    _defaultMode = prefs.getString(_keyDefaultMode) ?? 'vm';
    ApiService.baseUrl = _serverUrl;
    _isLoaded = true;
    notifyListeners();
  }

  Future<void> updateServerUrl(String url) async {
    _serverUrl = url;
    ApiService.baseUrl = url;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyServerUrl, url);
    notifyListeners();
  }

  Future<void> updateDefaultMode(String mode) async {
    _defaultMode = mode;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_keyDefaultMode, mode);
    notifyListeners();
  }
}
