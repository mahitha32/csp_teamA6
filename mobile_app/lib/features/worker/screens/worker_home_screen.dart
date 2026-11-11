import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../../auth/screens/login_screen.dart';
import 'task_detail_screen.dart';

class WorkerHomeScreen extends StatefulWidget {
  const WorkerHomeScreen({super.key});

  @override
  State<WorkerHomeScreen> createState() => _WorkerHomeScreenState();
}

class _WorkerHomeScreenState extends State<WorkerHomeScreen> {
  List<dynamic> _tasks = [];
  bool _isLoading = true;
  String? _error;
  String _workerName = '';

  @override
  void initState() {
    super.initState();
    _loadWorkerInfo();
    _fetchTasks();
  }

  Future<void> _loadWorkerInfo() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _workerName = prefs.getString('user_name') ?? 'Field Worker';
    });
  }

  Future<void> _fetchTasks() async {
    setState(() {
      _isLoading = true;
      _error = null;
    });

    try {
      final response = await apiClient.get('/workers/tasks');
      final data = response.data['data'];
      setState(() {
        _tasks = data['tasks'] ?? [];
      });
    } on DioException catch (e) {
      setState(() {
        _error = e.response?.data?['message'] ?? e.message ?? 'Failed to load assigned tasks';
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  Future<void> _logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.clear();
    if (!mounted) return;
    Navigator.pushAndRemoveUntil(
      context,
      MaterialPageRoute(builder: (_) => const LoginScreen()),
      (route) => false,
    );
  }

  Color _getStatusColor(String status) {
    switch (status.toLowerCase()) {
      case 'resolved':
        return Colors.green;
      case 'in progress':
        return Colors.orange;
      case 'assigned':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Field Worker Portal',
              style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold),
            ),
            if (_workerName.isNotEmpty)
              Text(
                'Assigned to $_workerName',
                style: const TextStyle(color: Colors.white70, fontSize: 12),
              ),
          ],
        ),
        backgroundColor: Colors.orange.shade800,
        iconTheme: const IconThemeData(color: Colors.white),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            tooltip: 'Refresh Tasks',
            onPressed: _fetchTasks,
          ),
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.white),
            tooltip: 'Sign Out',
            onPressed: _logout,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _fetchTasks,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? Center(
                    child: Padding(
                      padding: const EdgeInsets.all(24.0),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          const Icon(Icons.error_outline, size: 48, color: Colors.red),
                          const SizedBox(height: 12),
                          Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: Colors.red)),
                          const SizedBox(height: 16),
                          ElevatedButton.icon(
                            onPressed: _fetchTasks,
                            icon: const Icon(Icons.refresh),
                            label: const Text('Try Again'),
                          ),
                        ],
                      ),
                    ),
                  )
                : _tasks.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.assignment_turned_in, size: 64, color: Colors.grey.shade400),
                            const SizedBox(height: 16),
                            const Text(
                              'No tasks currently assigned',
                              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                            ),
                            const SizedBox(height: 8),
                            const Text(
                              'Assigned field complaints will appear here.',
                              style: TextStyle(color: Colors.grey),
                            ),
                          ],
                        ),
                      )
                    : ListView.separated(
                        padding: const EdgeInsets.all(16),
                        itemCount: _tasks.length,
                        separatorBuilder: (_, __) => const SizedBox(height: 12),
                        itemBuilder: (context, index) {
                          final task = _tasks[index] as Map<String, dynamic>;
                          final complaintId = task['complaint_id'] ?? 'CMP';
                          final title = task['title'] ?? 'Complaint';
                          final status = task['status'] ?? 'Assigned';
                          final category = task['category_name'] ?? task['category'] ?? 'General';
                          final location = task['location'] ?? 'Vemavaram';

                          return Card(
                            elevation: 2,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                            child: ListTile(
                              contentPadding: const EdgeInsets.all(16),
                              leading: Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: Colors.orange.shade50,
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Icon(Icons.build_circle, color: Colors.orange.shade700, size: 28),
                              ),
                              title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  const SizedBox(height: 4),
                                  Text('$complaintId • $category', style: TextStyle(color: Colors.grey.shade700, fontSize: 13)),
                                  const SizedBox(height: 2),
                                  Row(
                                    children: [
                                      const Icon(Icons.location_on, size: 13, color: Colors.grey),
                                      const SizedBox(width: 3),
                                      Expanded(
                                        child: Text(
                                          location,
                                          style: const TextStyle(fontSize: 12, color: Colors.grey),
                                          maxLines: 1,
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Chip(
                                    label: Text(
                                      status,
                                      style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: _getStatusColor(status)),
                                    ),
                                    backgroundColor: _getStatusColor(status).withOpacity(0.1),
                                    padding: EdgeInsets.zero,
                                    materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                                  ),
                                ],
                              ),
                              trailing: const Icon(Icons.chevron_right, color: Colors.grey),
                              onTap: () async {
                                final updated = await Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (_) => TaskDetailScreen(
                                      task: task,
                                      complaintId: complaintId,
                                    ),
                                  ),
                                );
                                if (updated == true) {
                                  _fetchTasks();
                                }
                              },
                            ),
                          );
                        },
                      ),
      ),
    );
  }
}
