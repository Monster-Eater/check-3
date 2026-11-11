import 'package:sembast/sembast.dart';

DatabaseFactory get outboxDatabaseFactory => throw UnsupportedError('No local database adapter for this platform.');
Future<String> outboxDatabasePath() async => 'campus_times_outbox.db';
