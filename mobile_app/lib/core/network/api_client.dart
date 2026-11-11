import 'dart:io' show Platform;
import 'package:flutter/foundation.dart';
import 'package:dio/dio.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ApiClient {
  static String get defaultBaseUrl {
    if (kIsWeb) return 'http://localhost:5000/api';
    try {
      if (Platform.isAndroid) return 'http://10.0.2.2:5000/api';
      return 'http://127.0.0.1:5000/api';
    } catch (_) {
      return 'http://10.0.2.2:5000/api';
    }
  }

  late final Dio dio;

  ApiClient() {
    dio = Dio(BaseOptions(
      baseUrl: defaultBaseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      headers: {
        'Accept': 'application/json',
      },
    ));

    dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final prefs = await SharedPreferences.getInstance();
        // Allow custom base url override if stored in preferences
        final customUrl = prefs.getString('api_base_url');
        if (customUrl != null && customUrl.isNotEmpty) {
          options.baseUrl = customUrl;
        }

        final token = prefs.getString('access_token');
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (DioException e, handler) async {
        if (e.response?.statusCode == 401) {
          final prefs = await SharedPreferences.getInstance();
          await prefs.remove('access_token');
        }
        return handler.next(e);
      },
    ));
  }
}

final apiClient = ApiClient().dio;
