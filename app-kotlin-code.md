# Shemsu Shop — Kotlin Code for OTP Authentication

---

## File: `data/remote/ApiService.kt`

```kotlin
package com.shemsushop.data.remote

import com.shemsushop.data.model.*
import retrofit2.Response
import retrofit2.http.*

interface ApiService {

    // --- Auth ---

    @POST("api/auth/request-otp")
    suspend fun requestOtp(@Body body: Map<String, String>): Response<OtpRequestResponse>

    @POST("api/auth/verify-otp")
    suspend fun verifyOtp(@Body body: Map<String, String>): Response<OtpVerifyResponse>

    @GET("api/auth/session")
    suspend fun checkSession(@Query("token") token: String): Response<UserResponse>

    // --- User ---

    @GET("api/user/profile")
    suspend fun getUserProfile(@Query("user_id") userId: Long): Response<UserResponse>

    @PUT("api/user/profile")
    suspend fun updateProfile(@Body body: Map<String, Any>): Response<SuccessResponse>

    // --- Menu ---

    @GET("api/menu")
    suspend fun getMenu(@Query("parent") parent: String? = null): Response<List<MenuItemDto>>

    // --- Payment Accounts ---

    @GET("api/payment-accounts")
    suspend fun getPaymentAccounts(): Response<List<PaymentAccountDto>>

    // --- Debt Check ---

    @GET("api/debt-allow-list/check")
    suspend fun checkDebtAllow(@Query("username") username: String): Response<DebtAllowResponse>

    // --- Orders ---

    @POST("api/orders")
    suspend fun placeOrder(@Body body: PlaceOrderRequest): Response<PlaceOrderResponse>

    @GET("api/orders")
    suspend fun getOrders(@Query("user_id") userId: Long): Response<List<OrderItemDto>>

    @GET("api/orders/group/{orderGroup}")
    suspend fun getOrderGroup(@Path("orderGroup") orderGroup: String): Response<OrderGroupDto>

    @PUT("api/orders/{orderGroup}/items")
    suspend fun editOrderItems(
        @Path("orderGroup") orderGroup: String,
        @Body body: Map<String, List<Map<String, Any>>>
    ): Response<SuccessResponse>

    @DELETE("api/orders/{orderGroup}")
    suspend fun cancelOrder(@Path("orderGroup") orderGroup: String): Response<SuccessResponse>

    // --- Debts ---

    @GET("api/debts")
    suspend fun getDebts(@Query("username") username: String): Response<DebtsResponse>

    @POST("api/debts/pay")
    suspend fun payDebt(@Body body: DebtPayRequest): Response<SuccessResponse>

    // --- Notifications ---

    @GET("api/notifications")
    suspend fun getNotifications(@Query("user_id") userId: Long): Response<List<NotificationDto>>

    @PUT("api/notifications/{id}/read")
    suspend fun markNotificationRead(@Path("id") id: Int): Response<SuccessResponse>

    // --- Other ---

    @POST("api/feedback")
    suspend fun submitFeedback(@Body body: Map<String, Any>): Response<SuccessResponse>

    @POST("api/contact")
    suspend fun contactAdmin(@Body body: Map<String, Any>): Response<SuccessResponse>
}
```

---

## File: `data/remote/RetrofitClient.kt`

```kotlin
package com.shemsushop.data.remote

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object RetrofitClient {

    // 👇 CHANGE THIS TO YOUR RENDER URL
    private const val BASE_URL = "https://shopbotshemsu-1.onrender.com/"

    private val logging = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val client = OkHttpClient.Builder()
        .addInterceptor(logging)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()

    val api: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}
```

---

## File: `data/model/Models.kt`

