class CodeResult {
  final bool success;
  final String output;
  final String? error;

  CodeResult({required this.success, required this.output, this.error});

  factory CodeResult.fromJson(Map<String, dynamic> json) {
    return CodeResult(
      success: json['success'] ?? false,
      output: json['output'] ?? '',
      error: json['error'],
    );
  }
}
