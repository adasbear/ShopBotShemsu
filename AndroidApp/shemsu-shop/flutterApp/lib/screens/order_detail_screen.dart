import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../viewmodels/orders_viewmodel.dart';
import '../core/theme.dart';
import 'common_widgets.dart';

class OrderDetailScreen extends StatelessWidget {
  final OrderGroup order;

  const OrderDetailScreen({super.key, required this.order});

  @override
  Widget build(BuildContext context) {
    final ordersVM = context.watch<OrdersViewModel>();

    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      appBar: AppBar(title: Text(order.orderGroup)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Status timeline
            GlassCard(
              child: Column(
                children: [
                  _TimelineStep(label: 'Placed', active: true, isFirst: true),
                  _TimelineStep(label: 'Preparing', active: order.status == 'Accepted' || order.status == 'Ready' || order.status == 'Arrived' || order.status == 'Delivered'),
                  _TimelineStep(label: 'Ready', active: order.status == 'Ready' || order.status == 'Arrived' || order.status == 'Delivered'),
                  _TimelineStep(label: 'Delivered', active: order.status == 'Delivered', isLast: true),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Order details
            const SectionTitle(title: 'Items'),
            GlassCard(
              child: Column(
                children: order.items.map((item) => Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('${item.qty}x ${item.item}', style: const TextStyle(color: AppTheme.onSurface)),
                      if (item.status != null) StatusPill(status: item.status!),
                    ],
                  ),
                )).toList(),
              ),
            ),

            if (order.comment != null && order.comment!.isNotEmpty) ...[
              const SizedBox(height: 16),
              const SectionTitle(title: 'Special Instructions'),
              GlassCard(child: Text(order.comment!, style: const TextStyle(color: AppTheme.onSurfaceVariant))),
            ],

            if (order.declineReason != null && order.declineReason!.isNotEmpty) ...[
              const SizedBox(height: 16),
              const SectionTitle(title: 'Decline Reason'),
              GlassCard(
                child: Row(
                  children: [
                    const Icon(Icons.warning, color: AppTheme.statusError),
                    const SizedBox(width: 8),
                    Expanded(child: Text(order.declineReason!, style: const TextStyle(color: AppTheme.statusError))),
                  ],
                ),
              ),
            ],

            if (order.payment != null) ...[
              const SizedBox(height: 16),
              const SectionTitle(title: 'Payment'),
              GlassCard(child: Text(order.payment!, style: const TextStyle(color: AppTheme.onSurfaceVariant))),
            ],

            // Cancel button (only for pending orders)
            if (order.status == 'Pending') ...[
              const SizedBox(height: 32),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(backgroundColor: AppTheme.statusError.withOpacity(0.2)),
                  onPressed: () => _confirmCancel(context, ordersVM),
                  child: const Text('Cancel Order', style: TextStyle(color: AppTheme.statusError)),
                ),
              ),
            ],

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  void _confirmCancel(BuildContext context, OrdersViewModel ordersVM) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppTheme.surfaceContainerLow,
        title: const Text('Cancel Order?', style: TextStyle(color: AppTheme.onSurface)),
        content: const Text('This cannot be undone.', style: TextStyle(color: AppTheme.onSurfaceVariant)),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('No')),
          TextButton(
            onPressed: () async {
              Navigator.pop(ctx);
              final ok = await ordersVM.cancelOrder(order.orderGroup);
              if (context.mounted) {
                ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                  content: Text(ok ? 'Order cancelled' : 'Failed to cancel'),
                  backgroundColor: ok ? AppTheme.statusAccepted : AppTheme.statusError,
                ));
              }
            },
            child: const Text('Yes, Cancel', style: TextStyle(color: AppTheme.statusError)),
          ),
        ],
      ),
    );
  }
}

class _TimelineStep extends StatelessWidget {
  final String label;
  final bool active;
  final bool isFirst;
  final bool isLast;

  const _TimelineStep({required this.label, required this.active, this.isFirst = false, this.isLast = false});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Column(
          children: [
            if (!isFirst)
              Container(width: 2, height: 20, color: active ? AppTheme.primaryOrange : AppTheme.onSurfaceVariant.withOpacity(0.3)),
            Container(
              width: 16, height: 16,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: active ? AppTheme.primaryOrange : AppTheme.onSurfaceVariant.withOpacity(0.3),
              ),
              child: active ? const Icon(Icons.check, size: 10, color: Colors.white) : null,
            ),
            if (!isLast)
              Container(width: 2, height: 20, color: active ? AppTheme.primaryOrange : AppTheme.onSurfaceVariant.withOpacity(0.3)),
          ],
        ),
        const SizedBox(width: 12),
        Text(label, style: TextStyle(color: active ? AppTheme.onSurface : AppTheme.onSurfaceVariant.withOpacity(0.5), fontWeight: active ? FontWeight.bold : FontWeight.normal)),
      ],
    );
  }
}
