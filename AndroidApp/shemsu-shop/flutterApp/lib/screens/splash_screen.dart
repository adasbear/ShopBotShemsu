import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/auth_viewmodel.dart';
import '../core/theme.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeIn;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(duration: const Duration(milliseconds: 1500), vsync: this);
    _fadeIn = CurvedAnimation(parent: _controller, curve: Curves.easeIn);
    _controller.forward();

    Future.delayed(const Duration(milliseconds: 1200), () {
      if (mounted) {
        context.read<AuthViewModel>().tryAutoLogin();
      }
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      body: Consumer<AuthViewModel>(
        builder: (context, auth, _) {
          if (auth.state == AuthState.authenticated) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              Navigator.pushReplacementNamed(context, '/home');
            });
          } else if (auth.state == AuthState.unauthenticated) {
            WidgetsBinding.instance.addPostFrameCallback((_) {
              Navigator.pushReplacementNamed(context, '/login');
            });
          }

          return Center(
            child: FadeTransition(
              opacity: _fadeIn,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Container(
                    width: 100,
                    height: 100,
                    decoration: BoxDecoration(
                      color: AppTheme.primaryContainerOrange,
                      borderRadius: BorderRadius.circular(24),
                    ),
                    child: const Icon(Icons.store, color: Colors.white, size: 50),
                  ),
                  const SizedBox(height: 24),
                  const Text('Shemsu Shop', style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold, color: AppTheme.onSurface, fontFamily: 'serif')),
                  const SizedBox(height: 8),
                  const Text('Gourmet Kitchen', style: TextStyle(fontSize: 16, color: AppTheme.onSurfaceVariant)),
                  const SizedBox(height: 48),
                  const CircularProgressIndicator(color: AppTheme.accentGold),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}