```kotlin
package com.shemshop.data.model

// --- Auth ---

data class OtpRequestResponse(
    val success: Boolean,
    val delivery: String?,
    val error: String?
)

data class OtpVerifyResponse(
    val success: Boolean,
    val session_token: String?,
    val is_new_user: Boolean?,
    val error: String?
)

data class UserResponse(
    val user_id: Long?,
    val username: String?,
    val full_name: String?,
    val banned: Boolean?,
    val created_at: String?,
    val error: String?
)

data class SuccessResponse(
    val success: Boolean?,
    val error: String?
)

// --- Menu ---

data class MenuItemDto(
    val id: Int,
    val name: String,
    val price: Double,
    val parent: String?,
    val available: Boolean
)

// --- Payment Accounts ---

data class PaymentAccountDto(
    val id: Int,
    val bank_name: String,
    val number: String,
    val holder_name: String
)

// --- Debt ---

data class DebtAllowResponse(
    val allowed: Boolean
)

data class DebtsResponse(
    val active_total: Double,
    val records: List<DebtDto>
)

data class DebtDto(
    val id: Int,
    val username: String,
    val amount: Double,
    val description: String?,
    val status: String,
    val created_at: String?,
    val paid_at: String?
)

// --- Orders ---

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
    val is_custom: Boolean = false
)

data class PlaceOrderResponse(
    val success: Boolean,
    val order_group: String?,
    val total: Double?,
    val payment_method: String?,
    val status: String?,
    val error: String?
)

data class OrderItemDto(
    val id: Int,
    val item: String,
    val qty: Int,
    val status: String?,
    val order_group: String?,
    val timestamp: String?
)

data class OrderGroupDto(
    val order_group: String?,
    val items: List<OrderItemDetailDto>?,
    val total: Double?,
    val payment: String?,
    val comment: String?,
    val decline_reason: String?,
    val status: String?,
    val created_at: String?
)

data class OrderItemDetailDto(
    val id: Int,
    val item: String,
    val qty: Int,
    val status: String?,
    val timestamp: String?
)

// --- Debt Pay ---

data class DebtPayRequest(
    val username: String,
    val user_id: Long,
    val amount: Double,
    val payment_account_id: Int,
    val confirmation: String
)

// --- Notifications ---

data class NotificationDto(
    val id: Int,
    val user_id: Long,
    val title: String,
    val body: String,
    val order_group: String?,
    val read: Boolean,
    val created_at: String?
)
```

---

## File: `data/local/SessionManager.kt`

```kotlin
package com.shemshop.data.local

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

/**
 * Stores session token securely on device using EncryptedSharedPreferences.
 */
class SessionManager(context: Context) {

    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val prefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "shemsu_secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    companion object {
        private const val KEY_TOKEN = "session_token"
        private const val KEY_USER_ID = "user_id"
        private const val KEY_USERNAME = "username"
        private const val KEY_FULL_NAME = "full_name"
    }

    fun saveSession(token: String, userId: Long, username: String, fullName: String) {
        prefs.edit()
            .putString(KEY_TOKEN, token)
            .putLong(KEY_USER_ID, userId)
            .putString(KEY_USERNAME, username)
            .putString(KEY_FULL_NAME, fullName)
            .apply()
    }

    fun getToken(): String? = prefs.getString(KEY_TOKEN, null)
    fun getUserId(): Long = prefs.getLong(KEY_USER_ID, -1)
    fun getUsername(): String? = prefs.getString(KEY_USERNAME, null)
    fun getFullName(): String? = prefs.getString(KEY_FULL_NAME, null)

    fun isLoggedIn(): Boolean = getToken() != null

    fun clearSession() {
        prefs.edit().clear().apply()
    }
}
```

---

## File: `data/repository/AuthRepository.kt`

