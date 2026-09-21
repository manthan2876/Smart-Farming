class SyncQueueItem {
  const SyncQueueItem({
    required this.path,
    required this.createdAt,
    this.status = 'pending_sync',
    this.location = 'North plot',
    this.language = 'English',
    this.requestId,
  });

  final String path;
  final DateTime createdAt;
  final String status;
  final String location;
  final String language;
  final String? requestId;

  Map<String, dynamic> toJson() => {
        'path': path,
        'created': createdAt.toIso8601String(),
        'status': status,
        'location': location,
        'language': language,
        if (requestId != null) 'request_id': requestId,
      };

  factory SyncQueueItem.fromJson(Map<String, dynamic> json) => SyncQueueItem(
        path: json['path'].toString(),
        createdAt: json['created'] != null
            ? DateTime.parse(json['created'].toString())
            : DateTime.now(),
        status: json['status']?.toString() ?? 'pending_sync',
        location: json['location']?.toString() ?? 'North plot',
        language: json['language']?.toString() ?? 'English',
        requestId: json['request_id']?.toString(),
      );
}
