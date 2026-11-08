import 'package:campus_times_mobile/main.dart';
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

void main() {
  setUp(() => SharedPreferences.setMockInitialValues({}));

  test('restores the phone server address without an existing session', () async {
    SharedPreferences.setMockInitialValues({'server_url': 'http://192.168.1.20:5000/'});
    final api = CampusApi();
    expect(await api.restore(), isFalse);
    expect(api.uri('/api/mobile/me/').toString(),
        'http://192.168.1.20:5000/api/mobile/me/');
  });

  testWidgets('login server dialog saves a valid LAN URL', (tester) async {
    final api = CampusApi();
    await tester.pumpWidget(MaterialApp(home: LoginScreen(api: api, onSignedIn: () {})));
    await tester.tap(find.text('Backend server'));
    await tester.pumpAndSettle();
    await tester.enterText(find.descendant(of: find.byType(AlertDialog), matching: find.byType(TextField)), 'http://192.168.1.20:5000/');
    await tester.tap(find.text('Save'));
    await tester.pumpAndSettle();
    expect(api.base, 'http://192.168.1.20:5000');
    expect((await SharedPreferences.getInstance()).getString('server_url'), api.base);
  });

  testWidgets('login rejects URLs containing embedded credentials', (tester) async {
    final api = CampusApi();
    final original = api.base;
    await tester.pumpWidget(MaterialApp(home: LoginScreen(api: api, onSignedIn: () {})));
    await tester.tap(find.text('Backend server'));
    await tester.pumpAndSettle();
    await tester.enterText(find.descendant(of: find.byType(AlertDialog), matching: find.byType(TextField)), 'http://user:pass@192.168.1.20:5000');
    await tester.tap(find.text('Save'));
    await tester.pumpAndSettle();
    expect(api.base, original);
    expect(find.textContaining('Enter a valid server URL'), findsOneWidget);
  });
}
