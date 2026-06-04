package com.example.viewmodel

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.data.local.AppDatabase
import com.example.data.model.*
import com.example.data.repository.*
import kotlinx.coroutines.flow.*
import kotlinx.coroutines.launch

class AuthViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = AuthRepository(application)
    val sessionManager = repo.sessionManager

    private val _isLoggedIn = MutableStateFlow(sessionManager.getToken().isNotEmpty())
    val isLoggedIn: StateFlow<Boolean> = _isLoggedIn.asStateFlow()

    private val _username = MutableStateFlow(sessionManager.getUsername())
    val username: StateFlow<String> = _username.asStateFlow()

    private val _fullName = MutableStateFlow(sessionManager.getFullName())
    val fullName: StateFlow<String> = _fullName.asStateFlow()

    private val _otpSent = MutableStateFlow(false)
    val otpSent: StateFlow<Boolean> = _otpSent.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _authError = MutableStateFlow<String?>(null)
    val authError: StateFlow<String?> = _authError.asStateFlow()

    fun requestOtp(usernameInput: String) {
        if (usernameInput.isBlank()) {
            _authError.value = "Username cannot be empty"
            return
        }
        viewModelScope.launch {
            _isLoading.value = true
            _authError.value = null
            val (success, errorMsg) = repo.requestOtp(usernameInput)
            _isLoading.value = false
            if (success) {
                _otpSent.value = true
                _username.value = usernameInput
            } else {
                _authError.value = errorMsg ?: "Failed to request OTP"
            }
        }
    }

    fun verifyOtp(otpCode: String) {
        if (otpCode.length < 6) {
            _authError.value = "OTP must be 6 digits"
            return
        }
        viewModelScope.launch {
            _isLoading.value = true
            _authError.value = null
            val (success, errorMsg) = repo.verifyOtp(_username.value, otpCode)
            _isLoading.value = false
            if (success) {
                _isLoggedIn.value = true
                _fullName.value = sessionManager.getFullName()
            } else {
                _authError.value = errorMsg ?: "Invalid or expired OTP"
            }
        }
    }

    fun validateSessionSilently(onResult: (Boolean) -> Unit) {
        val token = sessionManager.getToken()
        if (token.isEmpty()) {
            _isLoggedIn.value = false
            onResult(false)
            return
        }
        viewModelScope.launch {
            _isLoading.value = true
            val isValid = repo.checkSession(token)
            _isLoading.value = false
            if (isValid) {
                _isLoggedIn.value = true
                _fullName.value = sessionManager.getFullName()
                onResult(true)
            } else {
                logout()
                onResult(false)
            }
        }
    }

    fun logout() {
        sessionManager.clearSession()
        _isLoggedIn.value = false
        _otpSent.value = false
        _username.value = ""
        _fullName.value = ""
    }

    fun updateName(newName: String) {
        if (newName.isNotBlank()) {
            _fullName.value = newName
            sessionManager.saveSession(
                userId = sessionManager.getUserId(),
                username = sessionManager.getUsername(),
                fullName = newName,
                token = sessionManager.getToken()
            )
            viewModelScope.launch {
                repo.updateProfile(newName)
            }
        }
    }
}

class MenuViewModel : androidx.lifecycle.ViewModel() {
    private val repo = MenuRepository()

    private val _menuItems = MutableStateFlow<List<MenuItem>>(emptyList())
    val menuItems: StateFlow<List<MenuItem>> = _menuItems.asStateFlow()

    private val _categories = MutableStateFlow<List<String>>(emptyList())
    val categories: StateFlow<List<String>> = _categories.asStateFlow()

