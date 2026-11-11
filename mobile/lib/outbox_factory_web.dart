import 'package:sembast_web/sembast_web.dart';

final outboxDatabaseFactory = databaseFactoryWeb;
Future<String> outboxDatabasePath() async => 'campus_times_outbox.db';
