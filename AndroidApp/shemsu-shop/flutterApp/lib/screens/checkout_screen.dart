import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../viewmodels/cart_viewmodel.dart';
import '../viewmodels/orders_viewmodel.dart';
import '../viewmodels/debt_viewmodel.dart';
import '../viewmodels/auth_viewmodel.dart';
import '../core/theme.dart';
import '../core/constants.dart';
import 'common_widgets.dart';

class CheckoutScreen extends StatefulWidget {
  const CheckoutScreen({super.key});

  @override
  State<CheckoutScreen> createState() => _CheckoutScreenState();
}

class _CheckoutScreenState extends State<CheckoutScreen> {
  String _selectedMethod = 'CBE Transfer';
  int? _selectedAccountId;
  final _refCtrl = TextEditingController();
  final _commentCtrl = TextEditingController();
  bool _isPlacing = false;

  final List<String> _methods = ['CBE Transfer', 'Telebirr', 'Debt'];

  @override
  void dispose() {
    _refCtrl.dispose();
    _commentCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final cartVM = context.watch<CartViewModel>();
    final ordersVM = context.watch<OrdersViewModel>();
    final debtVM = context.watch<DebtViewModel>();
    final auth = context.read<AuthViewModel>();

    final subtotal = cartVM.totalPrice;
    final total = subtotal + AppConstants.deliveryFee;

    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      appBar: AppBar(title: const Text('Checkout')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const SectionTitle(title: 'Payment Method'),
            const SizedBox(height: 8),
            ..._methods.map((m) => _PaymentMethodTile(
              method: m,
              selected: _selectedMethod == m,
              enabled: m != 'Debt' || debtVM.allowDebt,
              onTap: () => setState(() => _selectedMethod = m),
            )),

            const SizedBox(height: 24),
            if (_selectedMethod != 'Debt') ...[
              const SectionTitle(title: 'Bank Account'),
              const SizedBox(height: 8),
              if (debtVM.paymentAccounts.isEmpty)
                const GlassCard(child: Text('Loading accounts...', style: TextStyle(color: AppTheme.onSurfaceVariant)))
              else
                ...debtVM.paymentAccounts.map((acc) => _AccountTile(
                  account: acc,
                  selected: _selectedAccountId == acc.id,
                  onTap: () => setState(() => _selectedAccountId = acc.id),
                )),
              const SizedBox(height: 16),
              TextField(
                controller: _refCtrl,
                decoration: InputDecoration(
                  labelText: 'Transaction Reference',
                  hintText: 'Paste your bank SMS confirmation ref',
                  prefixIcon: const Icon(Icons.receipt, color: AppTheme.primaryOrange),
                  helperText: 'Send the exact amount to the account above and paste the ref SMS',
                  helperStyle: TextStyle(color: AppTheme.onSurfaceVariant.withOpacity(0.6), fontSize: 11),
                ),
                style: const TextStyle(color: AppTheme.onSurface),
                maxLines: 2,
              ),
            ],

            if (_selectedMethod == 'Debt') ...[
              GlassCard(
                child: Row(
                  children: [
                    const Icon(Icons.info_outline, color: AppTheme.accentGold),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        debtVM.allowDebt ? 'Your debt limit allows this order.' : 'Debt is not enabled for your account.',
                        style: TextStyle(color: debtVM.allowDebt ? AppTheme.onSurfaceVariant : AppTheme.statusError),
                      ),
                    ),
                  ],
                ),
              ),
            ],

            const SizedBox(height: 24),
            const SectionTitle(title: 'Special Instructions'),
            const SizedBox(height: 8),
            TextField(
              controller: _commentCtrl,
              decoration: const InputDecoration(
                hintText: 'Any special requests?',
                prefixIcon: Icon(Icons.edit_note, color: AppTheme.primaryOrange),
              ),
              style: const TextStyle(color: AppTheme.onSurface),
              maxLines: 2,
            ),

