package com.example.data.remote

import com.example.data.model.*
import retrofit2.Response
import retrofit2.http.*

data class OtpRequest(val username: String)
data class OtpResponse(val success: Boolean, val message: String?, val error: String?)

data class VerifyRequest(val username: String, val otp: String)
data class VerifyResponse(val success: Boolean, val session_token: String?, val error: String?)

data class ProfileRequest(val user_id: Long, val full_name: String)

data class PlaceOrderRequest(
    val user_id: Long,
    val username: String?,
    val full_name: String?,
    val items: List<CartItemDto>,
    val payment_method: String,
    val payment_account_id: Int?,
    val confirmation: String?,
    val comment: String?
)

data class CartItemDto(
    val item: String,
    val qty: Int,
    val price: Double,
    val comment: String? = null,
    val isCustom: Boolean = false
)

data class PlaceOrderResponse(
    val success: Boolean,
    val order_group: String?,
    val total: Double?,
    val payment_method: String?,
    val status: String?,
    val error: String?
)

data class DebtTotalResponse(val active_total: Double)
data class DebtPayRequest(
    val username: String,
    val user_id: Long,
    val amount: Double,
    val payment_account_id: Int,
    val confirmation: String
)
data class GenericSuccessResponse(val success: Boolean, val message: String? = null, val error: String? = null)
data class DebtAllowResponse(val allowed: Boolean)
data class SessionCheckResponse(val user_id: Long, val username: String, val full_name: String)

interface ApiService {
    @POST("api/auth/request-otp")
    suspend fun requestOtp(@Body request: OtpRequest): Response<OtpResponse>

    @POST("api/auth/verify-otp")
    suspend fun verifyOtp(@Body request: VerifyRequest): Response<VerifyResponse>

    @GET("api/auth/session")
    suspend fun checkSession(@Query("token") token: String): Response<SessionCheckResponse>

    @GET("api/user/profile")
    suspend fun getProfile(@Query("user_id") userId: Long): Response<User>

    @PUT("api/user/profile")
    suspend fun updateProfile(@Body request: ProfileRequest): Response<GenericSuccessResponse>

    @GET("api/menu")
    suspend fun getMenu(): Response<List<MenuItem>>

    @POST("api/orders")
    suspend fun placeOrder(@Body request: PlaceOrderRequest): Response<PlaceOrderResponse>

    @GET("api/orders")
    suspend fun getOrders(@Query("user_id") userId: Long): Response<List<OrderItemRemote>>

    @DELETE("api/orders/{order_group}")
    suspend fun cancelOrder(@Path("order_group") orderGroup: String): Response<GenericSuccessResponse>

    @GET("api/debts")
    suspend fun getDebts(@Query("username") username: String): Response<List<Debt>>

    @GET("api/debts/active-total")
    suspend fun getDebtActiveTotal(@Query("username") username: String): Response<DebtTotalResponse>

    @POST("api/debts/pay")
    suspend fun payDebt(@Body request: DebtPayRequest): Response<GenericSuccessResponse>

    @GET("api/payment-accounts")
    suspend fun getPaymentAccounts(): Response<List<PaymentAccount>>

    @GET("api/debt-allow-list/check")
    suspend fun checkDebtAllowed(@Query("username") username: String): Response<DebtAllowResponse>

    @POST("api/feedback")
    suspend fun submitFeedback(@Body body: HashMap<String, Any>): Response<GenericSuccessResponse>

    @GET("api/notifications")
    suspend fun getNotifications(@Query("user_id") userId: Long): Response<List<Notification>>

    @PUT("api/notifications/{id}/read")
    suspend fun markNotificationRead(@Path("id") id: Int): Response<GenericSuccessResponse>

    @POST("api/contact")
    suspend fun postContactAdmin(@Body body: HashMap<String, Any>): Response<GenericSuccessResponse>
}

data class OrderItemRemote(
    val id: Int,
    val item: String,
    val qty: Int,
    val status: String,
    val order_group: String,
    val timestamp: String
)
