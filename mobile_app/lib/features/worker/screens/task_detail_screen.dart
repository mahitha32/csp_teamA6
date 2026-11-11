import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';

class TaskDetailScreen extends StatefulWidget {
  final Map<String, dynamic> task;
  final String complaintId;

  const TaskDetailScreen({
    super.key,
    required this.task,
    required this.complaintId,
  });

  @override
  State<TaskDetailScreen> createState() => _TaskDetailScreenState();
}

class _TaskDetailScreenState extends State<TaskDetailScreen> {
  File? _image;
  final TextEditingController _notesController = TextEditingController();
  bool _isUpdating = false;
  late String _currentStatus;

  @override
  void initState() {
    super.initState();
    _currentStatus = widget.task['status'] ?? 'Assigned';
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _pickImage(ImageSource source) async {
    try {
      final picker = ImagePicker();
      final pickedFile = await picker.pickImage(source: source, imageQuality: 75);
      if (pickedFile != null) {
        setState(() {
          _image = File(pickedFile.path);
        });
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Could not access camera/gallery: $e')),
      );
    }
  }

  Future<void> _startWork() async {
    setState(() => _isUpdating = true);
    try {
      await apiClient.put(
        '/workers/tasks/${widget.complaintId}/progress',
        data: {
          'status': 'In Progress',
          'notes': 'Work started on site by field worker.',
        },
      );
      setState(() {
        _currentStatus = 'In Progress';
      });
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Task status updated to In Progress!')),
      );
    } on DioException catch (e) {
      final msg = e.response?.data?['message'] ?? e.message ?? 'Update failed';
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
      if (mounted) setState(() => _isUpdating = false);
    }
  }

  Future<void> _submitResolution() async {
    final notes = _notesController.text.trim();
    if (_image == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Mandatory: Please attach a resolution photograph.'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }
    if (notes.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Mandatory: Please provide completion remarks.'),
          backgroundColor: Colors.red,
        ),
      );
      return;
    }

    setState(() => _isUpdating = true);

    try {
      final fileName = _image!.path.split('/').last.split('\\').last;
      final formData = FormData.fromMap({
        'status': 'Resolved',
        'notes': notes,
        'resolution_photo': await MultipartFile.fromFile(
          _image!.path,
          filename: fileName,
        ),
      });

      await apiClient.put(
        '/workers/tasks/${widget.complaintId}/progress',
        data: formData,
      );

      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Task resolved and proof photo uploaded successfully!'),
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
      if (mounted) setState(() => _isUpdating = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final title = widget.task['title'] ?? 'Complaint';
    final description = widget.task['description'] ?? 'No description provided';
    final category = widget.task['category_name'] ?? widget.task['category'] ?? 'General';
    final location = widget.task['location'] ?? 'Vemavaram';
    final wardId = widget.task['ward_id']?.toString() ?? '1';
    final citizenPhoto = widget.task['image_url'] ?? widget.task['complaint_image'];

    return Scaffold(
      appBar: AppBar(
        title: Text(widget.complaintId, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: Colors.orange.shade800,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Status & Category banner
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Chip(
                  label: Text(
                    _currentStatus,
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 12),
                  ),
                  backgroundColor: _currentStatus.toLowerCase() == 'resolved'
                      ? Colors.green
                      : (_currentStatus.toLowerCase() == 'in progress' ? Colors.orange.shade700 : Colors.blue),
                ),
                Text('Ward $wardId • $category', style: TextStyle(color: Colors.grey.shade600, fontSize: 13)),
              ],
            ),
            const SizedBox(height: 12),

            Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),

            Row(
              children: [
                const Icon(Icons.location_on, size: 16, color: Colors.grey),
                const SizedBox(width: 4),
                Expanded(child: Text(location, style: const TextStyle(color: Colors.grey, fontSize: 13))),
              ],
            ),
            const Divider(height: 32),

            const Text('Citizen Problem Description', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey)),
            const SizedBox(height: 6),
            Text(description, style: const TextStyle(fontSize: 15, height: 1.4)),
            const SizedBox(height: 16),

            if (citizenPhoto != null && citizenPhoto.toString().isNotEmpty) ...[
              const Text('Citizen Uploaded Photo', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey)),
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
                    child: const Center(child: Text('Photo not available')),
                  ),
                ),
              ),
              const Divider(height: 32),
            ],

            if (_currentStatus.toLowerCase() == 'assigned') ...[
              ElevatedButton.icon(
                onPressed: _isUpdating ? null : _startWork,
                icon: const Icon(Icons.play_arrow),
                label: _isUpdating
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Mark In Progress (Start On-Site Work)'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.orange.shade700,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
              const SizedBox(height: 24),
            ],

            if (_currentStatus.toLowerCase() != 'resolved') ...[
              const Text(
                'Resolution Proof (Mandatory to Resolve)',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
              ),
              const SizedBox(height: 4),
              const Text(
                'A photo of the completed work and closing remarks are required by policy.',
                style: TextStyle(fontSize: 12, color: Colors.grey),
              ),
              const SizedBox(height: 12),

              InkWell(
                onTap: () {
                  showModalBottomSheet(
                    context: context,
                    builder: (ctx) => SafeArea(
                      child: Wrap(
                        children: [
                          ListTile(
                            leading: const Icon(Icons.camera_alt),
                            title: const Text('Take Photo with Camera'),
                            onTap: () {
                              Navigator.pop(ctx);
                              _pickImage(ImageSource.camera);
                            },
                          ),
                          ListTile(
                            leading: const Icon(Icons.photo_library),
                            title: const Text('Choose from Gallery'),
                            onTap: () {
                              Navigator.pop(ctx);
                              _pickImage(ImageSource.gallery);
                            },
                          ),
                        ],
                      ),
                    ),
                  );
                },
                child: Container(
                  height: 160,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade50,
                    border: Border.all(color: Colors.grey.shade300, width: 1.5),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: _image != null
                      ? ClipRRect(
                          borderRadius: BorderRadius.circular(10),
                          child: Image.file(_image!, fit: BoxFit.cover, width: double.infinity),
                        )
                      : Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.camera_alt, size: 40, color: Colors.orange.shade700),
                            const SizedBox(height: 8),
                            const Text('Take / Upload Resolution Photo *', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                            const SizedBox(height: 4),
                            Text('Tap to select photo', style: TextStyle(color: Colors.grey.shade500, fontSize: 11)),
                          ],
                        ),
                ),
              ),
              const SizedBox(height: 16),

              TextField(
                controller: _notesController,
                decoration: InputDecoration(
                  labelText: 'Resolution Remarks *',
                  hintText: 'Describe how the issue was fixed...',
                  alignLabelWithHint: true,
                  border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                ),
                maxLines: 3,
              ),
              const SizedBox(height: 24),

              ElevatedButton.icon(
                onPressed: _isUpdating ? null : _submitResolution,
                icon: const Icon(Icons.check_circle_outline),
                label: _isUpdating
                    ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                    : const Text('Complete & Mark Resolved'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green.shade700,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
              ),
            ] else ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.green.shade50,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.green.shade200),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.check_circle, color: Colors.green, size: 28),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text('This task has been resolved!', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.green)),
                          if (widget.task['notes'] != null) ...[
                            const SizedBox(height: 4),
                            Text(widget.task['notes'].toString(), style: const TextStyle(fontSize: 13)),
                          ],
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
