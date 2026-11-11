import 'dart:convert';
import 'dart:typed_data';
import 'package:sembast/sembast.dart';
import 'outbox_factory_stub.dart'
    if (dart.library.io) 'outbox_factory_io.dart'
    if (dart.library.html) 'outbox_factory_web.dart' as platform;

class OfflineOutbox {
  OfflineOutbox._();
  static final OfflineOutbox instance = OfflineOutbox._();
  final _store = intMapStoreFactory.store('pending_requests');
  Future<Database>? _database;

  Future<Database> get database => _database ??= _open();

  Future<Database> _open() async => platform.outboxDatabaseFactory.openDatabase(await platform.outboxDatabasePath());

  Future<int> enqueue({required String path, required Map<String, dynamic> fields, required String clientId, required String owner, Map<String, dynamic>? realtime, Uint8List? bytes, String? filename, String fileField = 'attachment'}) async {
    final db = await database;
    return _store.add(db, {
      'path': path,
      'fields': fields,
      'client_id': clientId,
      'owner': owner,
      if (realtime != null) 'realtime': realtime,
      if (bytes != null) 'bytes': base64Encode(bytes),
      if (filename != null) 'filename': filename,
      'file_field': fileField,
      'created_at': DateTime.now().toUtc().toIso8601String(),
    });
  }

  Future<List<RecordSnapshot<int, Map<String, dynamic>>>> pending(String owner) async => _store.find(await database, finder: Finder(filter: Filter.equals('owner', owner), sortOrders: [SortOrder('created_at')]));
  Future<void> remove(int key) async => _store.delete(await database, finder: Finder(filter: Filter.byKey(key)));
}
