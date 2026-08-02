class BouFile {
  final String id;
  final String name;
  final String code;
  final int updatedAt; // millisecondsSinceEpoch

  const BouFile({
    required this.id,
    required this.name,
    required this.code,
    required this.updatedAt,
  });

  BouFile copyWith({String? name, String? code, int? updatedAt}) {
    return BouFile(
      id: id,
      name: name ?? this.name,
      code: code ?? this.code,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        'code': code,
        'updatedAt': updatedAt,
      };

  factory BouFile.fromJson(Map<String, dynamic> json) => BouFile(
        id: json['id'] as String,
        name: json['name'] as String,
        code: json['code'] as String,
        updatedAt: json['updatedAt'] as int,
      );

  String get formattedDate {
    final d = DateTime.fromMillisecondsSinceEpoch(updatedAt);
    String two(int n) => n.toString().padLeft(2, '0');
    return '${two(d.day)}/${two(d.month)}/${d.year} à ${two(d.hour)}:${two(d.minute)}';
  }
}