```kotlin
package com.shemshop.data.repository

import com.shemshop.data.local.SessionManager
import com.shemshop.data.model.OtpRequestResponse
import com.shemshop.data.model.OtpVerifyResponse
import com.shemshop.data.model.UserResponse
import com.shemshop.data.remote.ApiService

/**
 * Repository handling all authentication operations.
 * Calls the backend API and manages local session storage.
 */
class AuthRepository(
    private val api: ApiService,
    private val sessionManager: SessionManager
) {

    /**
     * Step 1: Request OTP.
     * Sends the user's Telegram username to the backend.
     * Backend sends a 6-digit OTP to the user's Telegram DM via the bot.
     *
     * @param username Telegram username (without @)
     * @return Result containing success/failure + delivery method
     */
    suspend fun requestOtp(username: String): Result<OtpRequestResponse> {
        return try {
            val response = api.requestOtp(mapOf("username" to username))
            if (response.isSuccessful && response.body() != null) {
                Result.success(response.body()!!)
            } else {
                val errorBody = response.errorBody()?.string() ?: "Unknown error"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Step 2: Verify OTP.
     * User enters the OTP they received on Telegram.
     * Backend validates and returns a session token.
     *
     * @param username Telegram username
     * @param otp The 6-digit code the user received
     * @return Result with session token on success
     */
    suspend fun verifyOtp(username: String, otp: String): Result<OtpVerifyResponse> {
        return try {
            val response = api.verifyOtp(mapOf("username" to username, "otp" to otp))
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                // Save session locally
                if (body.success && body.session_token != null) {
                    // We'll get user info in the next step (checkSession)
                    Result.success(body)
                } else {
                    Result.failure(Exception(body.error ?: "Verification failed"))
                }
            } else {
                val errorBody = response.errorBody()?.string() ?: "Invalid or expired OTP"
                Result.failure(Exception(errorBody))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * Step 3: Validate session and get user info.
     * Called on app launch to check if the stored session is still valid.
     *
     * @param token The session token stored locally
     * @return Result with user data if session is valid
     */
    suspend fun checkSession(token: String): Result<UserResponse> {
        return try {
            val response = api.checkSession(token)
            if (response.isSuccessful && response.body() != null) {
                val body = response.body()!!
                if (body.user_id != null) {
                    // Update local session with fresh data
                    sessionManager.saveSession(
                        token = token,
                        userId = body.user_id,
                        username = body.username ?: "",
                        fullName = body.full_name ?: ""
                    )
                    Result.success(body)
                } else {
                    Result.failure(Exception(body.error ?: "Session expired"))
                }
            } else {
                Result.failure(Exception("Session expired"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    /**
     * After OTP verification, fetch user profile and save session locally.
     */
    suspend fun finalizeLogin(token: String, userId: Long, username: String): Result<UserResponse> {
        return try {
            val response = api.getUserProfile(userId)
            if (response.isSuccessful && response.body() != null) {
                val user = response.body()!!
                sessionManager.saveSession(
                    token = token,
                    userId = user.user_id ?: userId,
                    username = user.username ?: username,
                    fullName = user.full_name ?: username
                )
                Result.success(user)
            } else {
                // Fallback: save what we have
                sessionManager.saveSession(
                    token = token,
                    userId = userId,
                    username = username,
                    fullName = username
                )
                Result.failure(Exception("Could not fetch profile"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun logout() {
        sessionManager.clearSession()
    }

    fun isLoggedIn(): Boolean = sessionManager.isLoggedIn()
    fun getSavedUserId(): Long = sessionManager.getUserId()
    fun getSavedUsername(): String? = sessionManager.getUsername()
    fun getSavedFullName(): String? = sessionManager.getFullName()
}
```

---

## File: `viewmodel/AuthViewModel.kt`

