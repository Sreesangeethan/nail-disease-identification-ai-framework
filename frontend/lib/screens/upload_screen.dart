import 'dart:io';

import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';

import '../services/api_service.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key, required this.apiService});

  final ApiService apiService;

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  final ImagePicker _picker = ImagePicker();

  XFile? _selectedImage;
  Map<String, dynamic>? _validationResult;
  Map<String, dynamic>? _analysisResult;
  bool _isBusy = false;

  Future<void> _pickImage(ImageSource source) async {
    try {
      final picked = await _picker.pickImage(
        source: source,
        imageQuality: 92,
        maxWidth: 1600,
      );
      if (picked == null) return;
      setState(() {
        _selectedImage = picked;
        _validationResult = null;
        _analysisResult = null;
      });
    } catch (_) {
      _showMessage('Could not open image picker.');
    }
  }

  Future<void> _validateImage() async {
    final image = _selectedImage;
    if (image == null) {
      _showMessage('Select an image first.');
      return;
    }

    setState(() => _isBusy = true);
    try {
      final result = await widget.apiService.validateImage(image.path);
      setState(() => _validationResult = result);
      _showMessage('Image validation completed.');
    } on ApiException catch (error) {
      _showMessage(error.message);
    } finally {
      if (mounted) setState(() => _isBusy = false);
    }
  }

  Future<void> _runAnalysis() async {
    final image = _selectedImage;
    if (image == null) {
      _showMessage('Select an image first.');
      return;
    }

    setState(() => _isBusy = true);
    try {
      final result = await widget.apiService.analyzeImage(image.path);
      setState(() => _analysisResult = result);
      _showMessage('Analysis completed.');
    } on ApiException catch (error) {
      _showMessage(error.message);
    } finally {
      if (mounted) setState(() => _isBusy = false);
    }
  }

  void _showMessage(String message) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), behavior: SnackBarBehavior.floating),
    );
  }

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Scaffold(
      appBar: AppBar(title: const Text('Upload nail image')),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    AspectRatio(
                      aspectRatio: 4 / 3,
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          color: colorScheme.surfaceContainerHighest,
                          borderRadius: BorderRadius.circular(14),
                        ),
                        child: _selectedImage == null
                            ? _EmptyImageState(colorScheme: colorScheme)
                            : ClipRRect(
                                borderRadius: BorderRadius.circular(14),
                                child: Image.file(
                                  File(_selectedImage!.path),
                                  fit: BoxFit.cover,
                                ),
                              ),
                      ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _isBusy
                                ? null
                                : () => _pickImage(ImageSource.camera),
                            icon: const Icon(Icons.photo_camera_outlined),
                            label: const Text('Camera'),
                          ),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: OutlinedButton.icon(
                            onPressed: _isBusy
                                ? null
                                : () => _pickImage(ImageSource.gallery),
                            icon: const Icon(Icons.photo_library_outlined),
                            label: const Text('Gallery'),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    FilledButton.icon(
                      onPressed: _isBusy ? null : _validateImage,
                      icon: const Icon(Icons.fact_check_outlined),
                      label: const Text('Validate image quality'),
                    ),
                    const SizedBox(height: 10),
                    FilledButton.tonalIcon(
                      onPressed: _isBusy ? null : _runAnalysis,
                      icon: const Icon(Icons.biotech_outlined),
                      label: const Text('Run AI analysis'),
                    ),
                    if (_isBusy) ...[
                      const SizedBox(height: 16),
                      const LinearProgressIndicator(),
                    ],
                  ],
                ),
              ),
            ),
            if (_validationResult != null) ...[
              const SizedBox(height: 16),
              _ValidationCard(result: _validationResult!),
            ],
            if (_analysisResult != null) ...[
              const SizedBox(height: 16),
              _AnalysisCard(result: _analysisResult!),
            ],
          ],
        ),
      ),
    );
  }
}

class _EmptyImageState extends StatelessWidget {
  const _EmptyImageState({required this.colorScheme});

  final ColorScheme colorScheme;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.add_photo_alternate_outlined,
            size: 56,
            color: colorScheme.onSurfaceVariant,
          ),
          const SizedBox(height: 10),
          Text(
            'Choose a clear nail image',
            style: Theme.of(context).textTheme.titleMedium,
          ),
        ],
      ),
    );
  }
}

class _ValidationCard extends StatelessWidget {
  const _ValidationCard({required this.result});

  final Map<String, dynamic> result;

  @override
  Widget build(BuildContext context) {
    final metadata = result['metadata'] as Map<String, dynamic>? ?? {};
    final warnings = result['warnings'] as List<dynamic>? ?? const [];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Image quality',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
            ),
            const SizedBox(height: 12),
            _MetricRow(
              label: 'Resolution',
              value: '${metadata['width']} x ${metadata['height']}',
            ),
            _MetricRow(
              label: 'Blur score',
              value: '${metadata['blur_score'] ?? '-'}',
            ),
            _MetricRow(
              label: 'Brightness',
              value: '${metadata['brightness'] ?? '-'}',
            ),
            if (warnings.isNotEmpty) ...[
              const SizedBox(height: 8),
              ...warnings.map((warning) => Text('- $warning')),
            ],
          ],
        ),
      ),
    );
  }
}

class _AnalysisCard extends StatelessWidget {
  const _AnalysisCard({required this.result});

  final Map<String, dynamic> result;

  @override
  Widget build(BuildContext context) {
    final condition = result['predicted_condition'] ?? 'Unknown';
    final confidence = result['confidence'];
    final severity = result['severity_label'] ?? 'Unknown';
    final score = result['severity_score'];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              'Analysis result',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.w800,
                  ),
            ),
            const SizedBox(height: 12),
            _MetricRow(label: 'Condition', value: '$condition'),
            _MetricRow(label: 'Confidence', value: '$confidence'),
            _MetricRow(label: 'Severity', value: '$severity'),
            _MetricRow(label: 'Severity score', value: '$score'),
            const SizedBox(height: 12),
            Text(
              'This result is decision support only and is not a standalone diagnosis.',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

class _MetricRow extends StatelessWidget {
  const _MetricRow({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          Expanded(
            child: Text(
              label,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontWeight: FontWeight.w600,
                  ),
            ),
          ),
          Text(value),
        ],
      ),
    );
  }
}
