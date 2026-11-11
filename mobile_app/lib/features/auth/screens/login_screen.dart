import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:dio/dio.dart';
import '../../../../core/network/api_client.dart';
import '../../complaints/screens/home_screen.dart';
import '../../worker/screens/worker_home_screen.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final TextEditingController _phoneController = TextEditingController();
  final TextEditingController _passwordController = TextEditingController();
  final TextEditingController _nameController = TextEditingController();

  bool _isLoading = false;
  bool _isWorker = false;
  bool _isRegister = false;
  bool _obscurePassword = true;

  @override
  void dispose() {
    _phoneController.dispose();
    _passwordController.dispose();
    _nameController.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final phone = _phoneController.text.trim();
    final password = _passwordController.text;
    final name = _nameController.text.trim();

    if (phone.length != 10) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter a valid 10-digit mobile number')),
      );
      return;
    }
    if (password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter your password')),
      );
      return;
    }
    if (_isRegister && name.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter your full name')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      Response response;
      if (_isRegister) {
        response = await apiClient.post('/auth/register', data: {
          'name': name,
          'mobile': phone,
          'password': password,
          'village': 'Vemavaram',
        });
      } else if (_isWorker) {
        response = await apiClient.post('/auth/worker-login', data: {
          'mobile': phone,
          'password': password,
        });
      } else {
        response = await apiClient.post('/auth/login', data: {
          'mobile': phone,
          'password': password,
        });
      }

      final data = response.data['data'];
      final token = data['access_token'];
      final user = data['user'];
      final role = user['role'] ?? (_isWorker ? 'worker' : 'citizen');

      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('access_token', token);
      await prefs.setString('user_role', role);
      await prefs.setString('user_name', user['name'] ?? '');
      await prefs.setString('user_mobile', user['mobile'] ?? phone);

      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Welcome, ${user['name']}!')),
      );

      if (role == 'worker') {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const WorkerHomeScreen()),
        );
      } else {
        Navigator.pushReplacement(
          context,
          MaterialPageRoute(builder: (_) => const HomeScreen()),
        );
      }
    } on DioException catch (e) {
      final msg = e.response?.data?['message'] ?? e.message ?? 'Authentication failed';
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $msg'), backgroundColor: Colors.red),
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed: $e'), backgroundColor: Colors.red),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const SizedBox(height: 32),
              const Center(
                child: Text('🏘️', style: TextStyle(fontSize: 64)),
              ),
              const SizedBox(height: 16),
              Text(
                'Welcome to Vemavaram Village',
                style: Theme.of(context).textTheme.titleLarge?.copyWith(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                    ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 6),
              Text(
                _isWorker
                    ? 'Field Worker Task Management Portal'
                    : (_isRegister ? 'Register as a citizen of Vemavaram' : 'Login to report and track village issues'),
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(color: Colors.grey.shade600),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 24),

              // Citizen vs Worker Selector
              Container(
                decoration: BoxDecoration(
                  color: Colors.grey.shade100,
                  borderRadius: BorderRadius.circular(12),
                ),
                padding: const EdgeInsets.all(4),
                child: Row(
                  children: [
                    Expanded(
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _isWorker = false;
                          });
                        },
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          decoration: BoxDecoration(
                            color: !_isWorker ? Theme.of(context).colorScheme.primary : Colors.transparent,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            'Citizen',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: !_isWorker ? Colors.white : Colors.grey.shade700,
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      ),
                    ),
                    Expanded(
                      child: GestureDetector(
                        onTap: () {
                          setState(() {
                            _isWorker = true;
                            _isRegister = false;
                          });
                        },
                        child: Container(
                          padding: const EdgeInsets.symmetric(vertical: 10),
                          decoration: BoxDecoration(
                            color: _isWorker ? Colors.orange.shade700 : Colors.transparent,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            'Field Worker',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: _isWorker ? Colors.white : Colors.grey.shade700,
                              fontWeight: FontWeight.bold,
                              fontSize: 13,
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              if (_isRegister && !_isWorker) ...[
                TextField(
                  controller: _nameController,
                  decoration: const InputDecoration(
                    labelText: 'Full Name',
                    prefixIcon: Icon(Icons.person_outline),
                  ),
                ),
                const SizedBox(height: 16),
              ],

              TextField(
                controller: _phoneController,
                keyboardType: TextInputType.phone,
                maxLength: 10,
                decoration: InputDecoration(
                  labelText: _isWorker ? 'Worker Mobile Number' : 'Mobile Number',
                  prefixText: '+91 ',
                  prefixIcon: const Icon(Icons.phone_android),
                ),
              ),
              const SizedBox(height: 12),

              TextField(
                controller: _passwordController,
                obscureText: _obscurePassword,
                decoration: InputDecoration(
                  labelText: 'Password',
                  prefixIcon: const Icon(Icons.lock_outline),
                  suffixIcon: IconButton(
                    icon: Icon(_obscurePassword ? Icons.visibility_off : Icons.visibility),
                    onPressed: () => setState(() => _obscurePassword = !_obscurePassword),
                  ),
                ),
              ),
              const SizedBox(height: 24),

              ElevatedButton(
                onPressed: _isLoading ? null : _submit,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _isWorker ? Colors.orange.shade700 : Theme.of(context).colorScheme.primary,
                  padding: const EdgeInsets.symmetric(vertical: 14),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: _isLoading
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : Text(
                        _isRegister ? 'Register Account' : (_isWorker ? 'Worker Sign In' : 'Sign In'),
                        style: const TextStyle(fontSize: 15, fontWeight: FontWeight.bold, color: Colors.white),
                      ),
              ),

              if (!_isWorker) ...[
                const SizedBox(height: 16),
                TextButton(
                  onPressed: () => setState(() => _isRegister = !_isRegister),
                  child: Text(
                    _isRegister ? 'Already have an account? Sign In' : 'New to Vemavaram? Register Account',
                    style: TextStyle(color: Theme.of(context).colorScheme.primary),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
