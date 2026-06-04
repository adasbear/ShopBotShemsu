package com.example.data.model

data class User(
    val user_id: Long,
    val full_name: String,
    val username: String?,
    val phone: String?,
    val banned: Boolean,
    val created_at: String?
)

data class MenuItem(
    val id: Int,
    val name: String,
    val price: Double,
    val parent: String?,
    val available: Boolean? = true
)

data class CartItem(
    val name: String,
    val price: Double,
    val qty: Int,
    val isCustom: Boolean = false,
    val comment: String = ""
)

data class OrderItem(
    val id: Int,
    val item: String,
    val qty: Int,
    val status: String?
)

data class OrderGroup(
    val order_group: String,
    val timestamp: String?,
    val status: String,
    val items: List<OrderItem>,
    val payment: String?,
    val comment: String?,
    val decline_reason: String?,
    val total: Double = 0.0
)

data class Debt(
    val id: Int,
    val username: String,
    val amount: Double,
    val description: String?,
    val status: String,
    val created_at: String?,
    val paid_at: String?
)

data class PaymentAccount(
    val id: Int,
    val bank_name: String,
    val number: String,
    val holder_name: String
)

data class Notification(
    val id: Int,
    val title: String,
    val body: String,
    val order_group: String?,
    val read: Boolean,
    val created_at: String?
)

data class ContactMessage(
    val id: String = java.util.UUID.randomUUID().toString(),
    val text: String,
    val isUser: Boolean,
    val timestamp: String = java.text.SimpleDateFormat("hh:mm a", java.util.Locale.getDefault()).format(java.util.Date())
)
