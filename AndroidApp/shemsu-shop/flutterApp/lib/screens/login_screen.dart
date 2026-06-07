import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/auth_viewmodel.dart';
import '../core/theme.dart';
import '../core/constants.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> with SingleTickerProviderStateMixin {
  final _usernameCtrl = TextEditingController();
  final _otpCtrl = TextEditingController();
  late AnimationController _animCtrl;
  late Animation<Offset> _slideIn;

  @override
  void initState() {
    super.initState();
    _animCtrl = AnimationController(duration: const Duration(milliseconds: 400), vsync: this);
    _slideIn = Tween<Offset>(begin: const Offset(0, 0.3), end: Offset.zero).animate(CurvedAnimation(parent: _animCtrl, curve: Curves.easeOut));
  }

  @override
  void dispose() {
    _usernameCtrl.dispose();
    _otpCtrl.dispose();
    _animCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      body: Consumer<AuthViewModel>(
        builder: (context, auth, _) {
          if (auth.state == AuthState.authenticated) {
            WidgetsBinding.instance.addPostFrameCallback((_) => Navigator.pushReplacementNamed(context, '/home'));
          }

          return SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const SizedBox(height: 40),
                  Container(
                    width: 80, height: 80,
                    decoration: BoxDecoration(
                      color: AppTheme.primaryContainerOrange,
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: const Icon(Icons.store, color: Colors.white, size: 40),
                  ),
                  const SizedBox(height: 24),
                  const Text('Welcome', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
                  const SizedBox(height: 4),
                  const Text('Sign in with your Telegram username', style: TextStyle(fontSize: 14, color: AppTheme.onSurfaceVariant)),
                  const SizedBox(height: 32),

                  if (!auth.otpSent) ..._buildUsernameInput(auth) else ..._buildOtpInput(auth),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  List<Widget> _buildUsernameInput(AuthViewModel auth) {
    return [
      TextField(
        controller: _usernameCtrl,
        decoration: const InputDecoration(
          labelText: 'Telegram Username',
          hintText: '@your_username',
          prefixIcon: Icon(Icons.telegram, color: AppTheme.primaryOrange),
        ),
        style: const TextStyle(color: AppTheme.onSurface),
        textInputAction: TextInputAction.done,
        onSubmitted: (_) => _sendOtp(auth),
      ),
      const SizedBox(height: 8),
      Text('Enter the same username you used to register with the bot.', style: TextStyle(fontSize: 12, color: AppTheme.onSurfaceVariant.withOpacity(0.7))),
      const SizedBox(height: 24),
      _buildButton('Send OTP', auth.isLoading, () => _sendOtp(auth)),
      if (auth.error != null) _buildError(auth.error!),
      const SizedBox(height: 32),
      Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Flexible(
            child: Text("Don't have an account?", style: TextStyle(color: AppTheme.onSurfaceVariant.withOpacity(0.7))),
          ),
          TextButton(
            onPressed: () {},
            child: const Text('Register via @sshopdelivery_bot', style: TextStyle(color: AppTheme.primaryOrange)),
          ),
        ],
      ),
    ];
  }

  List<Widget> _buildOtpInput(AuthViewModel auth) {
    if (_animCtrl.status == AnimationStatus.dismissed) _animCtrl.forward();
    return [
      SlideTransition(
        position: _slideIn,
        child: Column(
          children: [
            const Text('Enter the 6-digit code sent to your Telegram.', style: TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 14)),
            const SizedBox(height: 16),
            TextField(
              controller: _otpCtrl,
              decoration: const InputDecoration(
                labelText: 'OTP Code',
                hintText: '000000',
                prefixIcon: Icon(Icons.pin, color: AppTheme.primaryOrange),
              ),
              style: const TextStyle(color: AppTheme.onSurface, fontSize: 24, letterSpacing: 8),
              keyboardType: TextInputType.number,
              maxLength: 6,
              textAlign: TextAlign.center,
              textInputAction: TextInputAction.done,
              onSubmitted: (_) => _verifyOtp(auth),
            ),
            const SizedBox(height: 24),
            _buildButton('Verify & Continue', auth.isLoading, () => _verifyOtp(auth)),
            if (auth.error != null) _buildError(auth.error!),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () {
                auth.resetOtp();
                _animCtrl.reset();
              },
              child: const Text('Change username', style: TextStyle(color: AppTheme.onSurfaceVariant)),
            ),
          ],
        ),
      ),
    ];
  }

  Widget _buildButton(String text, bool loading, VoidCallback onTap) {
    return SizedBox(
      width: double.infinity,
      child: ElevatedButton(
        onPressed: loading ? null : onTap,
        child: loading
          ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
          : Text(text),
      ),
    );
  }

  Widget _buildError(String error) {
    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: Text(error, style: const TextStyle(color: AppTheme.statusError, fontSize: 13), textAlign: TextAlign.center),
    );
  }

  void _sendOtp(AuthViewModel auth) {
    final username = _usernameCtrl.text.trim();
    if (username.isEmpty) return;
    auth.requestOtp(username);
  }

  void _verifyOtp(AuthViewModel auth) {
    final otp = _otpCtrl.text.trim();
    if (otp.length != 6) return;
    auth.verifyOtp(otp);
  }
}
