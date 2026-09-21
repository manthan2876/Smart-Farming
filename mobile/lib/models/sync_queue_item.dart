class SyncQueueItem {
  const SyncQueueItem({
    this.path = '',
    required this.createdAt,
    this.status = 'pending_sync',
    this.location = 'North plot',
    this.language = 'English',
    this.requestId,
    this.base64Data,
    this.fileName = 'leaf.jpg',
  });

  final String path;
  final DateTime createdAt;
  final String status;
  final String location;
  final String language;
  final String? requestId;
  final String? base64Data;
  final String fileName;

  Map<String, dynamic> toJson() => {
        'path': path,
        'created': createdAt.toIso8601String(),
        'status': status,
        'location': location,
        'language': language,
        if (requestId != null) 'request_id': requestId,
        if (base64Data != null) 'base64_data': base64Data,
        'file_name': fileName,
      };

  factory SyncQueueItem.fromJson(Map<String, dynamic> json) => SyncQueueItem(
        path: json['path']?.toString() ?? '',
        createdAt: json['created'] != null
            ? DateTime.parse(json['created'].toString())
            : DateTime.now(),
        status: json['status']?.toString() ?? 'pending_sync',
        location: json['location']?.toString() ?? 'North plot',
        language: json['language']?.toString() ?? 'English',
        requestId: json['request_id']?.toString(),
        base64Data: json['base64_data']?.toString(),
        fileName: json['file_name']?.toString() ?? 'leaf.jpg',
      );
}
