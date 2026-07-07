import 'dart:convert';

import 'package:http/http.dart' as http;

class ApiException implements Exception {
  const ApiException(this.message, {this.statusCode, this.code, this.details});

  final String message;
  final int? statusCode;
  final String? code;
  final Map<String, dynamic>? details;

  @override
  String toString() => message;
}

class ApiService {
  ApiService({
    this.baseUrl = 'http://127.0.0.1:5000/api',
    http.Client? client,
  }) : _client = client ?? http.Client();

  final String baseUrl;
  final http.Client _client;

  String? _token;
  Map<String, dynamic>? _currentUser;

  bool get isAuthenticated => _token != null;
  String? get token => _token;
  Map<String, dynamic>? get currentUser => _currentUser;

  Future<Map<String, dynamic>> login({
    required String email,
    required String password,
  }) async {
    final response = await _postJson('/auth/login', {
      'email': email.trim(),
      'password': password,
    });

    final data = response['data'] as Map<String, dynamic>;
    _token = data['access_token'] as String?;
    _currentUser = data['user'] as Map<String, dynamic>?;

    if (_token == null || _token!.isEmpty) {
      throw const ApiException('Login response did not include a token');
    }
    return data;
  }

  Future<Map<String, dynamic>> register({
    required String fullName,
    required String email,
    required String password,
  }) async {
    final response = await _postJson('/auth/register', {
      'full_name': fullName.trim(),
      'email': email.trim(),
      'password': password,
    });
    return response['data'] as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> fetchProfile() async {
    final response = await _getJson('/auth/profile');
    _currentUser = response['data'] as Map<String, dynamic>;
    return _currentUser!;
  }

  Future<Map<String, dynamic>> validateImage(String imagePath) async {
    final response = await _postMultipartImage('/upload/validate', imagePath);
    return response['data'] as Map<String, dynamic>;
  }

  Future<Map<String, dynamic>> analyzeImage(String imagePath) async {
    final response = await _postMultipartImage('/analyze', imagePath);
    return response['data'] as Map<String, dynamic>;
  }

  void logout() {
    _token = null;
    _currentUser = null;
  }

  Future<Map<String, dynamic>> _getJson(String path) async {
    final uri = Uri.parse('$baseUrl$path');
    final response = await _client.get(uri, headers: _headers());
    return _decodeResponse(response);
  }

  Future<Map<String, dynamic>> _postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    final uri = Uri.parse('$baseUrl$path');
    final response = await _client.post(
      uri,
      headers: _headers(contentTypeJson: true),
      body: jsonEncode(body),
    );
    return _decodeResponse(response);
  }

  Future<Map<String, dynamic>> _postMultipartImage(
    String path,
    String imagePath,
  ) async {
    final uri = Uri.parse('$baseUrl$path');
    final request = http.MultipartRequest('POST', uri);
    request.headers.addAll(_headers());
    request.files.add(await http.MultipartFile.fromPath('image', imagePath));

    final streamedResponse = await _client.send(request);
    final response = await http.Response.fromStream(streamedResponse);
    return _decodeResponse(response);
  }

  Map<String, String> _headers({bool contentTypeJson = false}) {
    return {
      'Accept': 'application/json',
      if (contentTypeJson) 'Content-Type': 'application/json',
      if (_token != null) 'Authorization': 'Bearer $_token',
    };
  }

  Map<String, dynamic> _decodeResponse(http.Response response) {
    Map<String, dynamic> payload;
    try {
      payload = jsonDecode(response.body) as Map<String, dynamic>;
    } on FormatException {
      throw ApiException(
        'Server returned an invalid response',
        statusCode: response.statusCode,
      );
    }

    if (response.statusCode >= 400 || payload['success'] == false) {
      final error = payload['error'] as Map<String, dynamic>?;
      throw ApiException(
        error?['message'] as String? ?? 'Request failed',
        statusCode: response.statusCode,
        code: error?['code'] as String?,
        details: error?['details'] as Map<String, dynamic>?,
      );
    }

    return payload;
  }
}
