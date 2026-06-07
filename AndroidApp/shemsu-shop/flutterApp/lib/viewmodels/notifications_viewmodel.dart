import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../data/api_service.dart';

class NotificationsViewModel with ChangeNotifier {
  final ApiService _api;

  NotificationsViewModel(this._api);

  List<AppNotification> _notifications = [];
  List<AppNotification> get notifications => _notifications;

  int get unreadCount => _notifications.where((n) => !n.read).length;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  Future<void> loadNotifications(int userId) async {
    _isLoading = true;
    notifyListeners();
    try {
      _notifications = await _api.getNotifications(userId);
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }

  Future<void> markRead(int id) async {
    try {
      await _api.markNotificationRead(id);
      final idx = _notifications.indexWhere((n) => n.id == id);
      if (idx >= 0) {
        _notifications[idx] = AppNotification(
          id: _notifications[idx].id,
          title: _notifications[idx].title,
          body: _notifications[idx].body,
          orderGroup: _notifications[idx].orderGroup,
          read: true,
          createdAt: _notifications[idx].createdAt,
        );
        notifyListeners();
      }
    } catch (_) {}
  }
}