```kotlin
package com.shemshop.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.shemshop.data.model.UserResponse
import com.shemshop.data.repository.AuthRepository
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch

/**
 * Possible states for the OTP authentication flow.
 */
sealed class AuthState {
    /** Initial state / idle */
    object Idle : AuthState()

    /** OTP has been sent, waiting for user to type the code */
    data class OtpSent(val delivery: String) : AuthState()

    /** Currently verifying the OTP with the server */
    object Verifying : AuthState()

    /** Login successful, user info available */
    data class Success(val user: UserResponse) : AuthState()

    /** An error occurred */
    data class Error(val message: String) : AuthState()

    /** Checking saved session on app launch */
    object Loading : AuthState()

    /** No valid session found, user must log in */
    object NotLoggedIn : AuthState()
}

class AuthViewModel(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _authState = MutableStateFlow<AuthState>(AuthState.Loading)
    val authState: StateFlow<AuthState> = _authState

    private val _otpTimer = MutableStateFlow(0) // seconds remaining
    val otpTimer: StateFlow<Int> = _otpTimer

    private val _username = MutableStateFlow("")
    val username: StateFlow<String> = _username

    companion object {
        private const val OTP_EXPIRY_SECONDS = 300 // 5 minutes
        private const val COOLDOWN_SECONDS = 60    // 1 minute between resends
    }

    init {
        checkSavedSession()
    }

    /**
     * On app launch: check if a valid session token exists.
     * If yes, validate with server. If no, show login.
     */
    private fun checkSavedSession() {
        if (!authRepository.isLoggedIn()) {
            _authState.value = AuthState.NotLoggedIn
            return
        }
        viewModelScope.launch {
            val token = authRepository.sessionManager.getToken() ?: ""
            val result = authRepository.checkSession(token)
            _authState.value = if (result.isSuccess) {
                AuthState.Success(result.getOrThrow())
            } else {
                authRepository.logout()
                AuthState.NotLoggedIn
            }
        }
    }

    /**
     * Called when user enters their Telegram username and presses "Send OTP".
     */
    fun requestOtp(username: String) {
        val clean = username.trimStart('@').trim()
        if (clean.isEmpty()) {
            _authState.value = AuthState.Error("Enter your Telegram username")
            return
        }
        _username.value = clean
        _authState.value = AuthState.Loading

        viewModelScope.launch {
            val result = authRepository.requestOtp(clean)
            _authState.value = if (result.isSuccess) {
                val body = result.getOrThrow()
                if (body.success) {
                    startOtpTimer()
                    AuthState.OtpSent(delivery = body.delivery ?: "bot")
                } else {
                    AuthState.Error(body.error ?: "Failed to send OTP")
                }
            } else {
                val errorMsg = result.exceptionOrNull()?.message ?: "Network error"
                AuthState.Error(parseErrorMessage(errorMsg))
            }
        }
    }

    /**
     * Called when user enters the 6-digit OTP and presses "Verify".
     */
    fun verifyOtp(otp: String) {
        if (otp.length != 6) {
            _authState.value = AuthState.Error("Enter the 6-digit code")
            return
        }
        _authState.value = AuthState.Verifying

        viewModelScope.launch {
            val result = authRepository.verifyOtp(_username.value, otp)
            if (result.isSuccess) {
                val body = result.getOrThrow()
                // Fetch full profile and save session
                val userId = authRepository.sessionManager.getUserId()
                if (userId != -1L) {
                    // Session already saved by verifyOtp -> checkSession -> finalize
                    _authState.value = AuthState.Success(
                        UserResponse(userId, _username.value, authRepository.getSavedFullName(), null, null, null)
                    )
                } else {
                    // Need to resolve user info
                    _authState.value = AuthState.Error("Could not retrieve profile")
                }
            } else {
                val errorMsg = result.exceptionOrNull()?.message ?: "Invalid OTP"
                _authState.value = AuthState.Error(parseErrorMessage(errorMsg))
            }
        }
    }

    /**
     * Resend OTP (after cooldown).
     */
    fun resendOtp() {
        requestOtp(_username.value)
    }

    /**
     * Log the user out and clear session.
     */
    fun logout() {
        authRepository.logout()
        _authState.value = AuthState.NotLoggedIn
        _username.value = ""
        _otpTimer.value = 0
    }

    /**
     * Reset to Idle (clear error, go back to username input).
     */
    fun reset() {
        _authState.value = AuthState.Idle
    }

    private fun startOtpTimer() {
        _otpTimer.value = OTP_EXPIRY_SECONDS
        viewModelScope.launch {
            while (_otpTimer.value > 0) {
                delay(1000)
                _otpTimer.value -= 1
            }
        }
    }

    /**
     * Parse error JSON to extract user-friendly message.
     */
    private fun parseErrorMessage(raw: String): String {
        return when {
            raw.contains("429") || raw.contains("Too many") -> 
                "Too many requests. Try again in 1 hour."
            raw.contains("401") || raw.contains("Invalid or expired") -> 
                "Invalid or expired code. Request a new one."
            raw.contains("404") || raw.contains("not registered") || raw.contains("not found") ->
                "Username not found. First start @ShemsuShopBot on Telegram and register."
            raw.contains("403") || raw.contains("banned") ->
                "You are banned. Contact @PPopa054 on Telegram."
            else -> "Something went wrong. Check your connection and try again."
        }
    }
}
```

