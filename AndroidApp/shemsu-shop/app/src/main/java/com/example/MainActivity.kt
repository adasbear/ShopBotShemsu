package com.example

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.navigation.NamedNavArgument
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.example.data.model.OrderGroup
import com.example.ui.screens.*
import com.example.ui.theme.MyApplicationTheme
import com.example.viewmodel.*

class MainActivity : ComponentActivity() {
  override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    enableEdgeToEdge()
    setContent {
      MyApplicationTheme {
        val navController = rememberNavController()
        val snackbarHostState = remember { SnackbarHostState() }

        // Core ViewModels
        val authViewModel: AuthViewModel by viewModels()
        val menuViewModel: MenuViewModel by viewModels()
        val cartViewModel: CartViewModel by viewModels()
        val ordersViewModel: OrdersViewModel by viewModels()
        val debtViewModel: DebtViewModel by viewModels()
        val notificationsViewModel: NotificationsViewModel by viewModels()

        val navBackStackEntry by navController.currentBackStackEntryAsState()
        val currentRoute = navBackStackEntry?.destination?.route ?: "splash"

        val fullName by authViewModel.fullName.collectAsState()
        val username by authViewModel.username.collectAsState()
        val cartBadgeCount by cartViewModel.itemCount.collectAsState()
        val notificationsCount by notificationsViewModel.unreadCount.collectAsState()

        var activeSelectedOrder by remember { mutableStateOf<OrderGroup?>(null) }

        val showChrome = currentRoute in listOf("home", "menu", "orders", "profile")

        Scaffold(
          modifier = Modifier.fillMaxSize(),
          snackbarHost = { SnackbarHost(snackbarHostState) },
          topBar = {
            if (showChrome) {
              ShemsuTopBar(
                title = when (currentRoute) {
                  "home" -> "Shemsu Shop"
                  "menu" -> "Gourmet Kitchen"
                  "orders" -> "Order History"
                  "profile" -> "Patron Center"
                  else -> "Shemsu Shop"
                },
                showBack = false,
                cartBadgeCount = cartBadgeCount,
                onCartClick = { navController.navigate("cart") }
              )
            }
          },
          bottomBar = {
            if (showChrome) {
              ShemsuBottomBar(
                currentRoute = currentRoute,
                onNavigate = { route ->
                  navController.navigate(route) {
                    popUpTo(navController.graph.startDestinationId) { saveState = true }
                    launchSingleTop = true
                    restoreState = true
                  }
                },
                notificationsCount = notificationsCount
              )
            }
          }
        ) { innerPadding ->
          NavHost(
            navController = navController,
            startDestination = "splash",
            modifier = Modifier.padding(if (showChrome) innerPadding else androidx.compose.foundation.layout.PaddingValues())
          ) {
            // Splash flow
            composable("splash") {
              SplashScreen(viewModel = authViewModel) { loggedIn ->
                if (loggedIn) {
                  navController.navigate("home") {
                    popUpTo("splash") { inclusive = true }
                  }
                } else {
                  navController.navigate("login") {
                    popUpTo("splash") { inclusive = true }
                  }
                }
              }
            }

            // Authentication screen
            composable("login") {
              LoginScreen(viewModel = authViewModel) {
                navController.navigate("home") {
                  popUpTo("login") { inclusive = true }
                }
              }
            }

            // Primary Tabs
            composable("home") {
              HomeScreen(
                fullName = fullName,
                ordersViewModel = ordersViewModel,
                debtViewModel = debtViewModel,
                cartViewModel = cartViewModel
              ) { action ->
                when (action) {
                  "menu" -> navController.navigate("menu")
                  "orders" -> navController.navigate("orders")
                  "my_debt" -> navController.navigate("my_debt")
                  "help" -> navController.navigate("help")
                }
              }
            }

            composable("menu") {
              MenuScreen(
                menuViewModel = menuViewModel,
                cartViewModel = cartViewModel,
                onNavigateCart = { navController.navigate("cart") }
              )
            }

            composable("orders") {
              MyOrdersScreen(viewModel = ordersViewModel) { selectedGroup ->
                activeSelectedOrder = selectedGroup
                navController.navigate("order_detail")
              }
            }

            composable("profile") {
              ProfileScreen(
                fullName = fullName,
                username = username,
                authViewModel = authViewModel,
                notificationsViewModel = notificationsViewModel
              ) { action ->
                when (action) {
                  "notifications" -> navController.navigate("notifications")
                  "contact_admin" -> navController.navigate("contact_admin")
                  "help" -> navController.navigate("help")
                  "feedback" -> navController.navigate("feedback")
                  "my_debt" -> navController.navigate("my_debt")
                }
              }
            }

            // Checkout flow
            composable("cart") {
              CartScreen(
                viewModel = cartViewModel,
                onNavigateCheckout = { navController.navigate("checkout") },
                onNavigateMenu = { navController.navigate("menu") }
              )
            }

            composable("checkout") {
              CheckoutScreen(
                ordersViewModel = ordersViewModel,
                debtViewModel = debtViewModel,
                cartViewModel = cartViewModel,
                onSuccessPlaced = { orderRef ->
                  navController.navigate("success/$orderRef") {
                    popUpTo("cart") { inclusive = true }
                  }
                },
                onBack = { navController.popBackStack() }
              )
            }

            composable(
              route = "success/{ref}",
              arguments = listOf(navArgument("ref") { type = NavType.StringType })
            ) { backStackEntry ->
              val orderRef = backStackEntry.arguments?.getString("ref") ?: "SHM-00000"
              OrderSuccessScreen(
                orderGroup = orderRef,
                onNavigateOrders = {
                  navController.navigate("orders") {
                    popUpTo("home") { saveState = true }
                  }
                },
                onNavigateDashboard = {
                  navController.navigate("home") {
                    popUpTo("home") { inclusive = true }
                  }
                }
              )
            }

            // Auxiliary screens
            composable("order_detail") {
              activeSelectedOrder?.let { order ->
                OrderDetailScreen(
                  orderGroup = order,
                  viewModel = ordersViewModel,
                  onBack = { navController.popBackStack() }
                )
              }
            }

            composable("my_debt") {
              MyDebtScreen(viewModel = debtViewModel)
            }

            composable("help") {
              HelpScreen { navController.popBackStack() }
            }

            composable("feedback") {
              FeedbackScreen(userId = authViewModel.sessionManager.getUserId()) {
                navController.popBackStack()
              }
            }

            composable("contact_admin") {
              ContactAdminScreen { navController.popBackStack() }
            }

            composable("notifications") {
              NotificationsScreen(viewModel = notificationsViewModel) {
                navController.popBackStack()
              }
            }
          }
        }
      }
    }
  }
}
