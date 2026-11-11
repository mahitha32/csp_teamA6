import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import 'create_complaint_screen.dart';
import 'complaint_history_screen.dart';
import 'complaint_detail_screen.dart';
import '../../notifications/screens/notifications_screen.dart';
import '../../profile/screens/profile_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  String _citizenName = 'Villager';
  List<dynamic> _recentComplaints = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadUser();
    _fetchRecentComplaints();
  }

  Future<void> _loadUser() async {
    final prefs = await SharedPreferences.getInstance();
    final name = prefs.getString('user_name');
    if (name != null && name.isNotEmpty) {
      setState(() => _citizenName = name);
    }
  }

  Future<void> _fetchRecentComplaints() async {
    setState(() => _isLoading = true);
    try {
      final response = await apiClient.get('/complaints');
      final data = response.data['data'];
      setState(() {
        _recentComplaints = data['complaints'] ?? [];
      });
    } catch (_) {
      // Graceful fallback if network fails
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'resolved':
        return Colors.green;
      case 'in progress':
        return Colors.orange;
      case 'assigned':
        return Colors.blue;
      case 'under review':
        return Colors.purple;
      default:
        return Colors.grey.shade700;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Vemavaram Village', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.primary,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined, color: Colors.white),
            tooltip: 'Notifications',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const NotificationsScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.person_outline, color: Colors.white),
            tooltip: 'Profile',
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const ProfileScreen()),
              );
            },
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _fetchRecentComplaints,
        child: SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Hello, $_citizenName!', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
              const SizedBox(height: 6),
              Text('Welcome to Vemavaram Citizen Redressal Portal.', style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey.shade600)),
              const SizedBox(height: 28),

              // Quick Actions
              Row(
                children: [
                  Expanded(
                    child: _buildActionCard(
                      context,
                      title: 'New Complaint',
                      icon: Icons.add_circle_outline,
                      color: Theme.of(context).colorScheme.primary,
                      onTap: () async {
                        final res = await Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const CreateComplaintScreen()),
                        );
                        if (res == true) {
                          _fetchRecentComplaints();
                        }
                      },
                    ),
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: _buildActionCard(
                      context,
                      title: 'Track Status',
                      icon: Icons.history,
                      color: Theme.of(context).colorScheme.secondary,
                      onTap: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const ComplaintHistoryScreen()),
                        );
                      },
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 32),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Recent Complaints', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontSize: 18, fontWeight: FontWeight.bold)),
                  if (_recentComplaints.isNotEmpty)
                    TextButton(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => const ComplaintHistoryScreen()),
                        );
                      },
                      child: const Text('View All'),
                    ),
                ],
              ),
              const SizedBox(height: 12),

              if (_isLoading)
                const Center(
                  child: Padding(
                    padding: EdgeInsets.all(32.0),
                    child: CircularProgressIndicator(),
                  ),
                )
              else if (_recentComplaints.isEmpty)
                Card(
                  elevation: 1,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                  child: Padding(
                    padding: const EdgeInsets.all(28.0),
                    child: Center(
                      child: Column(
                        children: [
                          Icon(Icons.inbox_outlined, size: 48, color: Theme.of(context).colorScheme.primary.withOpacity(0.5)),
                          const SizedBox(height: 12),
                          const Text('No recent complaints found.', style: TextStyle(fontWeight: FontWeight.bold)),
                          const SizedBox(height: 4),
                          const Text('Report issues in Vemavaram to see them tracked here.', style: TextStyle(color: Colors.grey, fontSize: 13)),
                        ],
                      ),
                    ),
                  ),
                )
              else
                ListView.separated(
                  shrinkWrap: true,
                  physics: const NeverScrollableScrollPhysics(),
                  itemCount: _recentComplaints.take(4).length,
                  separatorBuilder: (_, __) => const SizedBox(height: 10),
                  itemBuilder: (context, index) {
                    final item = _recentComplaints[index] as Map<String, dynamic>;
                    final complaintId = item['complaint_id'] ?? 'CMP';
                    final title = item['title'] ?? 'Complaint';
                    final status = item['status'] ?? 'Submitted';
                    final category = item['category'] ?? 'General';

                    return Card(
                      elevation: 1,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                      child: ListTile(
                        leading: CircleAvatar(
                          backgroundColor: Theme.of(context).colorScheme.primary.withOpacity(0.1),
                          child: Icon(Icons.report_problem, color: Theme.of(context).colorScheme.primary, size: 20),
                        ),
                        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                        subtitle: Text('$complaintId • $category', style: const TextStyle(fontSize: 12, color: Colors.grey)),
                        trailing: Chip(
                          label: Text(
                            status,
                            style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: _getStatusColor(status)),
                          ),
                          backgroundColor: _getStatusColor(status).withOpacity(0.1),
                          padding: EdgeInsets.zero,
                          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (_) => ComplaintDetailScreen(
                                complaintId: complaintId,
                                complaintData: item,
                              ),
                            ),
                          );
                        },
                      ),
                    );
                  },
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildActionCard(BuildContext context, {required String title, required IconData icon, required Color color, required VoidCallback onTap}) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
        decoration: BoxDecoration(
          color: color.withOpacity(0.08),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: color.withOpacity(0.25)),
        ),
        child: Column(
          children: [
            Icon(icon, size: 36, color: color),
            const SizedBox(height: 10),
            Text(title, style: TextStyle(fontWeight: FontWeight.bold, color: color, fontSize: 13)),
          ],
        ),
      ),
    );
  }
}
