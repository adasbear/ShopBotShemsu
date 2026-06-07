import 'package:dio/dio.dart';
import '../models/models.dart';
import '../core/constants.dart';

class ApiService {
  final Dio _dio;

  ApiService({Dio? dio}) : _dio = dio ?? Dio(BaseOptions(
    baseUrl: AppConstants.baseUrl,
    connectTimeout: const Duration(seconds: 60),
    receiveTimeout: const Duration(seconds: 60),
    headers: {'Content-Type': 'application/json'},
  ));

  Future<OtpResponse> requestOtp(String username) async {
    final res = await _dio.post('api/auth/request-otp', data: {'username': username});
    return OtpResponse.fromJson(res.data);
  }

  Future<VerifyResponse> verifyOtp(String username, String otp) async {
    final res = await _dio.post('api/auth/verify-otp', data: {'username': username, 'otp': otp});
    return VerifyResponse.fromJson(res.data);
  }

  Future<SessionCheckResponse> checkSession(String token) async {
    final res = await _dio.get('api/auth/session', queryParameters: {'token': token});
    return SessionCheckResponse.fromJson(res.data);
  }

  Future<User> getProfile(int userId) async {
    final res = await _dio.get('api/user/profile', queryParameters: {'user_id': userId});
    return User.fromJson(res.data);
  }

  Future<GenericResponse> updateProfile(int userId, String fullName) async {
    final res = await _dio.put('api/user/profile', data: {'user_id': userId, 'full_name': fullName});
    return GenericResponse.fromJson(res.data);
  }

  Future<List<MenuItem>> getMenu() async {
    final res = await _dio.get('api/menu');
    return (res.data as List).map((i) => MenuItem.fromJson(i)).toList();
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
    final res = await _dio.post('api/orders', data: {
      'user_id': userId,
      'username': username,
      'full_name': fullName,
      'items': items.map((e) => e.toJson()).toList(),
      'payment_method': paymentMethod,
      'payment_account_id': paymentAccountId,
      'confirmation': confirmation,
      'comment': comment,
    });
    return PlaceOrderResponse.fromJson(res.data);
  }

  Future<List<OrderGroup>> getOrders(int userId) async {
    final res = await _dio.get('api/orders', queryParameters: {'user_id': userId});
    final data = res.data;
    if (data is List) {
      return data.map((i) => OrderGroup.fromJson(i)).toList();
    }
    return [];
  }

  Future<GenericResponse> cancelOrder(String orderGroup) async {
    final res = await _dio.delete('api/orders/$orderGroup');
    return GenericResponse.fromJson(res.data);
  }

  Future<List<Debt>> getDebts(String username) async {
    final res = await _dio.get('api/debts', queryParameters: {'username': username});
    return (res.data as List).map((i) => Debt.fromJson(i)).toList();
  }

  Future<DebtTotalResponse> getDebtActiveTotal(String username) async {
    final res = await _dio.get('api/debts/active-total', queryParameters: {'username': username});
    return DebtTotalResponse.fromJson(res.data);
  }

  Future<GenericResponse> payDebt({
    required String username,
    required int userId,
    required double amount,
    required int paymentAccountId,
    required String confirmation,
  }) async {
    final res = await _dio.post('api/debts/pay', data: {
      'username': username,
      'user_id': userId,
      'amount': amount,
      'payment_account_id': paymentAccountId,
      'confirmation': confirmation,
    });
    return GenericResponse.fromJson(res.data);
  }

  Future<List<PaymentAccount>> getPaymentAccounts() async {
    final res = await _dio.get('api/payment-accounts');
    return (res.data as List).map((i) => PaymentAccount.fromJson(i)).toList();
  }

  Future<GenericResponse> checkDebtAllowed(String username) async {
    final res = await _dio.get('api/debt-allow-list/check', queryParameters: {'username': username});
    return GenericResponse.fromJson(res.data);
  }

  Future<GenericResponse> submitFeedback(int userId, int rating, String comment) async {
    final res = await _dio.post('api/feedback', data: {
      'user_id': userId,
      'rating': rating,
      'comment': comment,
    });
    return GenericResponse.fromJson(res.data);
  }

  Future<List<AppNotification>> getNotifications(int userId) async {
    final res = await _dio.get('api/notifications', queryParameters: {'user_id': userId});
    return (res.data as List).map((i) => AppNotification.fromJson(i)).toList();
  }

  Future<GenericResponse> markNotificationRead(int id) async {
    final res = await _dio.put('api/notifications/$id/read');
    return GenericResponse.fromJson(res.data);
  }

  Future<GenericResponse> contactAdmin(int userId, String username, String message) async {
    final res = await _dio.post('api/contact', data: {
      'user_id': userId,
      'username': username,
      'message': message,
    });
    return GenericResponse.fromJson(res.data);
  }
}
