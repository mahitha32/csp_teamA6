import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../../feedback/screens/feedback_screen.dart';

class ComplaintDetailScreen extends StatefulWidget {
  final String complaintId;
  final Map<String, dynamic>? complaintData;

  const ComplaintDetailScreen({
    super.key,
    required this.complaintId,
    this.complaintData,
  });

  @override
  State<ComplaintDetailScreen> createState() => _ComplaintDetailScreenState();
}

class _ComplaintDetailScreenState extends State<ComplaintDetailScreen> {
  Map<String, dynamic>? _data;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _data = widget.complaintData;
    _fetchDetails();
  }

  Future<void> _fetchDetails() async {
    try {
      final response = await apiClient.get('/complaints/${widget.complaintId}');
      final details = response.data['data']?['complaint'];
      if (details != null) {
        setState(() {
          _data = details;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (_data == null) {
        setState(() {
          _error = 'Could not load complaint details.';
          _isLoading = false;
        });
      } else {
        setState(() => _isLoading = false);
      }
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
    if (_isLoading && _data == null) {
      return Scaffold(
        appBar: AppBar(title: Text(widget.complaintId, style: const TextStyle(color: Colors.white))),
        body: const Center(child: CircularProgressIndicator()),
      );
    }

    if (_error != null && _data == null) {
      return Scaffold(
        appBar: AppBar(title: Text(widget.complaintId, style: const TextStyle(color: Colors.white))),
        body: Center(child: Text(_error!, style: const TextStyle(color: Colors.red))),
      );
    }

    final d = _data!;
    final title = d['title'] ?? 'Complaint';
    final status = d['status'] ?? 'Submitted';
    final category = d['category'] ?? 'General';
    final description = d['description'] ?? '';
    final location = d['location'] ?? 'Vemavaram';
    final wardId = d['ward_id']?.toString() ?? '1';
    final citizenPhoto = d['image_url'];
    final resolutionPhoto = d['resolution_image_url'];
    final resolutionNotes = d['resolution_notes'];
    final assignment = d['assignment'];
    final history = (d['status_history'] as List<dynamic>?) ?? [];
    final isResolved = status.toLowerCase() == 'resolved';

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.complaintId, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.primary,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(widget.complaintId, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
                Chip(
                  label: Text(status, style: TextStyle(color: _getStatusColor(status), fontWeight: FontWeight.bold, fontSize: 12)),
                  backgroundColor: _getStatusColor(status).withOpacity(0.1),
                ),
              ],
            ),
            const SizedBox(height: 16),

            Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            const SizedBox(height: 6),
            Row(
              children: [
                const Icon(Icons.location_on, size: 14, color: Colors.grey),
                const SizedBox(width: 4),
                Expanded(child: Text('$location (Ward $wardId)', style: const TextStyle(color: Colors.grey, fontSize: 13))),
              ],
            ),
            const Divider(height: 32),

            const Text('Category', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey, fontSize: 13)),
            const SizedBox(height: 4),
            Text(category, style: const TextStyle(fontSize: 15)),
            const Divider(height: 32),

            const Text('Description', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey, fontSize: 13)),
            const SizedBox(height: 4),
            Text(description, style: const TextStyle(fontSize: 15, height: 1.4)),
            const SizedBox(height: 16),

            if (citizenPhoto != null && citizenPhoto.toString().isNotEmpty) ...[
              const Text('Photo Evidence', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey, fontSize: 13)),
              const SizedBox(height: 8),
              ClipRRect(
                borderRadius: BorderRadius.circular(12),
                child: Image.network(
                  citizenPhoto.toString(),
                  height: 180,
                  width: double.infinity,
                  fit: BoxFit.cover,
                  errorBuilder: (_, __, ___) => Container(
                    height: 120,
                    color: Colors.grey.shade200,
                    child: const Center(child: Text('Photo evidence unavailable')),
                  ),
                ),
              ),
              const Divider(height: 32),
            ],

            if (assignment != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.blue.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.blue.shade200),
                ),
                child: Row(
                  children: [
                    CircleAvatar(
                      backgroundColor: Colors.blue.shade700,
                      child: const Icon(Icons.person, color: Colors.white),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text('Assigned Worker: ${assignment['worker_name'] ?? 'Staff'}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                          Text('Dept: ${assignment['department'] ?? 'General Maintenance'}', style: TextStyle(color: Colors.grey.shade700, fontSize: 12)),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
              const Divider(height: 32),
            ],

            if (isResolved) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.check_circle, color: Colors.green, size: 24),
                        SizedBox(width: 8),
                        Text('Issue Resolved', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.green, fontSize: 16)),
                      ],
                    ),
                    if (resolutionNotes != null && resolutionNotes.toString().isNotEmpty) ...[
                      const SizedBox(height: 8),
                      Text('Remarks: $resolutionNotes', style: const TextStyle(fontSize: 14)),
                    ],
                    if (resolutionPhoto != null && resolutionPhoto.toString().isNotEmpty) ...[
                      const SizedBox(height: 12),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(8),
                        child: Image.network(
                          resolutionPhoto.toString(),
                          height: 160,
                          width: double.infinity,
                          fit: BoxFit.cover,
                          errorBuilder: (_, __, ___) => const SizedBox(),
                        ),
                      ),
                    ],
                    const SizedBox(height: 16),
                    ElevatedButton.icon(
                      onPressed: () {
                        Navigator.push(
                          context,
                          MaterialPageRoute(builder: (_) => FeedbackScreen(complaintId: widget.complaintId)),
                        );
                      },
                      icon: const Icon(Icons.star, size: 18),
                      label: const Text('Rate This Resolution'),
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.amber.shade700,
                        foregroundColor: Colors.white,
                      ),
                    ),
                  ],
                ),
              ),
              const Divider(height: 32),
            ],

            const Text('Status Timeline', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey, fontSize: 13)),
            const SizedBox(height: 16),
            if (history.isNotEmpty)
              ...history.map((h) => _buildTimelineItem(
                    context,
                    h['new_status'] ?? 'Updated',
                    (h['changed_at'] ?? '').toString().replaceFirst('T', ' '),
                    isDone: true,
                  ))
            else ...[
              _buildTimelineItem(context, 'Submitted', 'Recorded in database', isDone: true),
              if (status != 'Submitted')
                _buildTimelineItem(context, status, 'Current active status', isDone: true, isLast: true),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildTimelineItem(BuildContext context, String title, String subtitle, {bool isDone = false, bool isLast = false}) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            Container(
              width: 14,
              height: 14,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: isDone ? Theme.of(context).colorScheme.primary : Colors.grey.shade300,
              ),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 36,
                color: isDone ? Theme.of(context).colorScheme.primary : Colors.grey.shade300,
              ),
          ],
        ),
        const SizedBox(width: 14),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: TextStyle(fontWeight: FontWeight.bold, color: isDone ? Colors.black : Colors.grey, fontSize: 13)),
              const SizedBox(height: 2),
              Text(subtitle, style: TextStyle(fontSize: 11, color: Colors.grey.shade600)),
              const SizedBox(height: 14),
            ],
          ),
        ),
      ],
    );
  }
}
