import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../data/api_service.dart';

class OrdersViewModel with ChangeNotifier {
  final ApiService _api;

  OrdersViewModel(this._api);

  List<OrderGroup> _orders = [];
  List<OrderGroup> get orders => _orders;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _error;
  String? get error => _error;

  Future<void> loadOrders(int userId) async {
    _isLoading = true;
    notifyListeners();
    try {
      _orders = await _api.getOrders(userId);
    } catch (e) {
      _error = e.toString();
    }
    _isLoading = false;
    notifyListeners();
  }

  Future<PlaceOrderResponse> placeOrder({
    required int userId,
    String? username,
    String? fullName,
    required List<CartItem> items,
    required String paymentMethod,
    int? paymentAccountId,
    String? confirmation,
    String? comment,
  }) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await _api.placeOrder(
        userId: userId,
        username: username,
        fullName: fullName,
        items: items,
        paymentMethod: paymentMethod,
        paymentAccountId: paymentAccountId,
        confirmation: confirmation,
        comment: comment,
      );
      _isLoading = false;
      notifyListeners();
      return res;
    } catch (e) {
      _isLoading = false;
      notifyListeners();
      return PlaceOrderResponse(success: false, error: e.toString());
    }
  }

  Future<bool> cancelOrder(String orderGroup) async {
    try {
      final res = await _api.cancelOrder(orderGroup);
      if (res.success) {
        _orders.removeWhere((o) => o.orderGroup == orderGroup);
        notifyListeners();
        return true;
      }
      _error = res.error;
      notifyListeners();
      return false;
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    }
  }

  List<OrderGroup> get activeOrders =>
    _orders.where((o) => o.status == 'Pending' || o.status == 'Accepted').toList();

  List<OrderGroup> get historyOrders =>
    _orders.where((o) => o.status != 'Pending' && o.status != 'Accepted').toList();
}