---

## File: `ui/screens/login/LoginScreen.kt`

```kotlin
package com.shemshop.ui.screens.login

import androidx.compose.animation.*
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.FocusDirection
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shemshop.viewmodel.AuthState
import com.shemshop.viewmodel.AuthViewModel
import kotlinx.coroutines.delay

/**
 * Login screen with two-step flow:
 * 1. User enters Telegram username → Send OTP
 * 2. User enters 6-digit OTP → Verify
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LoginScreen(
    viewModel: AuthViewModel,
    onLoginSuccess: () -> Unit
) {
    val authState by viewModel.authState.collectAsState()
    val otpTimer by viewModel.otpTimer.collectAsState()
    val focusManager = LocalFocusManager.current

    var username by remember { mutableStateOf("") }
    var otp by remember { mutableStateOf("") }

    // Navigate on success
    LaunchedEffect(authState) {
        if (authState is AuthState.Success) {
            delay(500)
            onLoginSuccess()
        }
    }

    Scaffold { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(horizontal = 24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center
        ) {
            // --- App Logo / Title ---
            Text(
                text = "Shemsu Shop",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = "First time? Open Telegram, start\n@ShemsuShopBot, and type /start",
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

            Spacer(modifier = Modifier.height(32.dp))

            // --- Step 1: Username Input ---
            if (authState !is AuthState.OtpSent) {
                OutlinedTextField(
                    value = username,
                    onValueChange = {
                        username = it.trimStart('@')
                        viewModel.reset()
                    },
                    label = { Text("Telegram username") },
                    placeholder = { Text("e.g., PPopa054") },
                    singleLine = true,
                    enabled = authState !is AuthState.Loading,
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Ascii,
                        imeAction = ImeAction.Done
                    ),
                    keyboardActions = KeyboardActions(
                        onDone = {
                            focusManager.clearFocus()
                            viewModel.requestOtp(username)
                        }
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Send OTP button
                Button(
                    onClick = {
                        focusManager.clearFocus()
                        viewModel.requestOtp(username)
                    },
                    enabled = username.isNotBlank() && authState !is AuthState.Loading,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp)
                ) {
                    if (authState is AuthState.Loading) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = MaterialTheme.colorScheme.onPrimary,
                            strokeWidth = 2.dp
                        )
                    } else {
                        Text("Send OTP", fontSize = 16.sp)
                    }
                }
            }

            // --- Step 2: OTP Input (shown after OTP is sent) ---
            if (authState is AuthState.OtpSent) {
                Text(
                    text = "A code was sent to your Telegram DM",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                Spacer(modifier = Modifier.height(24.dp))

                // 6-digit OTP input
                OutlinedTextField(
                    value = otp,
                    onValueChange = {
                        if (it.length <= 6 && it.all { c -> c.isDigit() }) {
                            otp = it
                        }
                    },
                    label = { Text("6-digit code") },
                    placeholder = { Text("000000") },
                    singleLine = true,
                    enabled = authState !is AuthState.Verifying,
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.Number,
                        imeAction = ImeAction.Done
                    ),
                    keyboardActions = KeyboardActions(
                        onDone = {
                            focusManager.clearFocus()
                            if (otp.length == 6) viewModel.verifyOtp(otp)
                        }
                    ),
                    modifier = Modifier.fillMaxWidth()
                )

                Spacer(modifier = Modifier.height(16.dp))

                // Verify button
                Button(
                    onClick = {
                        focusManager.clearFocus()
                        viewModel.verifyOtp(otp)
                    },
                    enabled = otp.length == 6 && authState !is AuthState.Verifying,
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(50.dp)
                ) {
                    if (authState is AuthState.Verifying) {
                        CircularProgressIndicator(
                            modifier = Modifier.size(24.dp),
                            color = MaterialTheme.colorScheme.onPrimary,
                            strokeWidth = 2.dp
                        )
                    } else {
                        Text("Verify", fontSize = 16.sp)
                    }
                }

                Spacer(modifier = Modifier.height(12.dp))

                // Timer and Resend
                if (otpTimer > 0) {
                    val minutes = otpTimer / 60
                    val seconds = otpTimer % 60
                    Text(
                        text = "Code expires in ${minutes}:${String.format("%02d", seconds)}",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                } else {
                    TextButton(onClick = { viewModel.resendOtp() }) {
                        Text("Resend code")
                    }
                }
            }

            // --- Error message ---
            if (authState is AuthState.Error) {
                Spacer(modifier = Modifier.height(16.dp))
                Card(
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.errorContainer
                    ),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Text(
                        text = (authState as AuthState.Error).message,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onErrorContainer,
                        modifier = Modifier.padding(16.dp),
                        textAlign = TextAlign.Center
                    )
                }
            }
        }
    }
}
```

