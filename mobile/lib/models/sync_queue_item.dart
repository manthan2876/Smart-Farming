class SyncQueueItem {
  const SyncQueueItem({
    this.id,
    this.clientUuid,
    this.imageFilePath,
    this.path = '',
    required this.createdAt,
    this.status = 'pending_sync',
    this.location = 'North plot',
    this.language = 'English',
    this.requestId,
    this.base64Data,
    this.fileName = 'leaf.jpg',
    this.plotId,
    this.lat,
    this.lon,
    this.retryCount = 0,
    this.lastAttemptAt,
  });

  final int? id;
  final String? clientUuid;
  final String? imageFilePath;
  final String path;
  final DateTime createdAt;
  final String status;
  final String location;
  final String language;
  final String? requestId;
  final String? base64Data;
  final String fileName;
  final int? plotId;
  final double? lat;
  final double? lon;
  final int retryCount;
  final DateTime? lastAttemptAt;

  SyncQueueItem copyWith({
    int? id,
    String? clientUuid,
    String? imageFilePath,
    int? retryCount,
    DateTime? lastAttemptAt,
    String? status,
  }) =>
      SyncQueueItem(
        id: id ?? this.id,
        clientUuid: clientUuid ?? this.clientUuid,
        imageFilePath: imageFilePath ?? this.imageFilePath,
        path: path,
        createdAt: createdAt,
        status: status ?? this.status,
        location: location,
        language: language,
        requestId: requestId,
        base64Data: base64Data,
        fileName: fileName,
        plotId: plotId,
        lat: lat,
        lon: lon,
        retryCount: retryCount ?? this.retryCount,
        lastAttemptAt: lastAttemptAt ?? this.lastAttemptAt,
      );

  Map<String, dynamic> toJson() => {
        if (id != null) 'id': id,
        if (clientUuid != null) 'client_uuid': clientUuid,
        if (imageFilePath != null) 'image_file_path': imageFilePath,
        'path': path,
        'created': createdAt.toIso8601String(),
        'status': status,
        'location': location,
        'language': language,
        if (requestId != null) 'request_id': requestId,
        if (base64Data != null) 'base64_data': base64Data,
        'file_name': fileName,
        if (plotId != null) 'plot_id': plotId,
        if (lat != null) 'lat': lat,
        if (lon != null) 'lon': lon,
        'retry_count': retryCount,
        if (lastAttemptAt != null) 'last_attempt_at': lastAttemptAt!.toIso8601String(),
      };

  factory SyncQueueItem.fromJson(Map<String, dynamic> json) => SyncQueueItem(
        id: json['id'] != null ? int.tryParse(json['id'].toString()) : null,
        clientUuid: json['client_uuid']?.toString(),
        imageFilePath: json['image_file_path']?.toString(),
        path: json['path']?.toString() ?? '',
        createdAt: json['created'] != null
            ? DateTime.parse(json['created'].toString())
            : (json['created_at'] != null
                ? DateTime.parse(json['created_at'].toString())
                : DateTime.now()),
        status: json['status']?.toString() ?? 'pending_sync',
        location: json['location']?.toString() ?? 'North plot',
        language: json['language']?.toString() ?? 'English',
        requestId: json['request_id']?.toString(),
        base64Data: json['base64_data']?.toString(),
        fileName: json['file_name']?.toString() ?? 'leaf.jpg',
        plotId: json['plot_id'] != null ? int.tryParse(json['plot_id'].toString()) : null,
        lat: json['lat'] != null ? double.tryParse(json['lat'].toString()) : null,
        lon: json['lon'] != null ? double.tryParse(json['lon'].toString()) : null,
        retryCount: json['retry_count'] != null ? int.tryParse(json['retry_count'].toString()) ?? 0 : 0,
        lastAttemptAt: json['last_attempt_at'] != null ? DateTime.tryParse(json['last_attempt_at'].toString()) : null,
      );

  Map<String, dynamic> toDbMap() => {
        if (id != null) 'id': id,
        'client_uuid': clientUuid ?? '',
        'file_name': fileName,
        'image_file_path': imageFilePath ?? '',
        'location': location,
        'language': language,
        'plot_id': plotId,
        'lat': lat,
        'lon': lon,
        'status': status,
        'retry_count': retryCount,
        'last_attempt_at': lastAttemptAt?.toIso8601String(),
        'created_at': createdAt.toIso8601String(),
      };

  factory SyncQueueItem.fromDbMap(Map<String, dynamic> map) => SyncQueueItem(
        id: map['id'] != null ? int.tryParse(map['id'].toString()) : null,
        clientUuid: map['client_uuid']?.toString(),
        imageFilePath: map['image_file_path']?.toString(),
        path: map['image_file_path']?.toString() ?? '',
        createdAt: map['created_at'] != null
            ? DateTime.parse(map['created_at'].toString())
            : DateTime.now(),
        status: map['status']?.toString() ?? 'pending',
        location: map['location']?.toString() ?? 'North plot',
        language: map['language']?.toString() ?? 'English',
        fileName: map['file_name']?.toString() ?? 'leaf.jpg',
        plotId: map['plot_id'] != null ? int.tryParse(map['plot_id'].toString()) : null,
        lat: map['lat'] != null ? double.tryParse(map['lat'].toString()) : null,
        lon: map['lon'] != null ? double.tryParse(map['lon'].toString()) : null,
        retryCount: map['retry_count'] != null ? int.tryParse(map['retry_count'].toString()) ?? 0 : 0,
        lastAttemptAt: map['last_attempt_at'] != null
            ? DateTime.tryParse(map['last_attempt_at'].toString())
            : null,
      );
}

