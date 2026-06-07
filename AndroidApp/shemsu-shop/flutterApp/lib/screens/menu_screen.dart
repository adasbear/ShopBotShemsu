import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/models.dart';
import '../viewmodels/menu_viewmodel.dart';
import '../viewmodels/cart_viewmodel.dart';
import '../core/theme.dart';
import 'common_widgets.dart';
import 'cart_screen.dart';

class MenuScreen extends StatelessWidget {
  const MenuScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final menuVM = context.watch<MenuViewModel>();
    final cartVM = context.watch<CartViewModel>();

    if (menuVM.isLoading && menuVM.items.isEmpty) {
      return const Center(child: CircularProgressIndicator(color: AppTheme.accentGold));
    }

    return Stack(
      children: [
        Column(
          children: [
            if (menuVM.categories.isNotEmpty)
              Container(
                height: 48,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  children: [
                    _CategoryChip(
                      label: 'All',
                      selected: menuVM.selectedCategory == null,
                      onTap: () => menuVM.selectCategory(null),
                    ),
                    ...menuVM.categories.map((cat) => _CategoryChip(
                      label: cat.name,
                      selected: menuVM.selectedCategory == cat.name,
                      onTap: () => menuVM.selectCategory(cat.name),
                    )),
                  ],
                ),
              ),
            const SizedBox(height: 8),
            Expanded(
              child: GridView.builder(
                padding: const EdgeInsets.fromLTRB(16, 8, 16, 96),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  mainAxisSpacing: 16,
                  crossAxisSpacing: 16,
                  childAspectRatio: 0.72,
                ),
                itemCount: menuVM.subItems.length,
                itemBuilder: (context, index) => _MenuItemCard(
                  item: menuVM.subItems[index],
                  cartVM: cartVM,
                ),
              ),
            ),
          ],
        ),
        if (cartVM.items.isNotEmpty)
          Positioned(
            left: 0, right: 0, bottom: 0,
            child: Container(
              padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
              decoration: const BoxDecoration(
                color: AppTheme.surfaceElevated,
                borderRadius: BorderRadius.only(topLeft: Radius.circular(20), topRight: Radius.circular(20)),
              ),
              child: Row(
                children: [
                  Expanded(
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('${cartVM.items.length} item(s)', style: const TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 13)),
                        Text('Birr ${cartVM.totalPrice.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.accentGold, fontSize: 18, fontWeight: FontWeight.bold)),
                      ],
                    ),
                  ),
                  ElevatedButton(
                    onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CartScreen())),
                    child: const Text('View Cart'),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }
}

class _CategoryChip extends StatelessWidget {
  final String label;
  final bool selected;
  final VoidCallback onTap;

  const _CategoryChip({required this.label, required this.selected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: ChoiceChip(
        label: Text(label),
        selected: selected,
        onSelected: (_) => onTap(),
        selectedColor: AppTheme.primaryContainerOrange,
        backgroundColor: AppTheme.surfaceContainerLow,
        labelStyle: TextStyle(color: selected ? Colors.white : AppTheme.onSurfaceVariant, fontWeight: FontWeight.w600),
        side: BorderSide.none,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      ),
    );
  }
}

class _MenuItemCard extends StatelessWidget {
  final MenuItem item;
  final CartViewModel cartVM;

  const _MenuItemCard({required this.item, required this.cartVM});

  @override
  Widget build(BuildContext context) {
    return GlassCard(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Container(
              width: double.infinity,
              decoration: BoxDecoration(
                color: Colors.grey.withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(Icons.fastfood, color: AppTheme.onSurface.withOpacity(0.4), size: 40),
            ),
          ),
          const SizedBox(height: 10),
          Text(item.name, style: const TextStyle(color: AppTheme.onSurface, fontWeight: FontWeight.bold, fontSize: 14), maxLines: 1, overflow: TextOverflow.ellipsis),
          const SizedBox(height: 4),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Birr ${item.price.toStringAsFixed(2)}', style: const TextStyle(color: AppTheme.accentGold, fontWeight: FontWeight.bold, fontSize: 14)),
              InkWell(
                onTap: () {
                  cartVM.addToCart(CartItem(name: item.name, price: item.price, qty: 1));
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                    content: Text('${item.name} added'),
                    backgroundColor: AppTheme.accentGold,
                    duration: const Duration(seconds: 1),
                  ));
                },
                child: Container(
                  padding: const EdgeInsets.all(4),
                  decoration: BoxDecoration(color: AppTheme.accentGold, borderRadius: BorderRadius.circular(8)),
                  child: const Icon(Icons.add, color: Colors.black, size: 20),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
