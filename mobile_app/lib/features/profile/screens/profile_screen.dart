import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../auth/screens/login_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  String _name = 'Citizen';
  String _mobile = '';
  String _role = 'Citizen';

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _name = prefs.getString('user_name') ?? 'Citizen';
      _mobile = prefs.getString('user_mobile') ?? '';
      _role = prefs.getString('user_role') ?? 'Citizen';
    });
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('My Profile', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: Theme.of(context).colorScheme.primary,
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          const SizedBox(height: 12),
          CircleAvatar(
            radius: 46,
            backgroundColor: Theme.of(context).colorScheme.primary.withOpacity(0.15),
            child: Icon(Icons.person, size: 52, color: Theme.of(context).colorScheme.primary),
          ),
          const SizedBox(height: 16),
          Text(_name, textAlign: TextAlign.center, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          if (_mobile.isNotEmpty)
            Text('+91 $_mobile', textAlign: TextAlign.center, style: TextStyle(color: Colors.grey.shade600, fontSize: 14)),
          const SizedBox(height: 32),

          ListTile(
            leading: const Icon(Icons.location_city, color: Colors.blueGrey),
            title: const Text('Village', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: const Text('Vemavaram Village, Krishna District'),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: Colors.grey.shade200)),
          ),
          const SizedBox(height: 12),
          ListTile(
            leading: const Icon(Icons.badge_outlined, color: Colors.blueGrey),
            title: const Text('Account Type', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
            subtitle: Text(_role.toUpperCase()),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: Colors.grey.shade200)),
          ),
          const SizedBox(height: 24),

          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('Logout', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12), side: BorderSide(color: Colors.red.shade100)),
            tileColor: Colors.red.shade50,
            onTap: _logout,
          ),
        ],
      ),
    );
  }
}
