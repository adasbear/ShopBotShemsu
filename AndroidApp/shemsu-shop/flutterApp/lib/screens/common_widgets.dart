import 'package:flutter/material.dart';
import '../core/theme.dart';

class ShemsuBottomBar extends StatelessWidget {
  final int currentIndex;
  final ValueChanged<int> onTap;
  final int cartBadgeCount;
  final int notificationBadgeCount;

  const ShemsuBottomBar({
    super.key,
    required this.currentIndex,
    required this.onTap,
    this.cartBadgeCount = 0,
    this.notificationBadgeCount = 0,
  });

  @override
  Widget build(BuildContext context) {
    return BottomNavigationBar(
      currentIndex: currentIndex,
      onTap: onTap,
      items: [
        const BottomNavigationBarItem(icon: Icon(Icons.home_outlined), activeIcon: Icon(Icons.home), label: 'Home'),
        const BottomNavigationBarItem(icon: Icon(Icons.restaurant_menu_outlined), activeIcon: Icon(Icons.restaurant_menu), label: 'Menu'),
        BottomNavigationBarItem(
          icon: Badge(
            isLabelVisible: cartBadgeCount > 0,
            label: Text('$cartBadgeCount'),
            child: const Icon(Icons.shopping_cart_outlined),
          ),
          activeIcon: Badge(
            isLabelVisible: cartBadgeCount > 0,
            label: Text('$cartBadgeCount'),
            child: const Icon(Icons.shopping_cart),
          ),
          label: 'Cart',
        ),
        BottomNavigationBarItem(
          icon: Badge(
            isLabelVisible: notificationBadgeCount > 0,
            label: Text('$notificationBadgeCount'),
            child: const Icon(Icons.person_outline),
          ),
          activeIcon: Badge(
            isLabelVisible: notificationBadgeCount > 0,
            label: Text('$notificationBadgeCount'),
            child: const Icon(Icons.person),
          ),
          label: 'Profile',
        ),
      ],
    );
  }
}

class StatusPill extends StatelessWidget {
  final String status;

  const StatusPill({super.key, required this.status});

  @override
  Widget build(BuildContext context) {
    Color color;
    switch (status.toLowerCase()) {
      case 'pending':
        color = AppTheme.statusPending;
        break;
      case 'accepted':
        color = AppTheme.statusAccepted;
        break;
      case 'ready':
      case 'arrived':
        color = AppTheme.statusReady;
        break;
      case 'delivered':
      case 'completed':
        color = AppTheme.statusAccepted;
        break;
      case 'cancelled':
        color = AppTheme.statusError;
        break;
      default:
        color = AppTheme.onSurfaceVariant;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color, width: 1),
      ),
      child: Text(status, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }
}

class GlassCard extends StatelessWidget {
  final Widget child;
  final EdgeInsetsGeometry? padding;
  final EdgeInsetsGeometry? margin;
  final double borderRadius;

  const GlassCard({super.key, required this.child, this.padding, this.margin, this.borderRadius = 16});

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: margin,
      padding: padding ?? const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceGlass,
        borderRadius: BorderRadius.circular(borderRadius),
      ),
      child: child,
    );
  }
}

class SectionTitle extends StatelessWidget {
  final String title;

  const SectionTitle({super.key, required this.title});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Text(title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
    );
  }
}

class ActionTile extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final Color? iconColor;

  const ActionTile({super.key, required this.icon, required this.label, required this.onTap, this.iconColor});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: GlassCard(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, color: iconColor ?? AppTheme.primaryOrange, size: 32),
            const SizedBox(height: 8),
            Text(label, style: const TextStyle(color: AppTheme.onSurface, fontSize: 13, fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }
}

class ProfileOptionRow extends StatelessWidget {
  final IconData icon;
  final String title;
  final int? badgeCount;
  final Widget? trailing;
  final VoidCallback onTap;

  const ProfileOptionRow({super.key, required this.icon, required this.title, this.badgeCount, this.trailing, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: Icon(icon, color: AppTheme.primaryOrange),
      title: Text(title, style: const TextStyle(color: AppTheme.onSurface)),
      trailing: trailing ?? (badgeCount != null && badgeCount! > 0
        ? Badge(label: Text('$badgeCount'), child: const Icon(Icons.chevron_right, color: AppTheme.onSurfaceVariant))
        : const Icon(Icons.chevron_right, color: AppTheme.onSurfaceVariant)),
      onTap: onTap,
    );
  }
}

String getFoodImageUrl(String name) {
  return 'https://source.unsplash.com/200x200/?' + name.split(' ').first;
}
