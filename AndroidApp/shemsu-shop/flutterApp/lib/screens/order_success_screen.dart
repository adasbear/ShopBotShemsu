import 'package:flutter/material.dart';
import '../core/theme.dart';

class OrderSuccessScreen extends StatelessWidget {
  final String orderRef;

  const OrderSuccessScreen({super.key, required this.orderRef});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 100, height: 100,
                decoration: BoxDecoration(
                  color: AppTheme.statusAccepted.withOpacity(0.2),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.check_circle, color: AppTheme.statusAccepted, size: 60),
              ),
              const SizedBox(height: 24),
              const Text('Order Placed!', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppTheme.onSurface, fontFamily: 'serif')),
              const SizedBox(height: 8),
              Text('Reference: $orderRef', style: const TextStyle(fontSize: 16, color: AppTheme.accentGold, fontWeight: FontWeight.w600)),
              const SizedBox(height: 24),
              Text('Your order has been received. Track its status in My Orders.', style: TextStyle(color: AppTheme.onSurfaceVariant.withOpacity(0.8), fontSize: 14), textAlign: TextAlign.center),
              const SizedBox(height: 40),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: () => Navigator.pushNamedAndRemoveUntil(context, '/orders', (route) => false),
                  child: const Text('Track My Order'),
                ),
              ),
              const SizedBox(height: 12),
              TextButton(
                onPressed: () => Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false),
                child: const Text('Back to Dashboard', style: TextStyle(color: AppTheme.onSurfaceVariant)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
