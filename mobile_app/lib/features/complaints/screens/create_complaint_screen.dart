import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';

class CreateComplaintScreen extends StatefulWidget {
  const CreateComplaintScreen({super.key});

  @override
  State<CreateComplaintScreen> createState() => _CreateComplaintScreenState();
}

class _CreateComplaintScreenState extends State<CreateComplaintScreen> {
  final _formKey = GlobalKey<FormState>();
  String? _selectedCategory;
  final TextEditingController _titleController = TextEditingController();
  final TextEditingController _descController = TextEditingController();
  final TextEditingController _locationController = TextEditingController();
  File? _image;
  bool _isLoading = false;
  bool _isVoiceMode = false;
  double? _lat;
  double? _lng;

  final List<String> _categories = [
    'Road Issues',
    'Streetlight Issues',
    'Water Supply Problems',
    'Drainage Problems',
    'Garbage Collection Issues',
    'Sanitation Issues',
  ];

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery, imageQuality: 70);
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
      });
    }
  }

  Future<void> _submitComplaint() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedCategory == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please select a category')));
      return;
    }
    if (_image == null) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please attach a photo of the issue')));
      return;
    }

    setState(() => _isLoading = true);

    try {
      // Approximate Vemavaram coordinates
      _lat = 16.4866 + (DateTime.now().millisecond % 100) * 0.0001;
      _lng = 80.6433 + (DateTime.now().millisecond % 100) * 0.0001;

      final locationText = _locationController.text.trim();
      final Map<String, dynamic> map = {
        'title': _titleController.text.trim(),
        'description': _descController.text.trim(),
        'category': _selectedCategory,
        'location': locationText.isNotEmpty ? locationText : 'Vemavaram Village',
        'latitude': _lat,
        'longitude': _lng,
        'ward_id': 1,
      };

      if (_image != null) {
        final fileName = _image!.path.split('/').last.split('\\').last;
        map['image'] = await MultipartFile.fromFile(_image!.path, filename: fileName);
      }

      final formData = FormData.fromMap(map);
      final response = await apiClient.post('/complaints', data: formData);
      final newComplaintId = response.data['data']?['complaint_id'] ?? '';

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Complaint submitted successfully! ID: $newComplaintId'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true);
      }
    } on DioException catch (e) {
      final msg = e.response?.data?['message'] ?? e.message ?? 'Submission failed';
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: $msg'), backgroundColor: Colors.red),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Error: $e')));
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _titleController.dispose();
    _descController.dispose();
    _locationController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('New Complaint', style: TextStyle(color: Colors.white)),
        backgroundColor: Theme.of(context).colorScheme.primary,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Text('Report an Issue', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 8),
              
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Provide details about the problem in Vemavaram village.'),
                  IconButton(
                    icon: Icon(_isVoiceMode ? Icons.mic : Icons.mic_none, color: Theme.of(context).colorScheme.primary),
                    tooltip: 'Voice Assistant (Telugu/English)',
                    onPressed: () {
                      setState(() => _isVoiceMode = !_isVoiceMode);
                      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Voice Assistant activated (Stub)')));
                    },
                  )
                ],
              ),
              const SizedBox(height: 16),
              
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(labelText: 'Category'),
                value: _selectedCategory,
                items: _categories.map((c) => DropdownMenuItem(value: c, child: Text(c))).toList(),
                onChanged: (val) => setState(() => _selectedCategory = val),
              ),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(labelText: 'Short Title'),
                validator: (val) => val == null || val.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _descController,
                decoration: const InputDecoration(labelText: 'Detailed Description', alignLabelWithHint: true),
                maxLines: 4,
                validator: (val) => val == null || val.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              
              TextFormField(
                controller: _locationController,
                decoration: const InputDecoration(labelText: 'Specific Location/Landmark', prefixIcon: Icon(Icons.location_on)),
                validator: (val) => val == null || val.isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 24),
              
              // Image Picker
              InkWell(
                onTap: _pickImage,
                child: Container(
                  height: 150,
                  decoration: BoxDecoration(
                    color: Colors.white,
                    border: Border.all(color: Colors.grey.shade300, width: 2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: _image != null
                      ? ClipRRect(borderRadius: BorderRadius.circular(10), child: Image.file(_image!, fit: BoxFit.cover, width: double.infinity))
                      : Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.camera_alt, size: 40, color: Theme.of(context).colorScheme.primary),
                            const SizedBox(height: 8),
                            const Text('Tap to upload a photo', style: TextStyle(fontWeight: FontWeight.bold)),
                          ],
                        ),
                ),
              ),
              
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: _isLoading ? null : _submitComplaint,
                child: _isLoading 
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Text('Submit Complaint'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
