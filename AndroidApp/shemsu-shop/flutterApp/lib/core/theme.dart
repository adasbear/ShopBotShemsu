import 'package:flutter/material.dart';

class AppTheme {
  static const Color backgroundMidnight = Color(0xFF131313);
  static const Color surfaceContainerLow = Color(0xFF1C1B1B);
  static const Color surfaceElevated = Color(0xFF1E1E1E);
  static const Color surfaceDeep = Color(0xFF080808);
  static const Color primaryOrange = Color(0xFFFFB68A);
  static const Color primaryContainerOrange = Color(0xFFF27A18);
  static const Color onPrimary = Color(0xFF522300);
  static const Color secondaryGold = Color(0xFFE9C349);
  static const Color onSurface = Color(0xFFE5E2E1);
  static const Color onSurfaceVariant = Color(0xFFDEC1B0);
  static const Color accentGold = Color(0xFFFFD700);
  static const Color statusPending = Color(0xFFFFB800);
  static const Color statusAccepted = Color(0xFF4CAF50);
  static const Color statusReady = Color(0xFFFF6B00);
  static const Color statusError = Color(0xFFFF4B4B);
  static const Color surfaceGlass = Color(0x1FFFFFFF);

  static ThemeData get darkTheme => ThemeData(
    useMaterial3: true,
    brightness: Brightness.dark,
    colorScheme: const ColorScheme.dark(
      primary: primaryOrange,
      onPrimary: onPrimary,
      primaryContainer: primaryContainerOrange,
      secondary: secondaryGold,
      background: backgroundMidnight,
      surface: surfaceContainerLow,
      onSurface: onSurface,
      onSurfaceVariant: onSurfaceVariant,
      error: statusError,
    ),
    scaffoldBackgroundColor: backgroundMidnight,
    appBarTheme: const AppBarTheme(
      backgroundColor: Colors.transparent,
      elevation: 0,
      centerTitle: true,
      iconTheme: IconThemeData(color: onSurface),
      titleTextStyle: TextStyle(
        color: onSurface,
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
    ),
    bottomNavigationBarTheme: const BottomNavigationBarThemeData(
      backgroundColor: surfaceDeep,
      selectedItemColor: primaryOrange,
      unselectedItemColor: onSurfaceVariant,
      type: BottomNavigationBarType.fixed,
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: accentGold,
        foregroundColor: Colors.black,
        padding: const EdgeInsets.symmetric(vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: surfaceContainerLow,
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: BorderSide.none,
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(12),
        borderSide: const BorderSide(color: primaryOrange),
      ),
      labelStyle: const TextStyle(color: onSurfaceVariant),
      hintStyle: const TextStyle(color: onSurfaceVariant),
    ),
  );
}
