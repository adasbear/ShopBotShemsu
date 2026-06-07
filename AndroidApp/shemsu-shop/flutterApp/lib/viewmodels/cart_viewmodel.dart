import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../data/local_db.dart';

class CartViewModel with ChangeNotifier {
  final LocalDb _db = LocalDb();
  List<CartItem> _items = [];

  List<CartItem> get items => _items;

  double get totalPrice => _items.fold(0.0, (sum, item) => sum + (item.price * item.qty));

  CartViewModel() {
    loadCart();
  }

  Future<void> loadCart() async {
    _items = await _db.getCartItems();
    notifyListeners();
  }

  Future<void> addToCart(CartItem item) async {
    final idx = _items.indexWhere((i) => i.name == item.name);
    if (idx >= 0) {
      final updated = CartItem(name: item.name, price: item.price, qty: _items[idx].qty + item.qty, isCustom: item.isCustom, comment: item.comment);
      await _db.updateItem(updated);
    } else {
      await _db.insertItem(item);
    }
    await loadCart();
  }

  Future<void> updateQty(String name, int qty) async {
    if (qty <= 0) {
      await removeFromCart(name);
      return;
    }
    final idx = _items.indexWhere((i) => i.name == name);
    if (idx >= 0) {
      final updated = CartItem(name: name, price: _items[idx].price, qty: qty, isCustom: _items[idx].isCustom, comment: _items[idx].comment);
      await _db.updateItem(updated);
      await loadCart();
    }
  }

  Future<void> removeFromCart(String name) async {
    await _db.deleteItem(name);
    await loadCart();
  }

  Future<void> clearCart() async {
    await _db.clearCart();
    await loadCart();
  }
}
