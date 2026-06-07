import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../viewmodels/feedback_viewmodel.dart';
import '../viewmodels/auth_viewmodel.dart';
import '../core/theme.dart';
import 'common_widgets.dart';

class FeedbackScreen extends StatefulWidget {
  const FeedbackScreen({super.key});

  @override
  State<FeedbackScreen> createState() => _FeedbackScreenState();
}

class _FeedbackScreenState extends State<FeedbackScreen> {
  int _rating = 0;
  final _commentCtrl = TextEditingController();

  @override
  void dispose() {
    _commentCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final fbVM = context.watch<FeedbackViewModel>();

    return Scaffold(
      backgroundColor: AppTheme.backgroundMidnight,
      appBar: AppBar(title: const Text('Feedback')),
      body: fbVM.submitted
        ? const Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.check_circle, color: AppTheme.statusAccepted, size: 64),
                SizedBox(height: 16),
                Text('Thank you!', style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.onSurface, fontFamily: 'serif')),
                SizedBox(height: 8),
                Text('Your feedback helps us improve.', style: TextStyle(color: AppTheme.onSurfaceVariant)),
              ],
            ),
          )
        : SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              children: [
                const SizedBox(height: 16),
                const Text('Rate your experience', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.onSurface)),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: List.generate(5, (i) {
                    return IconButton(
                      icon: Icon(i < _rating ? Icons.star : Icons.star_outline, color: AppTheme.accentGold, size: 40),
                      onPressed: () => setState(() => _rating = i + 1),
                    );
                  }),
                ),
                const SizedBox(height: 24),
                TextField(
                  controller: _commentCtrl,
                  decoration: const InputDecoration(
                    hintText: 'Tell us more about your experience...',
                    prefixIcon: Icon(Icons.edit, color: AppTheme.primaryOrange),
                  ),
                  style: const TextStyle(color: AppTheme.onSurface),
                  maxLines: 4,
                ),
                const SizedBox(height: 24),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: fbVM.isLoading ? null : () => _submit(context),
                    child: fbVM.isLoading
                      ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black))
                      : const Text('Submit Feedback'),
                  ),
                ),
              ],
            ),
          ),
    );
  }

  Future<void> _submit(BuildContext context) async {
    if (_rating == 0) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Please select a rating')));
      return;
    }
    final fbVM = context.read<FeedbackViewModel>();
    final auth = context.read<AuthViewModel>();
    await fbVM.submit(auth.userId!, _rating, _commentCtrl.text.trim());
  }
}
