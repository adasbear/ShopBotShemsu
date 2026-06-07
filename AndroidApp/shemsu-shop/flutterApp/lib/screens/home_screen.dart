import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/auth_viewmodel.dart';
import '../viewmodels/debt_viewmodel.dart';
import '../core/theme.dart';
import 'common_widgets.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthViewModel>();
    final debtVM = context.watch<DebtViewModel>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const SizedBox(height: 8),
          Text(
            'Hi, ${auth.fullName.split(' ').first} \u{1F44B}',
            style: const TextStyle(fontFamily: 'serif', fontWeight: FontWeight.bold, fontSize: 24, color: AppTheme.onSurface),
          ),
          const Text('Welcome back to the harvest.', style: TextStyle(fontSize: 14, color: AppTheme.onSurfaceVariant)),
          const SizedBox(height: 24),

          if (debtVM.activeTotal > 0.0)
            GlassCard(
              margin: const EdgeInsets.only(bottom: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Active Debt', style: TextStyle(color: AppTheme.onSurfaceVariant)),
                      const SizedBox(height: 4),
                      Text('Birr ${debtVM.activeTotal.toStringAsFixed(2)}',
                        style: const TextStyle(color: AppTheme.accentGold, fontSize: 20, fontWeight: FontWeight.bold)),
                    ],
                  ),
                  ElevatedButton(
                    onPressed: () => Navigator.pushNamed(context, '/debt'),
                    child: const Text('Pay Now'),
                  ),
                ],
              ),
            ),

          const SectionTitle(title: 'Quick Actions'),
          const SizedBox(height: 8),
          GridView(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2, mainAxisSpacing: 16, crossAxisSpacing: 16, childAspectRatio: 1.2,
            ),
            children: [
              ActionTile(icon: Icons.restaurant_menu, label: 'Order Now', onTap: () => Navigator.pushNamed(context, '/menu')),
              ActionTile(icon: Icons.wallet, label: 'My Debt', onTap: () => Navigator.pushNamed(context, '/debt')),
              ActionTile(icon: Icons.receipt_long, label: 'My Orders', onTap: () => Navigator.pushNamed(context, '/orders')),
              ActionTile(icon: Icons.help, label: 'Help Center', onTap: () => Navigator.pushNamed(context, '/help')),
            ],
          ),

          const SizedBox(height: 24),
          const SectionTitle(title: 'Quick Info'),
          const SizedBox(height: 8),
          GlassCard(
            child: Row(
              children: [
                const Icon(Icons.workspace_premium, color: AppTheme.accentGold, size: 32),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Gold Patron', style: TextStyle(color: AppTheme.onSurface, fontWeight: FontWeight.bold, fontSize: 16)),
                      const Text('Enjoy priority service and exclusive offers.', style: TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 13)),
                    ],
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(height: 24),
        ],
      ),
    );
  }
}
