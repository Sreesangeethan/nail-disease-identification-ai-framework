# Flutter Integration

## Suggested Flutter Structure

```text
lib/
  core/
    api/
      api_client.dart
      api_exception.dart
    config/
      app_config.dart
    storage/
      token_storage.dart
  features/
    auth/
      data/auth_api.dart
      models/user.dart
      screens/login_screen.dart
      screens/register_screen.dart
    analysis/
      data/analysis_api.dart
      models/analysis_result.dart
      screens/upload_screen.dart
      screens/analysis_result_screen.dart
    history/
      data/history_api.dart
      screens/history_screen.dart
    feedback/
      data/feedback_api.dart
  main.dart
```

## pubspec.yaml Dependencies

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.2.2
  image_picker: ^1.1.2
  flutter_secure_storage: ^9.2.2
```

## API Client

```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiClient {
  ApiClient({required this.baseUrl, this.token});

  final String baseUrl;
  final String? token;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        if (token != null) 'Authorization': 'Bearer $token',
      };

  Future<Map<String, dynamic>> postJson(
    String path,
    Map<String, dynamic> body,
  ) async {
    final response = await http.post(
      Uri.parse('$baseUrl$path'),
      headers: _headers,
      body: jsonEncode(body),
    );
    return _decode(response);
  }

  Future<Map<String, dynamic>> getJson(String path) async {
    final response = await http.get(
      Uri.parse('$baseUrl$path'),
      headers: _headers,
    );
    return _decode(response);
  }

  Map<String, dynamic> _decode(http.Response response) {
    final body = jsonDecode(response.body) as Map<String, dynamic>;
    if (response.statusCode >= 400) {
      throw Exception(body['error']?['message'] ?? 'API request failed');
    }
    return body;
  }
}
```

## Login Example

```dart
final client = ApiClient(baseUrl: 'http://10.0.2.2:5000/api');

final response = await client.postJson('/auth/login', {
  'email': 'patient@example.com',
  'password': 'Password123',
});

final token = response['data']['access_token'] as String;
```

Use `10.0.2.2` for Android emulator localhost access. Use your computer LAN IP for a physical device.

## Upload and Analyze Example

```dart
import 'package:http/http.dart' as http;

Future<Map<String, dynamic>> analyzeImage({
  required String baseUrl,
  required String token,
  required String imagePath,
}) async {
  final request = http.MultipartRequest(
    'POST',
    Uri.parse('$baseUrl/analyze'),
  );

  request.headers['Authorization'] = 'Bearer $token';
  request.files.add(await http.MultipartFile.fromPath('image', imagePath));

  final streamed = await request.send();
  final response = await http.Response.fromStream(streamed);

  final decoded = jsonDecode(response.body) as Map<String, dynamic>;
  if (response.statusCode >= 400) {
    throw Exception(decoded['error']?['message'] ?? 'Analysis failed');
  }
  return decoded['data'] as Map<String, dynamic>;
}
```

## UI Flow

1. Register or login.
2. Store JWT securely using `flutter_secure_storage`.
3. Select or capture nail image.
4. Call `/upload/validate` for quality feedback.
5. Call `/analyze` for final report.
6. Show prediction, severity, confidence, and clinical notice.
7. Let user submit feedback through `/analysis/{id}/feedback`.
