import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../data/api_service.dart';

class ChatViewModel with ChangeNotifier {
  final ApiService _api;

  ChatViewModel(this._api);

  List<ContactMessage> _messages = [];
  List<ContactMessage> get messages => _messages;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  Future<void> sendMessage(int userId, String username, String text) async {
    final msg = ContactMessage(id: DateTime.now().millisecondsSinceEpoch.toString(), text: text, isUser: true);
    _messages.add(msg);
    notifyListeners();

    _isLoading = true;
    notifyListeners();

    try {
      await _api.contactAdmin(userId, username, text);
    } catch (_) {}

    _isLoading = false;
    notifyListeners();
  }
}
