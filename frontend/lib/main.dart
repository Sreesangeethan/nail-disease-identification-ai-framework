import 'package:flutter/material.dart';

import 'screens/home_screen.dart';
import 'screens/login_screen.dart';
import 'services/api_service.dart';

void main() {
  runApp(NailDiseaseApp(apiService: ApiService()));
}

class NailDiseaseApp extends StatefulWidget {
  const NailDiseaseApp({super.key, required this.apiService});

  final ApiService apiService;

  @override
  State<NailDiseaseApp> createState() => _NailDiseaseAppState();
}

class _NailDiseaseAppState extends State<NailDiseaseApp> {
  void _handleAuthenticated() {
    setState(() {});
  }

  void _handleLogout() {
    widget.apiService.logout();
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Nail Disease Detection',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF2563EB),
          brightness: Brightness.light,
        ),
        inputDecorationTheme: const InputDecorationTheme(
          border: OutlineInputBorder(),
        ),
        cardTheme: CardThemeData(
          elevation: 0,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0x14000000)),
          ),
        ),
      ),
      home: widget.apiService.isAuthenticated
          ? HomeScreen(
              apiService: widget.apiService,
              onLogout: _handleLogout,
            )
          : LoginScreen(
              apiService: widget.apiService,
              onAuthenticated: _handleAuthenticated,
            ),
    );
  }
}
