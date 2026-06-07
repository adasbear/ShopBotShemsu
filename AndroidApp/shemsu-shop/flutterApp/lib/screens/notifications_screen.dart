import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/notifications_viewmodel.dart';
import '../viewmodels/auth_viewmodel.dart';
import '../core/theme.dart';
import 'common_widgets.dart';

class NotificationsScreen extends StatelessWidget {
  const NotificationsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final notifVM = context.watch<NotificationsViewModel>();

    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      appBar: AppBar(title: const Text('Notifications')),
      body: notifVM.isLoading
        ? const Center(child: CircularProgressIndicator(color: AppTheme.accentGold))
        : notifVM.notifications.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.notifications_off, color: AppTheme.onSurfaceVariant.withOpacity(0.3), size: 64),
                  const SizedBox(height: 16),
                  const Text('No notifications', style: TextStyle(color: AppTheme.onSurfaceVariant)),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: notifVM.notifications.length,
              itemBuilder: (context, index) {
                final notif = notifVM.notifications[index];
                return InkWell(
                  onTap: () {
                    if (!notif.read) {
                      notifVM.markRead(notif.id);
                    }
                  },
                  child: GlassCard(
                    margin: const EdgeInsets.only(bottom: 8),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        if (!notif.read)
                          Container(
                            width: 8, height: 8, margin: const EdgeInsets.only(top: 6),
                            decoration: const BoxDecoration(shape: BoxShape.circle, color: AppTheme.primaryOrange),
                          ),
                        const SizedBox(width: 8),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(notif.title, style: TextStyle(
                                color: AppTheme.onSurface,
                                fontWeight: notif.read ? FontWeight.normal : FontWeight.bold,
                                fontSize: 15,
                              )),
                              const SizedBox(height: 4),
                              Text(notif.body, style: const TextStyle(color: AppTheme.onSurfaceVariant, fontSize: 13)),
                              if (notif.createdAt != null) ...[
                                const SizedBox(height: 4),
                                Text(notif.createdAt!, style: TextStyle(color: AppTheme.onSurfaceVariant.withOpacity(0.5), fontSize: 11)),
                              ],
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
    );
  }
}
