import 'package:flutter/foundation.dart';
import '../data/api_service.dart';
import '../core/session_manager.dart';
import '../core/constants.dart';
import 'package:dio/dio.dart';

enum AuthState { uninitialized, unauthenticated, authenticated }

class AuthViewModel with ChangeNotifier {
  final ApiService _api;
  final SessionManager _session;

  AuthViewModel(this._api, this._session);

  AuthState _state = AuthState.uninitialized;
  AuthState get state => _state;

  String _username = '';
  String get username => _username;

  String _fullName = '';
  String get fullName => _fullName;

  int? _userId;
  int? get userId => _userId;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _error;
  String? get error => _error;

  bool _otpSent = false;
  bool get otpSent => _otpSent;

  Future<void> tryAutoLogin() async {
    if (_session.isLoggedIn) {
      _userId = _session.userId;
      _username = _session.username ?? '';
      _fullName = _session.fullName ?? '';
      try {
        final session = await _api.checkSession(_session.token!);
        _userId = session.userId;
        _username = session.username;
        _fullName = session.fullName;
        _state = AuthState.authenticated;
      } catch (_) {
        await _session.clearSession();
        _state = AuthState.unauthenticated;
      }
    } else {
      _state = AuthState.unauthenticated;
    }
    notifyListeners();
  }

  Future<void> requestOtp(String username) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    String cleanUsername = username.trim();
    if (cleanUsername.startsWith('@')) {
      cleanUsername = cleanUsername.substring(1);
    }

    try {
      final res = await _api.requestOtp(cleanUsername);
      if (res.success) {
        _username = cleanUsername;
        _otpSent = true;
      } else {
        _error = res.error ?? 'Failed to send OTP';
      }
    } on DioException catch (e) {
      if (e.response?.data is Map && (e.response!.data as Map).containsKey('error')) {
        _error = (e.response!.data as Map)['error'].toString();
      } else {
        _error = 'Network error: ${e.message}';
      }
    } catch (e) {
      _error = 'Unexpected error: $e';
    }

    _isLoading = false;
    notifyListeners();
  }

  Future<bool> verifyOtp(String otp) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final res = await _api.verifyOtp(_username, otp.trim());
      if (res.success && res.sessionToken != null) {
        final session = await _api.checkSession(res.sessionToken!);
        _userId = session.userId;
        _fullName = session.fullName;
        await _session.saveSession(
          userId: session.userId,
          username: session.username,
          fullName: session.fullName,
          token: res.sessionToken!,
        );
        _state = AuthState.authenticated;
        _isLoading = false;
        notifyListeners();
        return true;
      } else {
        _error = res.error ?? 'Invalid OTP';
        _isLoading = false;
        notifyListeners();
        return false;
      }
    } on DioException catch (e) {
      if (e.response?.data is Map && (e.response!.data as Map).containsKey('error')) {
        _error = (e.response!.data as Map)['error'].toString();
      } else {
        _error = 'Network error: ${e.message}';
      }
    } catch (e) {
      _error = 'Unexpected error: $e';
    }

    _isLoading = false;
    notifyListeners();
    return false;
  }

  Future<void> updateName(String name) async {
    if (_userId == null) return;
    try {
      await _api.updateProfile(_userId!, name);
      _fullName = name;
      await _session.updateName(name);
      notifyListeners();
    } catch (_) {}
  }

  Future<void> logout() async {
    await _session.clearSession();
    _state = AuthState.unauthenticated;
    _username = '';
    _fullName = '';
    _userId = null;
    _otpSent = false;
    _error = null;
    notifyListeners();
  }

  void resetOtp() {
    _otpSent = false;
    _error = null;
    notifyListeners();
  }
}
