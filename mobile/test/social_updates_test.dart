import 'dart:io';
import 'dart:ui' as ui;
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:campus_times_mobile/main.dart';

class FakeSocialApi extends CampusApi {
  final statuses = <Map<String,dynamic>>[{'id':1,'username':'Ayesha','avatar':'','text':'A good day on campus!','media':'','created_at':DateTime.now().toIso8601String(),'is_mine':false,'viewed':false,'view_count':null,'viewers':[]}];
  String? publishedText;
  int views=0;
  @override Future<dynamic> get(String path) async {
    if(path.contains('/status/'))return {'statuses':statuses};
    if(path.contains('/feed/'))return {'posts':[]};
    return {'people':[]};
  }
  @override Future<dynamic> post(String path,Map<String,dynamic> data)async{views++;return {'status':{...statuses.first,'viewed':true}};}
  @override Future<dynamic> upload(String path,{Map<String,String> fields=const{},PickedUpload? file,String fileField='attachment',String method='POST'})async{
    publishedText=fields['text'];return {'status':{'id':2}};
  }
}
void main(){
  TestWidgetsFlutterBinding.ensureInitialized();
  setUpAll(() async {
    for(final entry in {'Ahem':'CAMPUS_PREVIEW_FONT','MaterialIcons':'CAMPUS_PREVIEW_ICONS'}.entries){
      final path=Platform.environment[entry.value];
      if(path!=null){final loader=FontLoader(entry.key);loader.addFont(File(path).readAsBytes().then((bytes)=>ByteData.sublistView(bytes)));await loader.load();}
    }
  });
  setUp(()=>SharedPreferences.setMockInitialValues({}));
  test('light gray theme and video formats',(){
    final theme=campusLightTheme();
    expect(theme.brightness,Brightness.light);
    expect(theme.scaffoldBackgroundColor,const Color(0xfff5f5f5));
    expect(socialVideo('https://example.org/movie.webm?token=abc'),isTrue);
    expect(socialVideo('photo.jpg'),isFalse);
  });
  testWidgets('feed fits a narrow phone and offers selfie and gallery', (tester)async{
    tester.view.physicalSize=const Size(320,720);tester.view.devicePixelRatio=1;
    addTearDown(tester.view.resetPhysicalSize);addTearDown(tester.view.resetDevicePixelRatio);
    final boundary=GlobalKey();
    await tester.pumpWidget(MaterialApp(theme:campusLightTheme(),home:RepaintBoundary(key:boundary,child:Scaffold(appBar:AppBar(title:const Text('Campus Times')),body:FeedScreen(api:FakeSocialApi())))));
    await tester.pumpAndSettle();
    expect(find.text('Photo / video'),findsOneWidget);expect(find.byTooltip('Take selfie'),findsOneWidget);
    expect(tester.takeException(),isNull);
    if(Platform.environment['CAMPUS_CAPTURE_PREVIEW']=='1') await tester.runAsync(() async {
      final image=await (boundary.currentContext!.findRenderObject() as RenderRepaintBoundary).toImage();
      final bytes=await image.toByteData(format:ui.ImageByteFormat.png);
      await File('/tmp/campus-feed-preview.png').writeAsBytes(bytes!.buffer.asUint8List());
    });
    await tester.pumpWidget(const SizedBox());
  });
  testWidgets('chat status opens text and records a view',(tester)async{
    final api=FakeSocialApi();
    await tester.pumpWidget(MaterialApp(theme:campusLightTheme(),home:Scaffold(body:ContactsScreen(api:api))));
    await tester.pumpAndSettle();await tester.tap(find.text('Ayesha'));await tester.pumpAndSettle();
    expect(find.text('A good day on campus!'),findsOneWidget);expect(api.views,1);
    expect(find.byTooltip('Delete status'),findsNothing);
    await tester.pumpWidget(const SizedBox());
  });
  testWidgets('status composer publishes text',(tester)async{
    final api=FakeSocialApi();
    await tester.pumpWidget(MaterialApp(theme:campusLightTheme(),home:Builder(builder:(context)=>Scaffold(body:TextButton(onPressed:()=>Navigator.push(context,MaterialPageRoute(builder:(_)=>StatusComposer(api:api))),child:const Text('Open'))))));
    await tester.tap(find.text('Open'));await tester.pumpAndSettle();
    await tester.enterText(find.byType(TextField),'Hello campus');await tester.tap(find.text('Share status'));await tester.pumpAndSettle();
    expect(api.publishedText,'Hello campus');expect(find.text('Open'),findsOneWidget);
  });
  testWidgets('photo filter produces a grayscale image',(tester)async{
    final source=img.Image(width:30,height:30);img.fill(source,color:img.ColorRgb8(220,50,25));
    PickedUpload? result;
    await tester.pumpWidget(MaterialApp(theme:campusLightTheme(),home:Builder(builder:(context)=>Scaffold(body:TextButton(onPressed:()async{result=await Navigator.push<PickedUpload>(context,MaterialPageRoute(builder:(_)=>PhotoFilterEditor(file:PickedUpload('test.png',Uint8List.fromList(img.encodePng(source)),'image/png'))));},child:const Text('Edit'))))));
    await tester.tap(find.text('Edit'));await tester.pumpAndSettle();await tester.tap(find.text('Mono'));await tester.pumpAndSettle();await tester.tap(find.text('Use photo'));await tester.pumpAndSettle();
    expect(result,isNotNull);final pixel=img.decodeImage(result!.bytes)!.getPixel(10,10);
    expect((pixel.r-pixel.g).abs(),lessThan(3));expect((pixel.g-pixel.b).abs(),lessThan(3));
  });
}
