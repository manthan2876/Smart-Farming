class SyncQueueItem {
  const SyncQueueItem({required this.path, required this.createdAt, this.status = 'pending_sync'});

  final String path;
  final DateTime createdAt;
  final String status;

  Map<String, dynamic> toJson() => {'path': path, 'created': createdAt.toIso8601String(), 'status': status};
  factory SyncQueueItem.fromJson(Map<String, dynamic> json) => SyncQueueItem(path: json['path'].toString(), createdAt: DateTime.parse(json['created'].toString()), status: json['status']?.toString() ?? 'pending_sync');
}
