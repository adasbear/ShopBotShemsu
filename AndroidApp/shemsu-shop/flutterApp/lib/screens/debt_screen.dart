import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../viewmodels/debt_viewmodel.dart';
import '../viewmodels/auth_viewmodel.dart';
import '../core/theme.dart';
import 'common_widgets.dart';

class DebtScreen extends StatefulWidget {
  const DebtScreen({super.key});

  @override
  State<DebtScreen> createState() => _DebtScreenState();
}

class _DebtScreenState extends State<DebtScreen> {
  final _amountCtrl = TextEditingController();
  final _refCtrl = TextEditingController();
  int? _selectedAccountId;
  bool _paying = false;

  @override
  void dispose() {
    _amountCtrl.dispose();
    _refCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final debtVM = context.watch<DebtViewModel>();

    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      appBar: AppBar(title: const Text('My Debt')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            GlassCard(
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Outstanding Balance', style: TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 13)),
                      SizedBox(height: 4),
                    ],
                  ),
                  Text('Birr ${debtVM.activeTotal.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.accentGold, fontSize: 24, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
            if (debtVM.activeTotal > 0) ...[
              const SizedBox(height: 24),
              const SectionTitle(title: 'Settle Debt'),
              TextField(
                controller: _amountCtrl,
                decoration: const InputDecoration(
                  labelText: 'Amount (Birr)',
                  prefixIcon: Icon(Icons.money, color: AppTheme.primaryOrange),
                ),
                style: const TextStyle(color: AppTheme.onSurface),
                keyboardType: TextInputType.number,
              ),
              const SizedBox(height: 12),
              const Text('Select Payment Account:', style: TextStyle(color: AppTheme.onSurfaceVariant)),
              const SizedBox(height: 8),
              ...debtVM.paymentAccounts.map((acc) => InkWell(
                onTap: () => setState(() => _selectedAccountId = acc.id),
                child: GlassCard(
                  margin: const EdgeInsets.only(bottom: 6),
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(acc.bankName, style: const TextStyle(color: AppTheme.onSurface, fontWeight: FontWeight.bold)),
                            Text(acc.number, style: const TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 13)),
                          ],
                        ),
                      ),
                      if (_selectedAccountId == acc.id) const Icon(Icons.check_circle, color: AppTheme.accentGold),
                    ],
                  ),
                ),
              )),
              const SizedBox(height: 12),
              TextField(
                controller: _refCtrl,
                decoration: const InputDecoration(
                  labelText: 'Transaction Reference',
                  prefixIcon: Icon(Icons.receipt, color: AppTheme.primaryOrange),
                ),
                style: const TextStyle(color: AppTheme.onSurface),
              ),
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: _paying ? null : () => _pay(context),
                  child: _paying
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                    : const Text('Pay Now'),
                ),
              ),
            ],
            const SizedBox(height: 24),
            const SectionTitle(title: 'Payment History'),
            if (debtVM.debts.isEmpty)
              const GlassCard(child: Text('No debt records', style: TextStyle(color: AppTheme.onSurfaceVariant)))
            else
              ...debtVM.debts.map((d) => GlassCard(
                margin: const EdgeInsets.only(bottom: 8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Birr ${d.amount.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.onSurface, fontWeight: FontWeight.bold)),
                        if (d.description != null) Text(d.description!, style: TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 12)),
                      ],
                    ),
                    StatusPill(status: d.status),
                  ],
                ),
              )),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Future<void> _pay(BuildContext context) async {
    final amount = double.tryParse(_amountCtrl.text.trim());
    if (amount == null || amount <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter a valid amount')));
      return;
    }
    if (_selectedAccountId == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Select a payment account')));
      return;
    }
    if (_refCtrl.text.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Enter transaction reference')));
      return;
    }

    setState(() => _paying = true);
    final debtVM = context.read<DebtViewModel>();
    final auth = context.read<AuthViewModel>();

    final ok = await debtVM.payDebt(
      username: auth.username,
      userId: auth.userId!,
      amount: amount,
      paymentAccountId: _selectedAccountId!,
      confirmation: _refCtrl.text.trim(),
    );

    setState(() => _paying = false);

    if (context.mounted) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
        content: Text(ok ? 'Payment submitted' : debtVM.error ?? 'Payment failed'),
        backgroundColor: ok ? AppTheme.statusAccepted : AppTheme.statusError,
      ));
    }
  }
}