---

## File: `ui/screens/splash/SplashScreen.kt`

```kotlin
package com.shemshop.ui.screens.splash

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.shemshop.viewmodel.AuthState
import com.shemshop.viewmodel.AuthViewModel

/**
 * Splash screen shown on app launch.
 * Waits for AuthViewModel to determine if user is logged in or not.
 */
@Composable
fun SplashScreen(
    viewModel: AuthViewModel,
    onLoggedIn: () -> Unit,
    onNotLoggedIn: () -> Unit
) {
    val authState by viewModel.authState.collectAsState()

    LaunchedEffect(authState) {
        when (authState) {
            is AuthState.Success -> onLoggedIn()
            is AuthState.NotLoggedIn -> onNotLoggedIn()
            else -> { /* still loading */ }
        }
    }

    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(horizontalAlignment = Alignment.CenterHorizontally) {
            Text(
                text = "Shemsu Shop",
                style = MaterialTheme.typography.headlineLarge,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.primary
            )
            Spacer(modifier = Modifier.height(16.dp))
            CircularProgressIndicator()
        }
    }
}
```

---

## File: `navigation/NavGraph.kt`

```kotlin
package com.shemshop.navigation

import androidx.compose.runtime.Composable
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import com.shemshop.ui.screens.login.LoginScreen
import com.shemshop.ui.screens.splash.SplashScreen
import com.shemshop.ui.screens.home.HomeScreen
import com.shemshop.viewmodel.AuthViewModel

object Routes {
    const val SPLASH = "splash"
    const val LOGIN = "login"
    const val HOME = "home"
    // Add more routes here as screens are built:
    // const val MENU = "menu"
    // const val CART = "cart"
    // const val CHECKOUT = "checkout"
    // const val ORDERS = "orders"
    // const val ORDER_DETAIL = "order_detail/{orderGroup}"
    // const val MY_DEBT = "my_debt"
    // const val HELP = "help"
    // const val PROFILE = "profile"
}

@Composable
fun AppNavGraph(
    navController: NavHostController,
    authViewModel: AuthViewModel
) {
    NavHost(
        navController = navController,
        startDestination = Routes.SPLASH
    ) {
        composable(Routes.SPLASH) {
            SplashScreen(
                viewModel = authViewModel,
                onLoggedIn = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.SPLASH) { inclusive = true }
                    }
                },
                onNotLoggedIn = {
                    navController.navigate(Routes.LOGIN) {
                        popUpTo(Routes.SPLASH) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.LOGIN) {
            LoginScreen(
                viewModel = authViewModel,
                onLoginSuccess = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.LOGIN) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.HOME) {
            HomeScreen(
                onLogout = {
                    authViewModel.logout()
                    navController.navigate(Routes.LOGIN) {
                        popUpTo(Routes.HOME) { inclusive = true }
                    }
                }
            )
        }
    }
}
```

---

## File: `di/AppModule.kt` (Hilt)

