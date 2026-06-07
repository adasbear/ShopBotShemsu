import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../data/api_service.dart';

class MenuViewModel with ChangeNotifier {
  final ApiService _api;

  MenuViewModel(this._api);

  List<MenuItem> _items = [];
  List<MenuItem> get items => _items;

  List<MenuItem> get categories => _items.where((i) => i.isCategory).toList();

  String? _selectedCategory;
  String? get selectedCategory => _selectedCategory;

  List<MenuItem> get subItems {
    if (_selectedCategory == null) return [];
    return _items.where((i) => i.parent == _selectedCategory).toList();
  }

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  List<MenuItem> _searchResults = [];
  List<MenuItem> get searchResults => _searchResults;

  Future<void> loadMenu() async {
    _isLoading = true;
    notifyListeners();
    try {
      _items = await _api.getMenu();
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }

  void selectCategory(String? name) {
    _selectedCategory = name;
    notifyListeners();
  }

  void search(String query) {
    if (query.isEmpty) {
      _searchResults = [];
    } else {
      _searchResults = _items.where((i) =>
        !i.isCategory &&
        i.name.toLowerCase().contains(query.toLowerCase())
      ).toList();
    }
    notifyListeners();
  }
}
