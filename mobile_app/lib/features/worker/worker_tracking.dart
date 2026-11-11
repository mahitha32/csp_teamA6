// lib/features/worker/worker_tracking.dart
import 'dart:async';

class WorkerTrackingService {
  static bool isCheckedIn = false;
  static Timer? _timer;

  static void checkIn() {
    isCheckedIn = true;
    // Start polling GPS every 5 minutes
    _timer = Timer.periodic(Duration(minutes: 5), (timer) {
      _sendLocationUpdate();
    });
    print("Worker Checked In");
  }

  static void checkOut() {
    isCheckedIn = false;
    _timer?.cancel();
    _sendLocationUpdate(status: "Checked-out");
    print("Worker Checked Out");
  }

  static void _sendLocationUpdate({String status = "Working"}) {
    if (!isCheckedIn && status != "Checked-out") return;
    // Mock logic to get current location
    double currentLat = 16.4866 + (DateTime.now().second * 0.0001);
    double currentLng = 80.6433 + (DateTime.now().minute * 0.0001);
    
    // In production, send this payload to /api/workers/tracking
    final payload = {
      "lat": currentLat,
      "lng": currentLng,
      "status": status,
      "timestamp": DateTime.now().toIso8601String()
    };
    print("Location Sync: \$payload");
  }
}
