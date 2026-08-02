import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'providers/code_provider.dart';
import 'providers/theme_provider.dart';
import 'providers/settings_provider.dart';
import 'providers/file_provider.dart';
import 'screens/main_navigation.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => CodeProvider()),
        ChangeNotifierProvider(create: (_) => ThemeProvider()),
        ChangeNotifierProvider(create: (_) => SettingsProvider()),
        ChangeNotifierProvider(create: (_) => FileProvider()),
      ],
      child: Consumer<ThemeProvider>(
        builder: (context, themeProvider, _) {
          return MaterialApp(
            title: 'TounsiLang',
            debugShowCheckedModeBanner: false,
            themeMode: themeProvider.themeMode,
            theme: ThemeData(
              brightness: Brightness.light,
              primaryColor: Colors.blue.shade700,
              colorScheme: ColorScheme.light(
                primary: Colors.blue.shade700,
                secondary: Colors.blue.shade400,
                surface: Colors.white,
                background: const Color(0xFFF2F3F5),
              ),
              scaffoldBackgroundColor: const Color(0xFFF2F3F5),
              useMaterial3: true,
              fontFamily: 'RobotoMono',
              appBarTheme: AppBarTheme(
                backgroundColor: Colors.blue.shade700,
                foregroundColor: Colors.white,
                elevation: 0,
              ),
            ),
            darkTheme: ThemeData(
              brightness: Brightness.dark,
              primaryColor: Colors.blue.shade600,
              colorScheme: ColorScheme.dark(
                primary: Colors.blue.shade600,
                secondary: Colors.blue.shade300,
                surface: const Color(0xFF1E1E1E),
                background: const Color(0xFF121212),
              ),
              scaffoldBackgroundColor: const Color(0xFF121212),
              useMaterial3: true,
              fontFamily: 'RobotoMono',
              appBarTheme: AppBarTheme(
                backgroundColor: Colors.grey.shade900,
                foregroundColor: Colors.white,
                elevation: 0,
              ),
            ),
            home: const MainNavigation(),
          );
        },
      ),
    );
  }
}