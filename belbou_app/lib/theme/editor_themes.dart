import 'package:flutter/material.dart';

/// Thème de coloration syntaxique utilisé par CodeTheme/CodeThemeData
/// (clés = className définis dans lib/languages/tounsilang.dart)
final Map<String, TextStyle> tounsiDarkTheme = {
  'root': const TextStyle(
    color: Color(0xFFE0E0E0),
    backgroundColor: Color(0xFF1E1E1E),
  ),
  'comment': TextStyle(color: Colors.grey.shade600, fontStyle: FontStyle.italic),
  'keyword': TextStyle(color: Colors.blue.shade300, fontWeight: FontWeight.bold),
  'built_in': TextStyle(color: Colors.lightBlue.shade200),
  'function': TextStyle(color: Colors.blue.shade200, fontWeight: FontWeight.w600),
  'string': TextStyle(color: Colors.grey.shade300),
  'number': TextStyle(color: Colors.blue.shade100),
};

final Map<String, TextStyle> tounsiLightTheme = {
  'root': const TextStyle(
    color: Color(0xFF1A1A1A),
    backgroundColor: Colors.white,
  ),
  'comment': TextStyle(color: Colors.grey.shade500, fontStyle: FontStyle.italic),
  'keyword': TextStyle(color: Colors.blue.shade800, fontWeight: FontWeight.bold),
  'built_in': TextStyle(color: Colors.blue.shade600),
  'function': TextStyle(color: Colors.blue.shade700, fontWeight: FontWeight.w600),
  'string': TextStyle(color: Colors.grey.shade800),
  'number': TextStyle(color: Colors.blue.shade900),
};
