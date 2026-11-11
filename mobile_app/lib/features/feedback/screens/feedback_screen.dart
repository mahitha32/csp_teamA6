import 'package:flutter/material.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';

class FeedbackScreen extends StatefulWidget {
  final String complaintId;
  const FeedbackScreen({super.key, required this.complaintId});

  @override
  State<FeedbackScreen> createState() => _FeedbackScreenState();
}

class _FeedbackScreenState extends State<FeedbackScreen> {
  int _rating = 5;
  final TextEditingController _remarksController = TextEditingController();
  bool _isSubmitting = false;

  @override
  void dispose() {
    _remarksController.dispose();
    super.dispose();
  }

  Future<void> _submitFeedback() async {
    setState(() => _isSubmitting = true);
    try {
      await apiClient.post('/feedback', data: {
        'complaint_id': widget.complaintId,
        'rating': _rating,
        'remarks': _remarksController.text.trim(),
      });

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Thank you! Your feedback has been submitted to the Vemavaram Panchayat.'),
          backgroundColor: Colors.green,
        ),
      );
      Navigator.pop(context, true);
    } on DioException catch (e) {
      final msg = e.response?.data?['message'] ?? e.message ?? 'Submission failed';
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $msg'), backgroundColor: Colors.red),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e'), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Provide Feedback', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.primary,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const SizedBox(height: 12),
            Text('Rate the Resolution', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            Text(
              'How satisfied are you with the resolution of issue ${widget.complaintId} in Vemavaram?',
              style: TextStyle(color: Colors.grey.shade700, fontSize: 14),
            ),
            const SizedBox(height: 32),

            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: List.generate(5, (index) {
                return IconButton(
                  icon: Icon(
                    index < _rating ? Icons.star : Icons.star_border,
                    color: Colors.amber,
                    size: 42,
                  ),
                  onPressed: () {
                    setState(() {
                      _rating = index + 1;
                    });
                  },
                );
              }),
            ),
            Center(
              child: Text(
                _rating == 5
                    ? 'Excellent (5/5)'
                    : (_rating == 4
                        ? 'Good (4/5)'
                        : (_rating == 3
                            ? 'Average (3/5)'
                            : (_rating == 2 ? 'Below Average (2/5)' : 'Poor (1/5)'))),
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15, color: Colors.grey),
              ),
            ),
            const SizedBox(height: 32),

            TextField(
              controller: _remarksController,
              decoration: InputDecoration(
                labelText: 'Additional Remarks / Suggestions',
                hintText: 'Share any thoughts on the work done by the panchayat...',
                alignLabelWithHint: true,
                border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
              ),
              maxLines: 4,
            ),
            const SizedBox(height: 32),

            ElevatedButton(
              onPressed: _isSubmitting ? null : _submitFeedback,
              style: ElevatedButton.styleFrom(
                backgroundColor: Theme.of(context).colorScheme.primary,
                padding: const EdgeInsets.symmetric(vertical: 14),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              child: _isSubmitting
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                  : const Text('Submit Feedback', style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white)),
            ),
          ],
        ),
      ),
    );
  }
}
