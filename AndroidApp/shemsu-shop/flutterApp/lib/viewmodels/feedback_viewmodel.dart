import 'package:flutter/foundation.dart';
import '../data/api_service.dart';

class FeedbackViewModel with ChangeNotifier {
  final ApiService _api;

  FeedbackViewModel(this._api);

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  bool _submitted = false;
  bool get submitted => _submitted;

  String? _error;
  String? get error => _error;

  Future<bool> submit(int userId, int rating, String comment) async {
    _isLoading = true;
    _error = null;
    notifyListeners();
    try {
      final res = await _api.submitFeedback(userId, rating, comment);
      if (res.success) {
        _submitted = true;
        _isLoading = false;
        notifyListeners();
        return true;
      }
      _error = res.error;
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
    return false;
  }
}
