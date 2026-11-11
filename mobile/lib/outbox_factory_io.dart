import 'package:path_provider/path_provider.dart';
import 'package:sembast/sembast_io.dart';

final DatabaseFactory outboxDatabaseFactory = databaseFactoryIo;
Future<String> outboxDatabasePath() async => '${(await getApplicationDocumentsDirectory()).path}/campus_times_outbox.db';
