// lib/features/offline/sync_service.dart
import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';
import 'package:connectivity_plus/connectivity_plus.dart';

class SyncService {
  static Database? _db;

  static Future<Database> get database async {
    if (_db != null) return _db!;
    _db = await initDB();
    return _db!;
  }

  static Future<Database> initDB() async {
    String path = join(await getDatabasesPath(), 'smart_village_offline.db');
    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        await db.execute('''
          CREATE TABLE pending_complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            description TEXT,
            location TEXT,
            latitude REAL,
            longitude REAL,
            image_path TEXT,
            created_at TEXT
          )
        ''');
      },
    );
  }

  static Future<void> queueComplaint(Map<String, dynamic> data) async {
    final db = await database;
    await db.insert('pending_complaints', data);
  }

  static Future<void> syncPendingComplaints() async {
    var connectivityResult = await (Connectivity().checkConnectivity());
    if (connectivityResult == ConnectivityResult.none) return;

    final db = await database;
    final pending = await db.query('pending_complaints');
    
    if (pending.isEmpty) return;

    for (var complaint in pending) {
      // In a real implementation, send via API here
      // await ApiService.submitComplaint(complaint);
      
      // On success, delete from local queue
      await db.delete('pending_complaints', where: 'id = ?', whereArgs: [complaint['id']]);
    }
  }
}
