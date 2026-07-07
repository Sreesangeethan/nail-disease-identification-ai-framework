import 'package:flutter/material.dart';

import '../services/api_service.dart';
import 'upload_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({
    super.key,
    required this.apiService,
    required this.onLogout,
  });

  final ApiService apiService;
  final VoidCallback onLogout;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;
    final user = apiService.currentUser;
    final displayName = user?['full_name'] as String? ?? 'Patient';

    return Scaffold(
      appBar: AppBar(
        title: const Text('Nail AI'),
        actions: [
          IconButton(
            tooltip: 'Sign out',
            onPressed: onLogout,
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(20),
          children: [
            Container(
              padding: const EdgeInsets.all(22),
              decoration: BoxDecoration(
                color: colorScheme.primaryContainer,
                borderRadius: BorderRadius.circular(24),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Welcome, $displayName',
                    style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                          fontWeight: FontWeight.w800,
                          color: colorScheme.onPrimaryContainer,
                        ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Upload a clear nail image to validate quality and run AI analysis.',
                    style: Theme.of(context).textTheme.bodyLarge?.copyWith(
                          color: colorScheme.onPrimaryContainer,
                        ),
                  ),
                  const SizedBox(height: 20),
                  FilledButton.icon(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => UploadScreen(apiService: apiService),
                        ),
                      );
                    },
                    icon: const Icon(Icons.add_a_photo_outlined),
                    label: const Text('Start analysis'),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),
            _InfoCard(
              icon: Icons.verified_outlined,
              title: 'Quality first',
              body:
                  'Images are checked for format, resolution, blur, and lighting before analysis.',
            ),
            _InfoCard(
              icon: Icons.psychology_outlined,
              title: 'AI pipeline',
              body:
                  'The backend runs segmentation, classification, heatmap generation, and severity scoring.',
            ),
            _InfoCard(
              icon: Icons.medical_information_outlined,
              title: 'Clinical reminder',
              body:
                  'AI results are decision support only and should be reviewed by a qualified clinician.',
            ),
          ],
        ),
      ),
    );
  }
}

class _InfoCard extends StatelessWidget {
  const _InfoCard({
    required this.icon,
    required this.title,
    required this.body,
  });

  final IconData icon;
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) {
    final colorScheme = Theme.of(context).colorScheme;

    return Card(
      margin: const EdgeInsets.only(bottom: 14),
      child: Padding(
        padding: const EdgeInsets.all(18),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            CircleAvatar(
              backgroundColor: colorScheme.secondaryContainer,
              foregroundColor: colorScheme.onSecondaryContainer,
              child: Icon(icon),
            ),
            const SizedBox(width: 14),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    body,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: colorScheme.onSurfaceVariant,
                        ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
