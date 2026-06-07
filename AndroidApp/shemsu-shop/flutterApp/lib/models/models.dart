class User {
  final int userId;
  final String fullName;
  final String? username;
  final String? phone;
  final bool banned;
  final String? createdAt;

  User({
    required this.userId,
    required this.fullName,
    this.username,
    this.phone,
    required this.banned,
    this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) => User(
    userId: json['user_id'],
    fullName: json['full_name'],
    username: json['username'],
    phone: json['phone'],
    banned: json['banned'] == 1 || json['banned'] == true,
    createdAt: json['created_at'],
  );

  Map<String, dynamic> toJson() => {
    'user_id': userId,
    'full_name': fullName,
    'username': username,
    'phone': phone,
    'banned': banned,
    'created_at': createdAt,
  };
}

class MenuItem {
  final int id;
  final String name;
  final double price;
  final String? parent;
  final bool available;

  MenuItem({required this.id, required this.name, required this.price, this.parent, this.available = true});

  factory MenuItem.fromJson(Map<String, dynamic> json) => MenuItem(
    id: json['id'],
    name: json['name'],
    price: (json['price'] as num).toDouble(),
    parent: json['parent'],
    available: json['available'] ?? true,
  );

  bool get isCategory => price == 0.0;
}

class CartItem {
  final String name;
  final double price;
  int qty;
  final bool isCustom;
  final String comment;

  CartItem({required this.name, required this.price, this.qty = 1, this.isCustom = false, this.comment = ''});

  factory CartItem.fromJson(Map<String, dynamic> json) => CartItem(
    name: json['name'],
    price: (json['price'] as num).toDouble(),
    qty: json['qty'] ?? 1,
    isCustom: json['isCustom'] == 1 || json['isCustom'] == true,
    comment: json['comment'] ?? '',
  );

  Map<String, dynamic> toJson() => {
    'name': name,
    'price': price,
    'qty': qty,
    'isCustom': isCustom ? 1 : 0,
    'comment': comment,
  };
}

class OrderItem {
  final int id;
  final String item;
  final int qty;
  final String? status;

  OrderItem({required this.id, required this.item, required this.qty, this.status});

  factory OrderItem.fromJson(Map<String, dynamic> json) => OrderItem(
    id: json['id'],
    item: json['item'],
    qty: json['qty'],
    status: json['status'],
  );
}

class OrderGroup {
  final String orderGroup;
  final String? timestamp;
  final String status;
  final List<OrderItem> items;
  final String? payment;
  final String? comment;
  final String? declineReason;
  final double total;

  OrderGroup({
    required this.orderGroup,
    this.timestamp,
    required this.status,
    required this.items,
    this.payment,
    this.comment,
    this.declineReason,
    this.total = 0.0,
  });

  factory OrderGroup.fromJson(Map<String, dynamic> json) {
    final itemsRaw = json['items'];
    List<OrderItem> items = [];
    if (itemsRaw is List) {
      items = itemsRaw.map((i) => OrderItem.fromJson(i)).toList();
    }
    return OrderGroup(
      orderGroup: json['order_group'],
      timestamp: json['timestamp'],
      status: json['status'],
      items: items,
      payment: json['payment'],
      comment: json['comment'],
      declineReason: json['decline_reason'],
      total: (json['total'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

class Debt {
  final int id;
  final String username;
  final double amount;
  final String? description;
  final String status;
  final String? createdAt;
  final String? paidAt;

  Debt({required this.id, required this.username, required this.amount, this.description, required this.status, this.createdAt, this.paidAt});

  factory Debt.fromJson(Map<String, dynamic> json) => Debt(
    id: json['id'],
    username: json['username'],
    amount: (json['amount'] as num).toDouble(),
    description: json['description'],
    status: json['status'],
    createdAt: json['created_at'],
    paidAt: json['paid_at'],
  );
}

class PaymentAccount {
  final int id;
  final String bankName;
  final String number;
  final String holderName;

  PaymentAccount({required this.id, required this.bankName, required this.number, required this.holderName});

  factory PaymentAccount.fromJson(Map<String, dynamic> json) => PaymentAccount(
    id: json['id'],
    bankName: json['bank_name'],
    number: json['number'],
    holderName: json['holder_name'],
  );
}

class AppNotification {
  final int id;
  final String title;
  final String body;
  final String? orderGroup;
  final bool read;
  final String? createdAt;

  AppNotification({required this.id, required this.title, required this.body, this.orderGroup, required this.read, this.createdAt});

  factory AppNotification.fromJson(Map<String, dynamic> json) => AppNotification(
    id: json['id'],
    title: json['title'],
    body: json['body'],
    orderGroup: json['order_group'],
    read: json['read'] == 1 || json['read'] == true,
    createdAt: json['created_at'],
  );
}

class ContactMessage {
  final String id;
  final String text;
  final bool isUser;
  final String timestamp;

  ContactMessage({required this.id, required this.text, required this.isUser, String? timestamp})
    : timestamp = timestamp ?? _now();

  static String _now() {
    final now = DateTime.now();
    final h = now.hour > 12 ? now.hour - 12 : now.hour;
    final m = now.minute.toString().padLeft(2, '0');
    final ampm = now.hour >= 12 ? 'PM' : 'AM';
    return '$h:$m $ampm';
  }
}

class OtpResponse {
  final bool success;
  final String? message;
  final String? error;

  OtpResponse({required this.success, this.message, this.error});

  factory OtpResponse.fromJson(Map<String, dynamic> json) => OtpResponse(
    success: json['success'] ?? false,
    message: json['message'],
    error: json['error'],
  );
}

class VerifyResponse {
  final bool success;
  final String? sessionToken;
  final String? error;

  VerifyResponse({required this.success, this.sessionToken, this.error});

  factory VerifyResponse.fromJson(Map<String, dynamic> json) => VerifyResponse(
    success: json['success'] ?? false,
    sessionToken: json['session_token'],
    error: json['error'],
  );
}

class PlaceOrderResponse {
  final bool success;
  final String? orderGroup;
  final double? total;
  final String? paymentMethod;
  final String? status;
  final String? error;

  PlaceOrderResponse({required this.success, this.orderGroup, this.total, this.paymentMethod, this.status, this.error});

  factory PlaceOrderResponse.fromJson(Map<String, dynamic> json) => PlaceOrderResponse(
    success: json['success'] ?? false,
    orderGroup: json['order_group'],
    total: (json['total'] as num?)?.toDouble(),
    paymentMethod: json['payment_method'],
    status: json['status'],
    error: json['error'],
  );
}

class GenericResponse {
  final bool success;
  final String? message;
  final String? error;

  GenericResponse({required this.success, this.message, this.error});

  factory GenericResponse.fromJson(Map<String, dynamic> json) => GenericResponse(
    success: json['success'] ?? false,
    message: json['message'],
    error: json['error'],
  );
}

class SessionCheckResponse {
  final int userId;
  final String username;
  final String fullName;

  SessionCheckResponse({required this.userId, required this.username, required this.fullName});

  factory SessionCheckResponse.fromJson(Map<String, dynamic> json) => SessionCheckResponse(
    userId: json['user_id'],
    username: json['username'],
    fullName: json['full_name'],
  );
}

class DebtTotalResponse {
  final double activeTotal;

  DebtTotalResponse({required this.activeTotal});

  factory DebtTotalResponse.fromJson(Map<String, dynamic> json) => DebtTotalResponse(
    activeTotal: (json['active_total'] as num?)?.toDouble() ?? 0.0,
  );
}
