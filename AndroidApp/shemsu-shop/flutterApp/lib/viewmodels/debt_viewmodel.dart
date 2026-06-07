import 'package:flutter/foundation.dart';
import '../models/models.dart';
import '../data/api_service.dart';

class DebtViewModel with ChangeNotifier {
  final ApiService _api;

  DebtViewModel(this._api);

  List<Debt> _debts = [];
  List<Debt> get debts => _debts;

  double _activeTotal = 0.0;
  double get activeTotal => _activeTotal;

  bool _allowDebt = false;
  bool get allowDebt => _allowDebt;

  List<PaymentAccount> _paymentAccounts = [];
  List<PaymentAccount> get paymentAccounts => _paymentAccounts;

  bool _isLoading = false;
  bool get isLoading => _isLoading;

  String? _error;
  String? get error => _error;

  Future<void> loadDebts(String username) async {
    _isLoading = true;
    notifyListeners();
    try {
      _debts = await _api.getDebts(username);
      _activeTotal = (await _api.getDebtActiveTotal(username)).activeTotal;
    } catch (_) {}
    _isLoading = false;
    notifyListeners();
  }

  Future<void> loadPaymentAccounts() async {
    try {
      _paymentAccounts = await _api.getPaymentAccounts();
      notifyListeners();
    } catch (_) {}
  }

  Future<void> checkDebtAllowed(String username) async {
    try {
      final res = await _api.checkDebtAllowed(username);
      _allowDebt = res.success;
      notifyListeners();
    } catch (_) {}
  }

  Future<bool> payDebt({
    required String username,
    required int userId,
    required double amount,
    required int paymentAccountId,
    required String confirmation,
  }) async {
    _isLoading = true;
    notifyListeners();
    try {
      final res = await _api.payDebt(
        username: username,
        userId: userId,
        amount: amount,
        paymentAccountId: paymentAccountId,
        confirmation: confirmation,
      );
      _isLoading = false;
      if (res.success) {
        await loadDebts(username);
        return true;
      }
      _error = res.error;
      notifyListeners();
      return false;
    } catch (e) {
      _error = e.toString();
      _isLoading = false;
      notifyListeners();
      return false;
    }
  }
}
