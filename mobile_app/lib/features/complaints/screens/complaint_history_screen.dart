import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import 'complaint_detail_screen.dart';
import '../../feedback/screens/feedback_screen.dart';

class ComplaintHistoryScreen extends StatefulWidget {
  const ComplaintHistoryScreen({super.key});

  @override
  State<ComplaintHistoryScreen> createState() => _ComplaintHistoryScreenState();
}

class _ComplaintHistoryScreenState extends State<ComplaintHistoryScreen> {
  List<dynamic> _complaints = [];
  bool _isLoading = true;
  String _filter = 'All';

  @override
  void initState() {
    super.initState();
    _fetchComplaints();
  }

  Future<void> _fetchComplaints() async {
    setState(() => _isLoading = true);
    try {
      final response = await apiClient.get('/complaints');
      final data = response.data['data'];
      setState(() {
        _complaints = data['complaints'] ?? [];
      });
    } catch (_) {
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
    final filtered = _filter == 'All'
        ? _complaints
        : _complaints.where((c) {
            final st = (c['status'] ?? '').toString().toLowerCase();
            if (_filter == 'Pending') return st == 'submitted' || st == 'under review';
            if (_filter == 'In Progress') return st == 'in progress' || st == 'assigned';
            if (_filter == 'Resolved') return st == 'resolved';
            return true;
          }).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('My Complaints', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.primary,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: Column(
        children: [
          // Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            child: Row(
              children: ['All', 'Pending', 'In Progress', 'Resolved'].map((label) {
                final isSelected = _filter == label;
                return Padding(
                  padding: const EdgeInsets.only(right: 8.0),
                  child: FilterChip(
                    label: Text(label),
                    selected: isSelected,
                    selectedColor: Theme.of(context).colorScheme.primary.withOpacity(0.2),
                    checkmarkColor: Theme.of(context).colorScheme.primary,
                    labelStyle: TextStyle(
                      color: isSelected ? Theme.of(context).colorScheme.primary : Colors.grey.shade800,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                    ),
                    onSelected: (_) => setState(() => _filter = label),
                  ),
                );
              }).toList(),
            ),
          ),
          const Divider(height: 1),

          Expanded(
            child: RefreshIndicator(
              onRefresh: _fetchComplaints,
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : filtered.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(Icons.folder_open, size: 56, color: Colors.grey.shade400),
                              const SizedBox(height: 12),
                              Text('No ${_filter == "All" ? "" : _filter} complaints found', style: const TextStyle(fontWeight: FontWeight.bold)),
                            ],
                          ),
                        )
                      : ListView.separated(
                          padding: const EdgeInsets.all(16),
                          itemCount: filtered.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 12),
                          itemBuilder: (context, index) {
                            final item = filtered[index] as Map<String, dynamic>;
                            final complaintId = item['complaint_id'] ?? 'CMP';
                            final title = item['title'] ?? 'Complaint';
                            final status = item['status'] ?? 'Submitted';
                            final category = item['category'] ?? 'General';
                            final date = (item['created_at'] ?? '').toString().split('T').first;
                            final isResolved = status.toLowerCase() == 'resolved';

                            return Card(
                              elevation: 2,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                              child: Padding(
                                padding: const EdgeInsets.all(16),
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                      children: [
                                        Text(complaintId, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: Colors.grey)),
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
                                    const SizedBox(height: 6),
                                    Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                                    const SizedBox(height: 4),
                                    Text('$category • $date', style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
                                    const SizedBox(height: 12),
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.end,
                                      children: [
                                        if (isResolved)
                                          TextButton.icon(
                                            icon: const Icon(Icons.star, size: 16, color: Colors.amber),
                                            label: const Text('Give Feedback', style: TextStyle(color: Colors.amber, fontSize: 12, fontWeight: FontWeight.bold)),
                                            onPressed: () {
                                              Navigator.push(
                                                context,
                                                MaterialPageRoute(builder: (_) => FeedbackScreen(complaintId: complaintId)),
                                              );
                                            },
                                          ),
                                        TextButton(
                                          child: const Text('View Details →', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                                          onPressed: () {
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
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            );
                          },
                        ),
            ),
          ),
        ],
      ),
    );
  }
}