            const SizedBox(height: 24),
            const SectionTitle(title: 'Order Summary'),
            const SizedBox(height: 8),
            GlassCard(
              child: Column(
                children: [
                  ...cartVM.items.map((item) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text('${item.qty}x ${item.name}', style: const TextStyle(color: AppTheme.onSurface)),
                        Text('Birr ${(item.price * item.qty).toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.onSurfaceVariant)),
                      ],
                    ),
                  )),
                  const Divider(color: AppTheme.onSurfaceVariant),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Subtotal', style: TextStyle(color: AppTheme.onSurfaceVariant)),
                      Text('Birr ${subtotal.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.onSurface)),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Delivery Fee', style: TextStyle(color: AppTheme.onSurfaceVariant)),
                      Text('Birr ${AppConstants.deliveryFee.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.onSurface)),
                    ],
                  ),
                  const Divider(color: AppTheme.accentGold),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text('Total', style: TextStyle(color: AppTheme.accentGold, fontWeight: FontWeight.bold, fontSize: 18)),
                      Text('Birr ${total.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.accentGold, fontWeight: FontWeight.bold, fontSize: 18)),
                    ],
                  ),
                ],
              ),
            ),

            const SizedBox(height: 32),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isPlacing ? null : () => _placeOrder(context, total),
                child: _isPlacing
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                  : Text('Place Order - Birr ${total.toStringAsFixed(2)}'),
              ),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Future<void> _placeOrder(BuildContext context, double total) async {
    if (_selectedMethod != 'Debt' && _selectedAccountId == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please select a bank account')));
      return;
    }
    if (_selectedMethod != 'Debt' && _refCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please enter transaction reference')));
      return;
    }

    setState(() => _isPlacing = true);

    final cartVM = context.read<CartViewModel>();
    final ordersVM = context.read<OrdersViewModel>();
    final auth = context.read<AuthViewModel>();

    final res = await ordersVM.placeOrder(
      userId: auth.userId!,
      username: auth.username,
      fullName: auth.fullName,
      items: cartVM.items,
      paymentMethod: _selectedMethod,
      paymentAccountId: _selectedMethod != 'Debt' ? _selectedAccountId : null,
      confirmation: _selectedMethod != 'Debt' ? _refCtrl.text.trim() : null,
      comment: _commentCtrl.text.trim().isEmpty ? null : _commentCtrl.text.trim(),
    );

    setState(() => _isPlacing = false);

    if (res.success) {
      await cartVM.clearCart();
      if (context.mounted) {
        Navigator.pushReplacementNamed(context, '/order_success', arguments: res.orderGroup ?? 'SHM-00000');
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(res.error ?? 'Failed to place order')));
    }
  }
}

class _PaymentMethodTile extends StatelessWidget {
  final String method;
  final bool selected;
  final bool enabled;
  final VoidCallback onTap;

  const _PaymentMethodTile({required this.method, required this.selected, required this.enabled, required this.onTap});

  IconData get _icon {
    switch (method) {
      case 'CBE Transfer': return Icons.account_balance;
      case 'Telebirr': return Icons.phone_android;
      case 'Debt': return Icons.credit_card;
      default: return Icons.payment;
    }
  }

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: enabled ? onTap : null,
      child: GlassCard(
        margin: const EdgeInsets.only(bottom: 8),
        child: Row(
          children: [
            Icon(_icon, color: selected ? AppTheme.primaryOrange : AppTheme.onSurfaceVariant),
            const SizedBox(width: 12),
            Expanded(child: Text(method, style: TextStyle(color: enabled ? AppTheme.onSurface : AppTheme.onSurfaceVariant.withOpacity(0.4), fontWeight: FontWeight.w600))),
            if (selected)
              const Icon(Icons.check_circle, color: AppTheme.accentGold)
            else if (!enabled)
              const Icon(Icons.lock, color: AppTheme.onSurfaceVariant, size: 18),
          ],
        ),
      ),
    );
  }
}

class _AccountTile extends StatelessWidget {
  final PaymentAccount account;
  final bool selected;
  final VoidCallback onTap;

  const _AccountTile({required this.account, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: GlassCard(
        margin: const EdgeInsets.only(bottom: 6),
        padding: const EdgeInsets.all(12),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(account.bankName, style: const TextStyle(color: AppTheme.onSurface, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 2),
                  Text(account.number, style: const TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 13)),
                  Text(account.holderName, style: TextStyle(color: AppTheme.onSurfaceVariant.withOpacity(0.6), fontSize: 12)),
                ],
              ),
            ),
            if (selected) const Icon(Icons.check_circle, color: AppTheme.accentGold),
          ],
        ),
      ),
    );
  }
}