    private val _selectedCategory = MutableStateFlow("All")
    val selectedCategory: StateFlow<String> = _selectedCategory.asStateFlow()

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    val filteredItems: StateFlow<List<MenuItem>> = combine(
        _menuItems, _selectedCategory, _searchQuery
    ) { items, category, query ->
        items.filter { item ->
            val matchesCategory = if (category == "All") {
                true
            } else {
                item.parent == category
            }
            val matchesSearch = item.name.contains(query, ignoreCase = true)
            matchesCategory && matchesSearch && item.price > 0.0 // Items with price
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    init {
        loadMenu()
    }

    fun loadMenu() {
        viewModelScope.launch {
            _isLoading.value = true
            val items = repo.getMenu()
            _menuItems.value = items
            val cats = items.filter { it.price == 0.0 }.map { it.name }
            _categories.value = listOf("All") + cats
            _isLoading.value = false
        }
    }

    fun selectCategory(cat: String) {
        _selectedCategory.value = cat
    }

    fun setSearchQuery(query: String) {
        _searchQuery.value = query
    }
}

class CartViewModel(application: Application) : AndroidViewModel(application) {
    private val db = AppDatabase.getDatabase(application)
    private val repo = CartRepository(db.cartDao())

    val cartItems: StateFlow<List<CartItem>> = repo.cartItems.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )

    val subtotal: StateFlow<Double> = cartItems.map { list ->
        list.sumOf { it.price * it.qty }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 0.0)

    val itemCount: StateFlow<Int> = cartItems.map { list ->
        list.sumOf { it.qty }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 0)

    fun addToCart(name: String, price: Double, qty: Int, isCustom: Boolean, comment: String = "") {
        viewModelScope.launch {
            repo.addToCart(CartItem(name, price, qty, isCustom, comment))
        }
    }

    fun updateQty(name: String, qty: Int) {
        viewModelScope.launch {
            repo.updateQty(name, qty)
        }
    }

    fun removeFromCart(name: String) {
        viewModelScope.launch {
            repo.removeFromCart(name)
        }
    }

    fun clearCart() {
        viewModelScope.launch {
            repo.clearCart()
        }
    }
}

class OrdersViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = OrderRepository(application)
    private val profileRepo = AuthRepository(application)

    private val _orders = MutableStateFlow<List<OrderGroup>>(emptyList())
    val orders: StateFlow<List<OrderGroup>> = _orders.asStateFlow()

    private val _activeTab = MutableStateFlow("Active")
    val activeTab: StateFlow<String> = _activeTab.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    val displayOrders: StateFlow<List<OrderGroup>> = combine(
        _orders, _activeTab
    ) { orderList, tab ->
        if (tab == "Active") {
            orderList.filter { it.status == "Pending" || it.status == "Accepted" || it.status == "Ready" }
        } else {
            orderList.filter { it.status == "Delivered" || it.status == "Cancelled" }
        }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), emptyList())

    init {
        loadOrders()
    }

    fun loadOrders() {
        viewModelScope.launch {
            _isLoading.value = true
            _orders.value = repo.getOrders()
            _isLoading.value = false
        }
    }

    fun placeOrder(
        items: List<CartItem>,
        paymentMethod: String,
        paymentAccountId: Int?,
        confirmation: String?,
        comment: String?,
        onSuccess: (orderGroup: String) -> Unit
    ) {
        viewModelScope.launch {
            _isLoading.value = true
            val result = repo.placeOrder(items, paymentMethod, paymentAccountId, confirmation, comment)
            _isLoading.value = false
            if (result.first) {
                loadOrders()
                onSuccess(result.second)
            }
        }
    }

    fun cancelOrder(orderGroup: String) {
        viewModelScope.launch {
            _isLoading.value = true
            val success = repo.cancelOrder(orderGroup)
            _isLoading.value = false
            if (success) {
                // Update local status immediately
                _orders.value = _orders.value.map {
                    if (it.order_group == orderGroup) it.copy(status = "Cancelled") else it
                }
            }
        }
    }
}

class DebtViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = DebtRepository(application)
    private val accountsRepo = PaymentAccountRepository()

    private val _debts = MutableStateFlow<List<Debt>>(emptyList())
    val debts: StateFlow<List<Debt>> = _debts.asStateFlow()

    private val _activeTotal = MutableStateFlow(450.0)
    val activeTotal: StateFlow<Double> = _activeTotal.asStateFlow()

    private val _allowDebt = MutableStateFlow(true)
    val allowDebt: StateFlow<Boolean> = _allowDebt.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    private val _paymentAccounts = MutableStateFlow<List<PaymentAccount>>(emptyList())
    val paymentAccounts: StateFlow<List<PaymentAccount>> = _paymentAccounts.asStateFlow()

    init {
        loadDebts()
    }

    fun loadDebts() {
        viewModelScope.launch {
            _isLoading.value = true
            _debts.value = repo.getDebts()
            _activeTotal.value = repo.getActiveTotal()
            _allowDebt.value = repo.isDebtAllowed()
            _paymentAccounts.value = accountsRepo.getAccounts()
            _isLoading.value = false
        }
    }

    fun payDebt(amount: Double, accountId: Int, confirmation: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            _isLoading.value = true
            val success = repo.payDebt(amount, accountId, confirmation)
            _isLoading.value = false
            if (success) {
                _activeTotal.value = maxOf(0.0, _activeTotal.value - amount)
                onSuccess()
            }
        }
    }
}

class NotificationsViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = NotificationRepository(application)

    private val _notifications = MutableStateFlow<List<Notification>>(emptyList())
    val notifications: StateFlow<List<Notification>> = _notifications.asStateFlow()

    val unreadCount: StateFlow<Int> = _notifications.map { list ->
        list.count { !it.read }
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), 0)

    init {
        loadNotifications()
    }

    fun loadNotifications() {
        viewModelScope.launch {
            _notifications.value = repo.getNotifications()
        }
    }

    fun markRead(id: Int) {
        viewModelScope.launch {
            repo.markNotificationRead(id)
            _notifications.value = _notifications.value.map {
                if (it.id == id) it.copy(read = true) else it
            }
        }
    }
}

class ChatAdminViewModel(application: Application) : AndroidViewModel(application) {
    private val repo = SupportRepository()
    private val sessionManager = SessionManager(application)

    private val _messages = MutableStateFlow<List<ContactMessage>>(listOf(
        ContactMessage(text = "Welcome to the Shemsu Shop Concierge. How can I assist you with your gourmet experience today?", isUser = false),
        ContactMessage(text = "Hello! I wanted to check the status of my order #SHM-9821. It's been pending for 20 minutes.", isUser = true),
        ContactMessage(text = "Checking that for you right now, Gourmet Guest. One moment please.", isUser = false)
    ))
    val messages: StateFlow<List<ContactMessage>> = _messages.asStateFlow()

    fun sendMessage(text: String) {
        if (text.isBlank()) return
        val userMsg = ContactMessage(text = text, isUser = true)
        _messages.value = _messages.value + userMsg

        viewModelScope.launch {
            repo.postContact(sessionManager.getUserId(), sessionManager.getUsername(), text)
            // Mock response after 1.5s
            kotlinx.coroutines.delay(1500)
            val replyText = when {
                text.contains("order", ignoreCase = true) || text.contains("shm", ignoreCase = true) -> {
                    "Absolutely! I've updated your order notes. The chef will add extra avocado to your Artisanal Harvest Bowl. Anything else?"
                }
                text.contains("debt", ignoreCase = true) || text.contains("payment", ignoreCase = true) -> {
                    "Your payment has been received. I've credited it to your active debt database node. Thank you!"
                }
                else -> {
                    "Understood. Your request has been transmitted directly to our on-duty chef and concierge admin. We are on it!"
                }
            }
            _messages.value = _messages.value + ContactMessage(text = replyText, isUser = false)
        }
    }
}

class HelpViewModel : androidx.lifecycle.ViewModel() {
    private val _helpCategories = MutableStateFlow<List<Map<String, String>>>(listOf(
        mapOf(
            "title" to "How to Order",
            "content" to "Browsing our collection is simple. Select your desired artisanal dishes, customize your preferences, and add them to your cart. Proceed to checkout to choose your delivery window and payment method. Our gourmet chefs will begin preparation immediately."
        ),
        mapOf(
            "title" to "Bot Not Responding",
            "content" to "If our digital concierge is unresponsive, please try refreshing the app or checking your internet connection. If the issue persists, the system might be undergoing maintenance. You can always use the 'Contact Admin' button below for immediate human assistance."
        ),
        mapOf(
            "title" to "Delivery Tracking",
            "content" to "Real-time tracking becomes available once your order leaves our kitchen. Visit the 'Orders' tab and select your active delivery to see the live location of your dedicated courier on the map."
        ),
        mapOf(
            "title" to "Membership Perks",
            "content" to "As a Gold Member, you enjoy priority preparation, zero delivery fees on orders over $50, and exclusive access to seasonal tasting menus. Your points can be redeemed for gourmet upgrades at any time."
        )
    ))
    val helpCategories: StateFlow<List<Map<String, String>>> = _helpCategories.asStateFlow()
}

class FeedbackViewModel : androidx.lifecycle.ViewModel() {
    private val repo = FeedbackRepository()

    fun submitFeedback(userId: Long, rating: Float, comment: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            val combined = "Rating: ${rating} Stars. Comment: $comment"
            val success = repo.submitFeedback(userId, combined)
            if (success) {
                onSuccess()
            }
        }
    }
}