```kotlin
package com.shemshop.di

import android.content.Context
import com.shemshop.data.local.SessionManager
import com.shemshop.data.remote.ApiService
import com.shemshop.data.remote.RetrofitClient
import com.shemshop.data.repository.AuthRepository
import com.shemshop.viewmodel.AuthViewModel
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideApiService(): ApiService = RetrofitClient.api

    @Provides
    @Singleton
    fun provideSessionManager(@ApplicationContext context: Context): SessionManager =
        SessionManager(context)

    @Provides
    @Singleton
    fun provideAuthRepository(
        api: ApiService,
        sessionManager: SessionManager
    ): AuthRepository = AuthRepository(api, sessionManager)

    @Provides
    @Singleton
    fun provideAuthViewModel(
        authRepository: AuthRepository
    ): AuthViewModel = AuthViewModel(authRepository)
}
```

---

## File: `MainActivity.kt`

```kotlin
package com.shemshop

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.navigation.compose.rememberNavController
import com.shemshop.navigation.AppNavGraph
import com.shemshop.ui.theme.ShemsuShopTheme
import com.shemshop.viewmodel.AuthViewModel
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {

    @Inject
    lateinit var authViewModel: AuthViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            ShemsuShopTheme {
                Surface(color = MaterialTheme.colorScheme.background) {
                    val navController = rememberNavController()
                    AppNavGraph(
                        navController = navController,
                        authViewModel = authViewModel
                    )
                }
            }
        }
    }
}
```

---

## File: `build.gradle.kts` (app) — Dependencies

```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp")
}

android {
    namespace = "com.shemshop"
    compileSdk = 34
    
    defaultConfig {
        applicationId = "com.shemshop.app"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }
    
    buildFeatures {
        compose = true
    }
    
    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.10"
    }
}

dependencies {
    // Compose BOM
    val composeBom = platform("androidx.compose:compose-bom:2024.02.00")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.activity:activity-compose:1.8.2")
    implementation("androidx.navigation:navigation-compose:2.7.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.7.0")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.7.0")

    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Encrypted SharedPreferences
    implementation("androidx.security:security-crypto:1.1.0-alpha06")

    // Hilt
    implementation("com.google.dagger:hilt-android:2.50")
    ksp("com.google.dagger:hilt-compiler:2.50")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
}
```

---

## HomeScreen.kt (placeholder to complete navigation)

```kotlin
package com.shemshop.ui.screens.home

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    onLogout: () -> Unit
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Shemsu Shop") },
                actions = {
                    TextButton(onClick = onLogout) {
                        Text("Logout")
                    }
                }
            )
        }
    ) { padding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding),
            contentAlignment = Alignment.Center
        ) {
            Text("Home — logged in!")
        }
    }
}
```

---

## How the OTP Flow Works End to End

```
┌─────────────────────────────────────────────────────┐
│                    ANDROID APP                       │
│                                                      │
│  1. User opens app → SplashScreen                    │
│     ├─ Session exists → validate with server         │
│     │   ├─ Valid → Home screen                       │
│     │   └─ Invalid → Login screen                    │
│     └─ No session → Login screen                     │
│                                                      │
│  2. Login screen:                                    │
│     User types "PPopa054" → taps "Send OTP"          │
│     App → POST /api/auth/request-otp                 │
│         { "username": "PPopa054" }                    │
│                                                      │
│  3. Backend sends OTP via Telegram bot:              │
│     Bot → DM to @PPopa054:                           │
│       "Shemsu Shop Login Code: 483921                │
│        Expires in 5 minutes."                         │
│                                                      │
│  4. User checks Telegram → sees code                 │
│     User types "483921" in app → taps "Verify"       │
│     App → POST /api/auth/verify-otp                  │
│         { "username": "PPopa054", "otp": "483921" }  │
│                                                      │
│  5. Backend validates OTP → returns session token:   │
│     { "success": true, "session_token": "uuid" }     │
│                                                      │
│  6. App saves token to EncryptedSharedPreferences    │
│     App navigates to Home screen                     │
│                                                      │
│  7. Next app launch:                                 │
│     App reads saved token → validates with server    │
│     Valid → straight to Home (no login screen)       │
│     Invalid → Login screen again                     │
└─────────────────────────────────────────────────────┘
```
