import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List<dynamic> _notifications = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _fetchNotifications();
  }

  Future<void> _fetchNotifications() async {
    setState(() => _isLoading = true);
    try {
      final response = await apiClient.get('/notifications');
      final data = response.data['data'];
      setState(() {
        _notifications = data['notifications'] ?? [];
      });
    } catch (_) {
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _markAsRead(int notifId) async {
    try {
      await apiClient.put('/notifications/$notifId/read');
      setState(() {
        final idx = _notifications.indexWhere((n) => n['notification_id'] == notifId);
        if (idx != -1) {
          _notifications[idx]['is_read'] = 1;
        }
      });
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.primary,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: RefreshIndicator(
        onRefresh: _fetchNotifications,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _notifications.isEmpty
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.notifications_none, size: 56, color: Colors.grey.shade400),
                        const SizedBox(height: 12),
                        const Text('No notifications yet', style: TextStyle(fontWeight: FontWeight.bold)),
                        const SizedBox(height: 4),
                        const Text('Updates on your submitted complaints will appear here.', style: TextStyle(color: Colors.grey, fontSize: 13)),
                      ],
                    ),
                  )
                : ListView.separated(
                    padding: const EdgeInsets.all(16),
                    itemCount: _notifications.length,
                    separatorBuilder: (_, __) => const Divider(),
                    itemBuilder: (context, index) {
                      final item = _notifications[index] as Map<String, dynamic>;
                      final notifId = item['notification_id'] is int ? item['notification_id'] : int.tryParse(item['notification_id'].toString()) ?? 0;
                      final title = item['title'] ?? 'Complaint Update';
                      final message = item['message'] ?? '';
                      final isRead = item['is_read'] == 1 || item['is_read'] == true;
                      final date = (item['created_at'] ?? '').toString().replaceFirst('T', ' ').split('.').first;

                      return ListTile(
                        leading: CircleAvatar(
                          backgroundColor: isRead ? Colors.grey.shade100 : const Color(0xFFE0F2FE),
                          child: Icon(
                            Icons.notifications,
                            color: isRead ? Colors.grey : const Color(0xFF0284C7),
                            size: 20,
                          ),
                        ),
                        title: Text(
                          title,
                          style: TextStyle(
                            fontWeight: isRead ? FontWeight.normal : FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                        subtitle: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const SizedBox(height: 2),
                            Text(message, style: const TextStyle(fontSize: 13)),
                            const SizedBox(height: 4),
                            Text(date, style: const TextStyle(fontSize: 11, color: Colors.grey)),
                          ],
                        ),
                        onTap: () {
                          if (!isRead && notifId > 0) {
                            _markAsRead(notifId);
                          }
                        },
                      );
                    },
                  ),
      ),
    );
  }
}
