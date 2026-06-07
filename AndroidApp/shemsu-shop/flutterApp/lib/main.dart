import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'core/theme.dart';
import 'core/session_manager.dart';
import 'core/constants.dart';
import 'data/api_service.dart';
import 'data/local_db.dart';

import 'viewmodels/auth_viewmodel.dart';
import 'viewmodels/menu_viewmodel.dart';
import 'viewmodels/cart_viewmodel.dart';
import 'viewmodels/orders_viewmodel.dart';
import 'viewmodels/debt_viewmodel.dart';
import 'viewmodels/notifications_viewmodel.dart';
import 'viewmodels/feedback_viewmodel.dart';
import 'viewmodels/chat_viewmodel.dart';

import 'screens/splash_screen.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'screens/menu_screen.dart';
import 'screens/cart_screen.dart';
import 'screens/orders_screen.dart';
import 'screens/order_success_screen.dart';
import 'screens/debt_screen.dart';
import 'screens/profile_screen.dart';
import 'screens/help_screen.dart';
import 'screens/feedback_screen.dart';
import 'screens/contact_admin_screen.dart';
import 'screens/notifications_screen.dart';
import 'screens/common_widgets.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final session = SessionManager(prefs);
  final apiService = ApiService();

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthViewModel(apiService, session)),
        ChangeNotifierProvider(create: (_) => MenuViewModel(apiService)),
        ChangeNotifierProvider(create: (_) => CartViewModel()),
        ChangeNotifierProvider(create: (_) => OrdersViewModel(apiService)),
        ChangeNotifierProvider(create: (_) => DebtViewModel(apiService)),
        ChangeNotifierProvider(create: (_) => NotificationsViewModel(apiService)),
        ChangeNotifierProvider(create: (_) => FeedbackViewModel(apiService)),
        ChangeNotifierProvider(create: (_) => ChatViewModel(apiService)),
      ],
      child: const ShemsuShopApp(),
    ),
  );
}

class ShemsuShopApp extends StatelessWidget {
  const ShemsuShopApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: AppConstants.appName,
      theme: AppTheme.darkTheme,
      debugShowCheckedModeBanner: false,
      initialRoute: '/splash',
      onGenerateRoute: _generateRoute,
    );
  }

  Route<dynamic>? _generateRoute(RouteSettings settings) {
    switch (settings.name) {
      case '/splash':
        return MaterialPageRoute(builder: (_) => const SplashScreen());
      case '/login':
        return MaterialPageRoute(builder: (_) => const LoginScreen());
      case '/home':
        return MaterialPageRoute(builder: (_) => const MainShell());
      case '/orders':
        return MaterialPageRoute(builder: (_) => const ScreenWrapper(title: 'My Orders', child: OrdersScreen()));
      case '/order_success':
        final ref = settings.arguments as String? ?? 'SHM-00000';
        return MaterialPageRoute(builder: (_) => OrderSuccessScreen(orderRef: ref));
      case '/debt':
        return MaterialPageRoute(builder: (_) => const ScreenWrapper(title: 'My Debt', child: DebtScreen()));
      case '/help':
        return MaterialPageRoute(builder: (_) => const HelpScreen());
      case '/feedback':
        return MaterialPageRoute(builder: (_) => const FeedbackScreen());
      case '/contact_admin':
        return MaterialPageRoute(builder: (_) => const ContactAdminScreen());
      case '/notifications':
        return MaterialPageRoute(builder: (_) => const ScreenWrapper(title: 'Notifications', child: NotificationsScreen()));
      default:
        return MaterialPageRoute(builder: (_) => const SplashScreen());
    }
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      final auth = context.read<AuthViewModel>();
      final menuVM = context.read<MenuViewModel>();
      final ordersVM = context.read<OrdersViewModel>();
      final debtVM = context.read<DebtViewModel>();
      final notifVM = context.read<NotificationsViewModel>();

      menuVM.loadMenu();
      debtVM.loadPaymentAccounts();
      if (auth.username.isNotEmpty) {
        ordersVM.loadOrders(auth.userId!);
        debtVM.loadDebts(auth.username);
        debtVM.checkDebtAllowed(auth.username);
        notifVM.loadNotifications(auth.userId!);
      }
    });
  }

  static const _titles = ['Shemsu Shop', 'Gourmet Kitchen', 'Your Cart', 'Patron Center'];

  @override
  Widget build(BuildContext context) {
    final cartVM = context.watch<CartViewModel>();
    final notifVM = context.watch<NotificationsViewModel>();

    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      appBar: _currentIndex != 2
        ? AppBar(title: Text(_titles[_currentIndex]))
        : null,
      body: IndexedStack(
        index: _currentIndex,
        children: const [
          HomeScreen(),
          MenuScreen(),
          CartScreen(),
          ProfileScreen(),
        ],
      ),
      bottomNavigationBar: ShemsuBottomBar(
        currentIndex: _currentIndex,
        cartBadgeCount: cartVM.items.length,
        notificationBadgeCount: notifVM.unreadCount,
        onTap: (i) => setState(() => _currentIndex = i),
      ),
    );
  }
}

class ScreenWrapper extends StatelessWidget {
  final String title;
  final Widget child;

  const ScreenWrapper({super.key, required this.title, required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      appBar: AppBar(title: Text(title)),
      body: child,
    );
  }
}
