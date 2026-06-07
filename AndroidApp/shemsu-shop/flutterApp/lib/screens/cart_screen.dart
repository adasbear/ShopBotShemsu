import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/cart_viewmodel.dart';
import '../core/theme.dart';
import '../core/constants.dart';
import 'common_widgets.dart';
import 'checkout_screen.dart';

class CartScreen extends StatelessWidget {
  const CartScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final cartVM = context.watch<CartViewModel>();
    final subtotal = cartVM.totalPrice;
    final total = subtotal + AppConstants.deliveryFee;

    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      appBar: AppBar(title: const Text('Your Cart')),
      body: cartVM.items.isEmpty
        ? const Center(child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.shopping_cart_outlined, color: AppTheme.onSurfaceVariant, size: 64),
              SizedBox(height: 16),
              Text('Your cart is empty.', style: TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 18)),
            ],
          ))
        : Column(
            children: [
              Expanded(
                child: ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: cartVM.items.length,
                  itemBuilder: (context, index) {
                    final item = cartVM.items[index];
                    return GlassCard(
                      margin: const EdgeInsets.only(bottom: 12),
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          Container(
                            width: 60, height: 60,
                            decoration: BoxDecoration(
                              color: Colors.grey.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Icon(Icons.fastfood, color: AppTheme.onSurface),
                          ),
                          const SizedBox(width: 16),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(item.name, style: const TextStyle(color: AppTheme.onSurface, fontWeight: FontWeight.bold, fontSize: 15)),
                                const SizedBox(height: 4),
                                Text('Birr ${item.price.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 13)),
                              ],
                            ),
                          ),
                          Row(
                            children: [
                              IconButton(
                                icon: const Icon(Icons.remove, color: AppTheme.onSurfaceVariant, size: 20),
                                onPressed: () => cartVM.updateQty(item.name, item.qty - 1),
                              ),
                              Text('${item.qty}', style: const TextStyle(color: AppTheme.onSurface, fontWeight: FontWeight.bold)),
                              IconButton(
                                icon: const Icon(Icons.add, color: AppTheme.onSurfaceVariant, size: 20),
                                onPressed: () => cartVM.updateQty(item.name, item.qty + 1),
                              ),
                            ],
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete_outline, color: AppTheme.statusError, size: 20),
                            onPressed: () => cartVM.removeFromCart(item.name),
                          ),
                        ],
                      ),
                    );
                  },
                ),
              ),
              Container(
                padding: const EdgeInsets.fromLTRB(24, 16, 24, 24),
                decoration: const BoxDecoration(
                  color: AppTheme.surfaceGlass,
                  borderRadius: BorderRadius.only(topLeft: Radius.circular(24), topRight: Radius.circular(24)),
                ),
                child: SafeArea(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Subtotal', style: TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 14)),
                          Text('Birr ${subtotal.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.onSurface, fontSize: 14)),
                        ],
                      ),
                      const SizedBox(height: 4),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Delivery Fee', style: TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 14)),
                          Text('Birr ${AppConstants.deliveryFee.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.onSurface, fontSize: 14)),
                        ],
                      ),
                      const Divider(color: AppTheme.accentGold, height: 24),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text('Total', style: TextStyle(color: AppTheme.accentGold, fontSize: 20, fontWeight: FontWeight.bold)),
                          Text('Birr ${total.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.accentGold, fontSize: 20, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      const SizedBox(height: 16),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CheckoutScreen())),
                          child: const Text('Proceed to Checkout'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
    );
  }
}
