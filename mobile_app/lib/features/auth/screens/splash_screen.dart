import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'login_screen.dart';
import '../../complaints/screens/home_screen.dart';
import '../../worker/screens/worker_home_screen.dart';

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkAuth();
  }

  Future<void> _checkAuth() async {
    await Future.delayed(const Duration(seconds: 2));
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    final role = prefs.getString('user_role');
    
    if (!mounted) return;
    
    if (token != null) {
      if (role == 'worker') {
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const WorkerHomeScreen()));
      } else {
        Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const HomeScreen()));
      }
    } else {
      Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const LoginScreen()));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.primary,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              '🏘️',
              style: TextStyle(fontSize: 80),
            ),
            const SizedBox(height: 24),
            Text(
              'Vemavaram Village',
              style: Theme.of(context).textTheme.displayLarge?.copyWith(
                color: Colors.white,
                fontSize: 28,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'Complaint Redressal System',
              style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                color: Colors.white.withOpacity(0.8),
                letterSpacing: 1.2,
              ),
            ),
            const SizedBox(height: 48),
            const CircularProgressIndicator(
              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
            ),
          ],
        ),
      ),
    );
  }
}
