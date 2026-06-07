import 'package:flutter/material.dart';
import '../core/theme.dart';
import 'common_widgets.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  static final _faqs = [
    _FaqCategory('Orders', [
      _FaqItem('How do I place an order?', 'Browse the Menu, add items to cart, proceed to Checkout, choose payment method, and confirm.'),
      _FaqItem('Can I cancel my order?', 'Yes, if the order status is still "Pending". Go to My Orders, tap the order, and select Cancel.'),
      _FaqItem('How do I edit an order?', 'Contact the admin via Contact Admin in your Profile.'),
    ]),
    _FaqCategory('Payments', [
      _FaqItem('What payment methods are accepted?', 'CBE Transfer, Telebirr, and Debt (if enabled).'),
      _FaqItem('How do I pay with debt?', 'You must be on the debt allow list. Contact admin to be added.'),
      _FaqItem('Where do I send payment?', 'Select a bank account during checkout and transfer the exact amount.'),
    ]),
    _FaqCategory('Debt', [
      _FaqItem('What is the debt system?', 'Eligible users can order on credit and pay later.'),
      _FaqItem('How do I pay my debt?', 'Go to My Debt in Profile, enter the amount, select an account, and submit the transaction ref.'),
    ]),
    _FaqCategory('Delivery', [
      _FaqItem('When will my order arrive?', 'Once accepted and prepared, the admin will mark it as Ready and then Delivered.'),
      _FaqItem('Can I change my delivery address?', 'Contact the admin directly.'),
    ]),
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      appBar: AppBar(title: const Text('Help & FAQ')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: _faqs.map((cat) => _FaqCategoryCard(category: cat)).toList(),
      ),
    );
  }
}

class _FaqCategory {
  final String title;
  final List<_FaqItem> items;
  _FaqCategory(this.title, this.items);
}

class _FaqItem {
  final String question;
  final String answer;
  _FaqItem(this.question, this.answer);
}

class _FaqCategoryCard extends StatefulWidget {
  final _FaqCategory category;
  const _FaqCategoryCard({required this.category});

  @override
  State<_FaqCategoryCard> createState() => _FaqCategoryCardState();
}

class _FaqCategoryCardState extends State<_FaqCategoryCard> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      margin: const EdgeInsets.only(bottom: 12),
      child: Column(
        children: [
          InkWell(
            onTap: () => setState(() => _expanded = !_expanded),
            child: Row(
              children: [
                Text(widget.category.title, style: const TextStyle(color: AppTheme.onSurface, fontSize: 18, fontWeight: FontWeight.bold)),
                const Spacer(),
                Icon(_expanded ? Icons.expand_less : Icons.expand_more, color: AppTheme.onSurfaceVariant),
              ],
            ),
          ),
          if (_expanded) ...[
            const SizedBox(height: 12),
            ...widget.category.items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(item.question, style: const TextStyle(color: AppTheme.accentGold, fontWeight: FontWeight.w600, fontSize: 14)),
                  const SizedBox(height: 4),
                  Text(item.answer, style: const TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 13)),
                ],
              ),
            )),
          ],
        ],
      ),
    );
  }
}
