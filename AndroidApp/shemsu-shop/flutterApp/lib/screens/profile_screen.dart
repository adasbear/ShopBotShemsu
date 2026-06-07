import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/auth_viewmodel.dart';
import '../viewmodels/notifications_viewmodel.dart';
import '../core/theme.dart';
import 'common_widgets.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _nameCtrl = TextEditingController();
  bool _editing = false;

  @override
  void dispose() {
    _nameCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthViewModel>();
    final notifVM = context.watch<NotificationsViewModel>();

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          const SizedBox(height: 16),
          CircleAvatar(
            radius: 40,
            backgroundColor: AppTheme.primaryContainerOrange,
            child: Text(
              (auth.fullName.isNotEmpty ? auth.fullName[0] : '?').toUpperCase(),
              style: const TextStyle(fontSize: 32, color: Colors.white, fontWeight: FontWeight.bold),
            ),
          ),
          const SizedBox(height: 12),
          if (_editing)
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                SizedBox(
                  width: 200,
                  child: TextField(
                    controller: _nameCtrl,
                    style: const TextStyle(color: AppTheme.onSurface),
                    decoration: const InputDecoration(
                      isDense: true,
                      contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                    ),
                  ),
                ),
                IconButton(
                  icon: const Icon(Icons.check, color: AppTheme.accentGold),
                  onPressed: () {
                    if (_nameCtrl.text.trim().isNotEmpty) {
                      auth.updateName(_nameCtrl.text.trim());
                    }
                    setState(() => _editing = false);
                  },
                ),
              ],
            )
          else
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(auth.fullName, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.onSurface, fontFamily: 'serif')),
                IconButton(
                  icon: const Icon(Icons.edit, color: AppTheme.onSurfaceVariant, size: 18),
                  onPressed: () {
                    _nameCtrl.text = auth.fullName;
                    setState(() => _editing = true);
                  },
                ),
              ],
            ),
          Text('@${auth.username}', style: const TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 14)),
          const SizedBox(height: 4),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: AppTheme.accentGold.withOpacity(0.2),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.workspace_premium, color: AppTheme.accentGold, size: 16),
                SizedBox(width: 4),
                Text('Gold Patron', style: TextStyle(color: AppTheme.accentGold, fontSize: 12, fontWeight: FontWeight.bold)),
              ],
            ),
          ),
          const SizedBox(height: 32),
          const Divider(color: AppTheme.surfaceContainerLow),
          ProfileOptionRow(icon: Icons.notifications_outlined, title: 'Notifications', badgeCount: notifVM.unreadCount, onTap: () => Navigator.pushNamed(context, '/notifications')),
          ProfileOptionRow(icon: Icons.headset_mic_outlined, title: 'Contact Admin', onTap: () => Navigator.pushNamed(context, '/contact_admin')),
          ProfileOptionRow(icon: Icons.help_outline, title: 'Help', onTap: () => Navigator.pushNamed(context, '/help')),
          ProfileOptionRow(icon: Icons.star_outline, title: 'Feedback', onTap: () => Navigator.pushNamed(context, '/feedback')),
          ProfileOptionRow(icon: Icons.credit_card_outlined, title: 'My Debt', onTap: () => Navigator.pushNamed(context, '/debt')),
          const Divider(color: AppTheme.surfaceContainerLow),
          ProfileOptionRow(
            icon: Icons.logout,
            title: 'Logout',
            trailing: const Icon(Icons.logout, color: AppTheme.statusError),
            onTap: () {
              auth.logout();
              Navigator.pushNamedAndRemoveUntil(context, '/login', (route) => false);
            },
          ),
        ],
      ),
    );
  }
}
