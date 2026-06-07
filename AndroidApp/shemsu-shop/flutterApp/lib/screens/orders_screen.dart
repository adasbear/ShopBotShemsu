import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../viewmodels/orders_viewmodel.dart';
import '../core/theme.dart';
import 'common_widgets.dart';
import 'order_detail_screen.dart';

class OrdersScreen extends StatefulWidget {
  const OrdersScreen({super.key});

  @override
  State<OrdersScreen> createState() => _OrdersScreenState();
}

class _OrdersScreenState extends State<OrdersScreen> with SingleTickerProviderStateMixin {
  late TabController _tabCtrl;

  @override
  void initState() {
    super.initState();
    _tabCtrl = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final ordersVM = context.watch<OrdersViewModel>();

    return Column(
      children: [
        TabBar(
          controller: _tabCtrl,
          tabs: [
            Tab(text: 'Active (${ordersVM.activeOrders.length})'),
            Tab(text: 'History (${ordersVM.historyOrders.length})'),
          ],
          labelColor: AppTheme.primaryOrange,
          unselectedLabelColor: AppTheme.onSurfaceVariant,
          indicatorColor: AppTheme.primaryOrange,
        ),
        Expanded(
          child: ordersVM.isLoading
            ? const Center(child: CircularProgressIndicator(color: AppTheme.accentGold))
            : TabBarView(
              controller: _tabCtrl,
              children: [
                _OrderList(orders: ordersVM.activeOrders, onTap: (o) => Navigator.push(context, MaterialPageRoute(builder: (_) => OrderDetailScreen(order: o)))),
                _OrderList(orders: ordersVM.historyOrders, onTap: (o) => Navigator.push(context, MaterialPageRoute(builder: (_) => OrderDetailScreen(order: o)))),
              ],
            ),
        ),
      ],
    );
  }
}

class _OrderList extends StatelessWidget {
  final List<OrderGroup> orders;
  final ValueChanged<OrderGroup> onTap;

  const _OrderList({required this.orders, required this.onTap});

  @override
  Widget build(BuildContext context) {
    if (orders.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.receipt_long, color: AppTheme.onSurfaceVariant.withOpacity(0.3), size: 64),
            const SizedBox(height: 16),
            const Text('No orders found', style: TextStyle(color: AppTheme.onSurfaceVariant)),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: orders.length,
      itemBuilder: (context, index) {
        final order = orders[index];
        final itemText = order.items.map((i) => '${i.qty}x ${i.item}').join(', ');
        return InkWell(
          onTap: () => onTap(order),
          child: GlassCard(
            margin: const EdgeInsets.only(bottom: 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(order.orderGroup, style: const TextStyle(color: AppTheme.accentGold, fontWeight: FontWeight.bold, fontSize: 14)),
                    StatusPill(status: order.status),
                  ],
                ),
                const SizedBox(height: 8),
                Text(itemText, style: const TextStyle(color: AppTheme.onSurface, fontSize: 14), maxLines: 2, overflow: TextOverflow.ellipsis),
                const SizedBox(height: 4),
                Text('Birr ${order.total.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 13)),
                if (order.timestamp != null)
                  Text(order.timestamp!, style: TextStyle(color: AppTheme.onSurfaceVariant.withOpacity(0.5), fontSize: 11)),
              ],
            ),
          ),
        );
      },
    );
  }
}
