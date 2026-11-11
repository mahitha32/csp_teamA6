// lib/features/qr/qr_scanner.dart
import 'package:flutter/material.dart';

// Mock implementation of QR Scanner 
// (In production, uses mobile_scanner package)
class QRScannerScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Scan Village QR')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.qr_code_scanner, size: 100, color: Colors.blue),
            SizedBox(height: 20),
            Text('Scan public QR to auto-fill location'),
            SizedBox(height: 40),
            ElevatedButton(
              onPressed: () {
                // Mock result
                Navigator.pop(context, '{"asset_id": "AST-WL-001", "ward": "North Ward"}');
              },
              child: Text('Simulate Scan'),
            )
          ],
        ),
      ),
    );
  }
}
