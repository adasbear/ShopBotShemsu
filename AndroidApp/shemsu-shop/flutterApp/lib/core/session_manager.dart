import 'package:shared_preferences/shared_preferences.dart';

class SessionManager {
  static const _keyUserId = 'user_id';
  static const _keyUsername = 'username';
  static const _keyFullName = 'full_name';
  static const _keyToken = 'token';

  final SharedPreferences _prefs;

  SessionManager(this._prefs);

  int? get userId => _prefs.getInt(_keyUserId);
  String? get username => _prefs.getString(_keyUsername);
  String? get fullName => _prefs.getString(_keyFullName);
  String? get token => _prefs.getString(_keyToken);
  bool get isLoggedIn => userId != null && token != null;

  Future<void> saveSession({
    required int userId,
    required String username,
    required String fullName,
    required String token,
  }) async {
    await _prefs.setInt(_keyUserId, userId);
    await _prefs.setString(_keyUsername, username);
    await _prefs.setString(_keyFullName, fullName);
    await _prefs.setString(_keyToken, token);
  }

  Future<void> updateName(String fullName) async {
    await _prefs.setString(_keyFullName, fullName);
  }

  Future<void> clearSession() async {
    await _prefs.remove(_keyUserId);
    await _prefs.remove(_keyUsername);
    await _prefs.remove(_keyFullName);
    await _prefs.remove(_keyToken);
  }
}
