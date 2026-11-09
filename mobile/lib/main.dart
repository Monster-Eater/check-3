import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:image_picker/image_picker.dart';
import 'package:record/record.dart';
import 'package:path_provider/path_provider.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image/image.dart' as img;
import 'package:video_player/video_player.dart';
import 'package:just_audio/just_audio.dart';

part 'social_updates.dart';

const configuredApiBaseUrl = String.fromEnvironment('API_BASE_URL');
const brand = Color(0xff555555);

void main() => runApp(const CampusTimesApp());

class CampusTimesApp extends StatefulWidget {
  const CampusTimesApp({super.key});
  @override
  State<CampusTimesApp> createState() => _CampusTimesAppState();
}

class _CampusTimesAppState extends State<CampusTimesApp> {
  final api = CampusApi();
  bool loading = true;
  bool signedIn = false;
  ThemeMode themeMode = ThemeMode.system;
  @override
  void initState() {
    super.initState();
    api.restore().then((v) async {
      final prefs = await SharedPreferences.getInstance();
      if (mounted)
        setState(() {
          signedIn = v;
          loading = false;
          themeMode = prefs.getBool("dark_theme") == true
              ? ThemeMode.dark
              : ThemeMode.light;
        });
    });
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'Campus Times',
    debugShowCheckedModeBanner: false,
    theme: campusLightTheme(),
    themeMode: ThemeMode.light,
    home: loading
        ? const Scaffold(body: Center(child: CircularProgressIndicator()))
        : signedIn
        ? HomeShell(
            key: ValueKey(api.activeUsername),
            api: api,
            onSignOut: () => setState(() => signedIn = false),
            onAddAccount: () => setState(() => signedIn = false),
            onSwitchAccount: () => setState(() => signedIn = true),
            dark: themeMode == ThemeMode.dark,
            onTheme: (v) async {
              final prefs = await SharedPreferences.getInstance();
              await prefs.setBool("dark_theme", v);
              if (mounted)
                setState(
                  () => themeMode = v ? ThemeMode.dark : ThemeMode.light,
                );
            },
          )
        : LoginScreen(
            api: api,
            onSignedIn: () => setState(() => signedIn = true),
            onCancel: api.token != null ? () => setState(() => signedIn = true) : null,
          ),
  );
}

class PickedUpload {
  final String name;
  final Uint8List bytes;
  final String? mime;
  PickedUpload(this.name, this.bytes, this.mime);
}

Future<PickedUpload?> pickUpload({bool imagesOnly = false}) async {
  final result = await FilePicker.platform.pickFiles(
    withData: true,
    type: imagesOnly ? FileType.image : FileType.any,
    allowMultiple: false,
  );
  if (result == null || result.files.isEmpty) return null;
  final f = result.files.first;
  if (f.bytes == null) return null;
  return PickedUpload(f.name, f.bytes!, f.extension);
}

/// Shared media tools for direct and group conversations.
class ChatMediaTools {
  static final ImagePicker camera = ImagePicker();

  static Future<PickedUpload?> gallery({required bool video}) async {
    final XFile? picked = video
        ? await camera.pickVideo(source: ImageSource.gallery)
        : await camera.pickImage(source: ImageSource.gallery, imageQuality: 90);
    if (picked == null) return null;
    return PickedUpload(picked.name, await picked.readAsBytes(), picked.mimeType);
  }

  static Future<PickedUpload?> capture({required bool video}) async {
    final XFile? picked = video
        ? await camera.pickVideo(
            source: ImageSource.camera,
            maxDuration: const Duration(minutes: 2),
          )
        : await camera.pickImage(source: ImageSource.camera, imageQuality: 85);
    if (picked == null) return null;
    return PickedUpload(
      picked.name,
      await picked.readAsBytes(),
      picked.mimeType,
    );
  }

  static Future<PickedUpload?> editPhoto(
    BuildContext context,
    PickedUpload file,
  ) async {
    return Navigator.push<PickedUpload>(
      context,
      MaterialPageRoute(builder: (_) => PhotoFilterEditor(file: file)),
    );
  }

  static Future<PickedUpload?> editVideo(
    BuildContext context,
    CampusApi api,
    PickedUpload file,
  ) async {
    final durationData = await api.videoInfo(file);
    final total = (durationData['duration'] as num).toDouble();
    if (total <= 0) throw Exception('Could not read video duration.');
    var start = 0.0;
    var end = total;
    final controller = VideoPlayerController.networkUrl(
      Uri.dataFromBytes(file.bytes, mimeType: file.mime ?? 'video/mp4'),
    );
    var previewReady = false;
    try {
      await controller.initialize();
      previewReady = true;
    } catch (_) {
      /* Some browsers cannot preview this format. */
    }
    if (!context.mounted) {
      await controller.dispose();
      return null;
    }
    final accepted = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => StatefulBuilder(
        builder: (dialogContext, update) => AlertDialog(
          title: const Text('Trim video before sending'),
          content: SizedBox(
            width: 350,
            height: 340,
            child: Column(
              children: [
                if (previewReady)
                  Expanded(
                    child: AspectRatio(
                      aspectRatio: controller.value.aspectRatio > 0
                          ? controller.value.aspectRatio
                          : 16 / 9,
                      child: VideoPlayer(controller),
                    ),
                  )
                else
                  const Expanded(
                    child: Center(
                      child: Text(
                        'Preview unavailable for this format. Trimming is still supported.',
                      ),
                    ),
                  ),
                if (previewReady)
                  TextButton.icon(
                    icon: Icon(
                      controller.value.isPlaying
                          ? Icons.pause
                          : Icons.play_arrow,
                    ),
                    label: Text(
                      controller.value.isPlaying
                          ? 'Pause preview'
                          : 'Play preview',
                    ),
                    onPressed: () async {
                      if (controller.value.isPlaying) {
                        await controller.pause();
                      } else {
                        await controller.seekTo(
                          Duration(milliseconds: (start * 1000).round()),
                        );
                        await controller.play();
                      }
                      update(() {});
                    },
                  ),
                Text(
                  'From ${start.toStringAsFixed(1)}s to ${end.toStringAsFixed(1)}s (total ${total.toStringAsFixed(1)}s)',
                ),
                RangeSlider(
                  values: RangeValues(start, end),
                  min: 0,
                  max: total,
                  onChanged: (v) {
                    if (v.end - v.start >= 0.5)
                      update(() {
                        start = v.start;
                        end = v.end;
                      });
                  },
                ),
                const Text(
                  'The server will export the selected segment as MP4.',
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(dialogContext, false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(dialogContext, true),
              child: const Text('Trim & use'),
            ),
          ],
        ),
      ),
    );
    await controller.dispose();
    if (accepted != true) return null;
    return api.trimVideo(file, start, end);
  }

  static Future<String> currentLocationLink() async {
    if (!await Geolocator.isLocationServiceEnabled())
      throw Exception('Enable location services first.');
    var permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied)
      permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      throw Exception(
        'Location permission is required to share your location.',
      );
    }
    final position = await Geolocator.getCurrentPosition(
      locationSettings: const LocationSettings(accuracy: LocationAccuracy.high),
    );
    return 'https://www.google.com/maps/search/?api=1&query=${position.latitude},${position.longitude}';
  }
}

Widget chatAttachment(String url, bool mine) {
   final path = (Uri.tryParse(url)?.path.toLowerCase() ?? url.toLowerCase()).split('?').first;
  final isImage = path.contains('.png') || path.contains('.jpg') || path.contains('.jpeg') || path.contains('.gif') || path.contains('.webp') || path.contains('/image/') || path.contains('image/upload');
  if (isImage)
    return InkWell(
      onTap: () => launchExternal(url),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(10),
        child: Image.network(
          url,
          width: 220,
          height: 180,
          fit: BoxFit.cover,
          errorBuilder: (_, __, ___) => const Text('Image unavailable'),
        ),
      ),
    );
    final isAudio = path.contains('.m4a') || path.contains('.mp3') || path.contains('.wav') || path.contains('.ogg') || path.contains('/audio/') || path.contains('audio/upload');
    final isVideo = (path.contains('.mp4') || path.contains('.mov') || path.contains('.mkv') || path.contains('.webm') || path.contains('/video/') || path.contains('video/upload')) && !isAudio;
  if (isAudio) return InlineAudioPlayer(url: url);
  if (isVideo) return InlineVideoPlayer(url: url);
  return TextButton.icon(
    onPressed: () => launchExternal(url),
    icon: Icon(Icons.attach_file, color: brand),
    label: Text('Open attachment', style: TextStyle(color: brand)),
  );
}

class InlineAudioPlayer extends StatefulWidget {
  const InlineAudioPlayer({super.key, required this.url});
  final String url;
  @override
  State<InlineAudioPlayer> createState() => _InlineAudioPlayerState();
}

class _InlineAudioPlayerState extends State<InlineAudioPlayer> {
  final AudioPlayer player = AudioPlayer();
  bool ready = false;
  String? error;
  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    try {
      await player.setUrl(widget.url);
      if (mounted) setState(() => ready = true);
    } catch (e) {
      if (mounted) setState(() => error = 'Audio unavailable');
    }
  }

  @override
  void dispose() {
    player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => SizedBox(
    width: 240,
    child: Row(
      children: [
        StreamBuilder<PlayerState>(
          stream: player.playerStateStream,
          builder: (context, snap) {
            final playing = snap.data?.playing ?? false;
            return IconButton(
              tooltip: playing ? 'Pause' : 'Play',
              onPressed: !ready
                  ? null
                  : () async {
                      if (playing) {
                        await player.pause();
                      } else {
                        if (player.processingState == ProcessingState.completed)
                          await player.seek(Duration.zero);
                        await player.play();
                      }
                    },
              icon: Icon(playing ? Icons.pause_circle : Icons.play_circle),
            );
          },
        ),
        Expanded(
          child: StreamBuilder<Duration>(
            stream: player.positionStream,
            builder: (context, snap) {
              final duration = player.duration ?? Duration.zero;
              final position = snap.data ?? Duration.zero;
              final max = duration.inMilliseconds > 0
                  ? duration.inMilliseconds.toDouble()
                  : 1.0;
              return Slider(
                value: position.inMilliseconds.clamp(0, max.toInt()).toDouble(),
                max: max,
                onChanged: !ready || duration == Duration.zero
                    ? null
                    : (value) =>
                          player.seek(Duration(milliseconds: value.round())),
              );
            },
          ),
        ),
        if (error != null)
          IconButton(
            tooltip: error!,
            onPressed: () => launchExternal(widget.url),
            icon: const Icon(Icons.open_in_new),
          ),
      ],
    ),
  );
}

class InlineVideoPlayer extends StatefulWidget {
  const InlineVideoPlayer({super.key, required this.url});
  final String url;
  @override
  State<InlineVideoPlayer> createState() => _InlineVideoPlayerState();
}

class _InlineVideoPlayerState extends State<InlineVideoPlayer> {
  late final VideoPlayerController player;
  bool failed = false;
  @override
  void initState() {
    super.initState();
    player = VideoPlayerController.networkUrl(Uri.parse(widget.url));
    _init();
  }

  Future<void> _init() async {
    try {
      await player.initialize();
      if (mounted) setState(() {});
    } catch (_) {
      if (mounted) setState(() => failed = true);
    }
  }

  @override
  void dispose() {
    player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    if (failed)
      return TextButton.icon(
        onPressed: () => launchExternal(widget.url),
        icon: const Icon(Icons.open_in_new),
        label: const Text('Open video'),
      );
    if (!player.value.isInitialized)
      return const SizedBox(
        width: 240,
        height: 140,
        child: Center(child: CircularProgressIndicator()),
      );
    return SizedBox(
      width: 260,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          AspectRatio(
            aspectRatio: player.value.aspectRatio > 0
                ? player.value.aspectRatio
                : 16 / 9,
            child: VideoPlayer(player),
          ),
          Row(
            children: [
              IconButton(
                onPressed: () {
                  if (player.value.isPlaying) {
                    player.pause();
                  } else {
                    player.play();
                  }
                  setState(() {});
                },
                icon: Icon(
                  player.value.isPlaying ? Icons.pause : Icons.play_arrow,
                ),
              ),
              Expanded(
                child: VideoProgressIndicator(
                  player,
                  allowScrubbing: true,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
              IconButton(
                tooltip: 'Open externally',
                onPressed: () => launchExternal(widget.url),
                icon: const Icon(Icons.open_in_new, size: 18),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class CampusApi {
  String? token;
  String? activeUsername;
  String? serverOverride;
  final prefsFuture = SharedPreferences.getInstance();
  String get base {
    final raw =
        serverOverride ??
        (configuredApiBaseUrl.isNotEmpty
            ? configuredApiBaseUrl
            : (kIsWeb ? 'http://127.0.0.1:5000' : 'http://10.0.2.2:5000'));
    return raw.replaceFirst(RegExp(r'/+$'), '');
  }

  Uri uri(String path) => Uri.parse('$base$path');
  Map<String, String> get headers => {
    'Accept': 'application/json',
    if (token != null) 'Authorization': 'Bearer $token',
  };
  Future<bool> restore() async {
    serverOverride = (await prefsFuture).getString('server_url');
    token = (await prefsFuture).getString('api_token');
    activeUsername = (await prefsFuture).getString('active_username');
    if (token == null) return false;
    try {
      await get('/api/mobile/me/');
      return true;
    } on ApiException catch (e) {
      if (e.statusCode == 401) {
        token = null;
        await (await prefsFuture).remove('api_token');
        return false;
      }
      return true; // Keep the token during temporary server errors.
    } catch (_) {
      return true; // A network outage must not sign the user out.
    }
  }

  dynamic decode(http.Response r) {
    dynamic b;
    try {
      b = r.body.isEmpty ? <String, dynamic>{} : jsonDecode(r.body);
    } catch (_) {
      b = {'error': 'Server returned an invalid response (${r.statusCode}).'};
    }
    if (r.statusCode < 200 || r.statusCode >= 300) {
      final message = b is Map
          ? (b['error'] ?? 'Request failed (${r.statusCode})').toString()
          : 'Request failed (${r.statusCode})';
      throw ApiException(r.statusCode, message);
    }
    return b;
  }

  Future<dynamic> get(String p) async => decode(
    await http
        .get(uri(p), headers: headers)
        .timeout(const Duration(seconds: 30)),
  );
  Future<dynamic> post(String p, Map<String, dynamic> data) async => decode(
    await http
        .post(
          uri(p),
          headers: {...headers, 'Content-Type': 'application/json'},
          body: jsonEncode(data),
        )
        .timeout(const Duration(seconds: 30)),
  );
  Future<dynamic> patch(String p, Map<String, dynamic> data) async => decode(
    await http
        .patch(
          uri(p),
          headers: {...headers, 'Content-Type': 'application/json'},
          body: jsonEncode(data),
        )
        .timeout(const Duration(seconds: 30)),
  );
  Future<dynamic> delete(String p) async => decode(
    await http.delete(uri(p), headers: headers).timeout(const Duration(seconds: 30)),
  );
  Future<dynamic> upload(
    String p, {
    Map<String, String> fields = const {},
    PickedUpload? file,
    String fileField = 'attachment',
    String method = 'POST',
  }) async {
    final req = http.MultipartRequest(method, uri(p));
    req.headers.addAll(headers);
    req.fields.addAll(fields);
    if (file != null)
      req.files.add(
        http.MultipartFile.fromBytes(
          fileField,
          file.bytes,
          filename: file.name,
        ),
      );
    final streamed = await req.send().timeout(const Duration(seconds: 90));
    return decode(await http.Response.fromStream(streamed));
  }

  Future<dynamic> videoInfo(PickedUpload file) async =>
      upload('/api/mobile/media/video-info/', file: file, fileField: 'video');
  Future<PickedUpload> trimVideo(
    PickedUpload file,
    double start,
    double end,
  ) async {
    final req = http.MultipartRequest('POST', uri('/api/mobile/media/trim/'));
    req.headers.addAll(headers);
    req.fields.addAll({
      'start': start.toStringAsFixed(3),
      'end': end.toStringAsFixed(3),
    });
    req.files.add(
      http.MultipartFile.fromBytes('video', file.bytes, filename: file.name),
    );
    final response = await http.Response.fromStream(
      await req.send().timeout(const Duration(minutes: 4)),
    );
    if (response.statusCode != 200) {
      decode(response);
      throw Exception('Video trim failed.');
    }
    return PickedUpload(
      'trimmed_${DateTime.now().millisecondsSinceEpoch}.mp4',
      response.bodyBytes,
      'video/mp4',
    );
  }

  Future<void> signUp(Map<String, dynamic> details) async {
    final data = await post('/api/mobile/signup/', details);
    token = data['token'];
    activeUsername = (data['username'] ?? details['username']).toString();
    await _rememberAccount();
  }

  Future<void> signIn(String username, String password) async {
    final data = await post('/api/mobile/login/', {
      'username': username,
      'password': password,
    });
    token = data['token'];
    activeUsername = (data['username'] ?? username).toString();
    await _rememberAccount();
  }

  Future<void> _rememberAccount() async {
    final prefs=await prefsFuture;
    final raw=prefs.getString('saved_accounts')??'{}';
    Map<String,dynamic> accounts={};
    try{accounts=Map<String,dynamic>.from(jsonDecode(raw) as Map);}catch(_){}
    if(activeUsername!=null&&token!=null)accounts[activeUsername!]=token;
    await prefs.setString('saved_accounts',jsonEncode(accounts));
    await prefs.setString('active_username',activeUsername??'');
    if(token!=null)await prefs.setString('api_token',token!);
  }

  Future<List<String>> accountNames() async {
    final raw=(await prefsFuture).getString('saved_accounts')??'{}';
    try{return Map<String,dynamic>.from(jsonDecode(raw) as Map).keys.cast<String>().toList();}catch(_){return <String>[];}
  }

  Future<void> switchAccount(String username) async {
    final prefs=await prefsFuture;
    final raw=prefs.getString('saved_accounts')??'{}';
    final accounts=Map<String,dynamic>.from(jsonDecode(raw) as Map);
    final next=accounts[username];
    if(next==null)throw Exception('Saved account not found. Sign in again.');
    token=next.toString(); activeUsername=username;
    await prefs.setString('api_token',token!); await prefs.setString('active_username',username);
    await get('/api/mobile/me/');
  }

  Future<void> signOut() async {
    try {
      await http.delete(uri('/api/mobile/me/'), headers: headers);
    } catch (_) {}
    token = null;
    if(activeUsername!=null){
      final prefs=await prefsFuture; final raw=prefs.getString('saved_accounts')??'{}';
      try{final accounts=Map<String,dynamic>.from(jsonDecode(raw) as Map);accounts.remove(activeUsername);await prefs.setString('saved_accounts',jsonEncode(accounts));}catch(_){}
    }
    activeUsername=null;
    await (await prefsFuture).remove('api_token');
    await (await prefsFuture).remove('active_username');
  }
}

class ApiException implements Exception {
  const ApiException(this.statusCode, this.message);
  final int statusCode;
  final String message;
  @override
  String toString() => message;
}

String errorText(Object e) => e.toString().replaceFirst('Exception: ', '');
String stamp(dynamic value) {
  try {
    final d = DateTime.parse(value.toString()).toLocal();
    final h = d.hour % 12 == 0 ? 12 : d.hour % 12;
    return '${d.day}/${d.month} $h:${d.minute.toString().padLeft(2, '0')} ${d.hour >= 12 ? 'PM' : 'AM'}';
  } catch (_) {
    return value?.toString() ?? '';
  }
}

String initials(String value) =>
    value.isEmpty ? '?' : value.trim()[0].toUpperCase();

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key, required this.api, required this.onSignedIn, this.onCancel});
  final CampusApi api;
  final VoidCallback onSignedIn;
  final VoidCallback? onCancel;
  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final u = TextEditingController(), p = TextEditingController();
  bool busy = false, hide = true;
  String? error;
  Future<void> login() async {
    if (u.text.trim().isEmpty || p.text.isEmpty) return;
    setState(() => busy = true);
    try {
      await widget.api.signIn(u.text.trim(), p.text);
      if (mounted) widget.onSignedIn();
    } catch (e) {
      if (mounted) setState(() => error = errorText(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> configureServer() async {
    final controller = TextEditingController(text: widget.api.base);
    final value = await showDialog<String>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Backend server'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.url,
          decoration: const InputDecoration(
            labelText: 'Server URL',
            hintText: 'http://192.168.1.10:5000',
            helperText: 'Use your computer’s Wi-Fi address.',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(dialogContext),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () =>
                Navigator.pop(dialogContext, controller.text.trim()),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    if (value == null || !mounted) return;
    final parsed = Uri.tryParse(value);
    if (parsed == null ||
        !['http', 'https'].contains(parsed.scheme) ||
        parsed.host.isEmpty ||
        parsed.userInfo.isNotEmpty ||
        parsed.hasQuery ||
        parsed.hasFragment ||
        (parsed.path.isNotEmpty && parsed.path != '/')) {
      setState(
        () => error =
            'Enter a valid server URL, such as http://192.168.1.10:5000',
      );
      return;
    }
    widget.api.serverOverride = value.replaceFirst(RegExp(r'/+$'), '');
    await (await widget.api.prefsFuture).setString(
      'server_url',
      widget.api.base,
    );
    if (mounted) setState(() => error = null);
  }

  @override
  void dispose() {
    u.dispose();
    p.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext c) => Scaffold(
    body: Center(
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 430),
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(26),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  const Icon(Icons.school_rounded, size: 58, color: brand),
                  const SizedBox(height: 12),
                  Text(
                    'Campus Times',
                    textAlign: TextAlign.center,
                    style: Theme.of(c).textTheme.headlineMedium
                        ?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  const Text(
                    'Your campus. Your community.',
                    textAlign: TextAlign.center,
                  ),
                  if(widget.onCancel!=null) Align(alignment:Alignment.centerLeft,child:TextButton.icon(onPressed:widget.onCancel,icon:const Icon(Icons.arrow_back),label:const Text('Back to current account'))),
                  TextButton.icon(
                    onPressed: busy ? null : configureServer,
                    icon: const Icon(Icons.dns_outlined),
                    label: const Text('Backend server'),
                  ),
                  const SizedBox(height: 28),
                  TextField(
                    controller: u,
                    autofillHints: const [AutofillHints.username],
                    decoration: const InputDecoration(
                      labelText: 'Username',
                      prefixIcon: Icon(Icons.person_outline),
                      border: OutlineInputBorder(),
                    ),
                  ),
                  const SizedBox(height: 12),
                  TextField(
                    controller: p,
                    obscureText: hide,
                    onSubmitted: (_) => login(),
                    decoration: InputDecoration(
                      labelText: 'Password',
                      prefixIcon: const Icon(Icons.lock_outline),
                      suffixIcon: IconButton(
                        icon: Icon(
                          hide ? Icons.visibility : Icons.visibility_off,
                        ),
                        onPressed: () => setState(() => hide = !hide),
                      ),
                      border: const OutlineInputBorder(),
                    ),
                  ),
                  if (error != null)
                    Padding(
                      padding: const EdgeInsets.only(top: 12),
                      child: Text(
                        error!,
                        style: const TextStyle(color: Colors.red),
                      ),
                    ),
                  const SizedBox(height: 20),
                  FilledButton(
                    onPressed: busy ? null : login,
                    child: Padding(
                      padding: const EdgeInsets.all(12),
                      child: Text(busy ? 'Signing in…' : 'Sign in'),
                    ),
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton(
                    onPressed: busy
                        ? null
                        : () async {
                            final created = await Navigator.push<bool>(
                              context,
                              MaterialPageRoute(
                                builder: (_) => SignUpScreen(api: widget.api),
                              ),
                            );
                            if (created == true && mounted) widget.onSignedIn();
                          },
                    child: const Text('Create a new account'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    ),
  );
}

class SignUpScreen extends StatefulWidget {
  const SignUpScreen({super.key, required this.api});
  final CampusApi api;
  @override
  State<SignUpScreen> createState() => _SignUpScreenState();
}

class _SignUpScreenState extends State<SignUpScreen> {
  final form = GlobalKey<FormState>();
  final first = TextEditingController(),
      last = TextEditingController(),
      username = TextEditingController(),
      email = TextEditingController(),
      password = TextEditingController(),
      confirm = TextEditingController();
  bool busy = false, hide = true;
  String? error;
  @override
  void dispose() {
    for (final c in [first, last, username, email, password, confirm]) {
      c.dispose();
    }
    super.dispose();
  }

  Future<void> submit() async {
    if (!(form.currentState?.validate() ?? false)) return;
    setState(() {
      busy = true;
      error = null;
    });
    try {
      await widget.api.signUp({
        'first_name': first.text.trim(),
        'last_name': last.text.trim(),
        'username': username.text.trim(),
        'email': email.text.trim(),
        'password': password.text,
        'confirm_password': confirm.text,
      });
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) setState(() => error = errorText(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Create account')),
    body: Center(
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 480),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Form(
            key: form,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'Join Campus Times',
                  style: TextStyle(fontSize: 25, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 20),
                TextFormField(
                  controller: first,
                  textCapitalization: TextCapitalization.words,
                  decoration: const InputDecoration(
                    labelText: 'First name',
                    border: OutlineInputBorder(),
                  ),
                  validator: (v) => v == null || v.trim().isEmpty
                      ? 'Enter your first name'
                      : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: last,
                  textCapitalization: TextCapitalization.words,
                  decoration: const InputDecoration(
                    labelText: 'Last name',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: username,
                  autofillHints: const [AutofillHints.newUsername],
                  decoration: const InputDecoration(
                    labelText: 'Username',
                    border: OutlineInputBorder(),
                  ),
                  validator: (v) => v == null || v.trim().length < 3
                      ? 'Enter at least 3 characters'
                      : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: email,
                  keyboardType: TextInputType.emailAddress,
                  autofillHints: const [AutofillHints.email],
                  decoration: const InputDecoration(
                    labelText: 'Email',
                    border: OutlineInputBorder(),
                  ),
                  validator: (v) =>
                      v == null ||
                          !RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
                              .hasMatch(v.trim())
                      ? 'Enter a valid email'
                      : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: password,
                  obscureText: hide,
                  decoration: InputDecoration(
                    labelText: 'Password',
                    border: const OutlineInputBorder(),
                    suffixIcon: IconButton(
                      onPressed: () => setState(() => hide = !hide),
                      icon: Icon(
                        hide ? Icons.visibility : Icons.visibility_off,
                      ),
                    ),
                  ),
                  validator: (v) => v == null || v.length < 8
                      ? 'Use at least 8 characters'
                      : null,
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: confirm,
                  obscureText: hide,
                  decoration: const InputDecoration(
                    labelText: 'Confirm password',
                    border: OutlineInputBorder(),
                  ),
                  validator: (v) =>
                      v != password.text ? 'Passwords do not match' : null,
                ),
                if (error != null)
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    child: Text(
                      error!,
                      style: const TextStyle(color: Colors.red),
                    ),
                  ),
                const SizedBox(height: 18),
                FilledButton(
                  onPressed: busy ? null : submit,
                  child: Padding(
                    padding: const EdgeInsets.all(12),
                    child: Text(busy ? 'Creating account…' : 'Create account'),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    ),
  );
}

class HomeShell extends StatefulWidget {
  const HomeShell({
    super.key,
    required this.api,
    required this.onSignOut,
    required this.dark,
    required this.onTheme,
    required this.onAddAccount,
    required this.onSwitchAccount,
  });
  final CampusApi api;
  final VoidCallback onSignOut;
  final bool dark;
  final ValueChanged<bool> onTheme;
  final VoidCallback onAddAccount;
  final VoidCallback onSwitchAccount;
  @override
  State<HomeShell> createState() => _HomeShellState();
}

class _HomeShellState extends State<HomeShell> {
  int tab = 0;
  int unread = 0;
  Timer? timer;
  @override
  void initState() {
    super.initState();
    loadBadge();
    timer = Timer.periodic(const Duration(seconds: 25), (_) => loadBadge());
  }

  Future<void> loadBadge() async {
    try {
      final d = await widget.api.get('/api/mobile/notifications/');
      if (mounted) setState(() => unread = d['unread'] ?? 0);
    } catch (_) {}
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext c) {
    final pages = [
      FeedScreen(api: widget.api),
      ContactsScreen(api: widget.api),
      GroupsScreen(api: widget.api),
      NewsShortsScreen(api: widget.api),
    ];
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Campus Times',
          style: TextStyle(fontWeight: FontWeight.w800, letterSpacing: -.4),
        ),
        actions: [
          IconButton(
            tooltip: 'Complaints',
            onPressed: () => Navigator.push(
              c,
              MaterialPageRoute(
                builder: (_) => ComplaintScreen(api: widget.api),
              ),
            ),
            icon: const Icon(Icons.report_problem_outlined),
          ),
          IconButton(
            tooltip: 'Alerts',
            onPressed: () => Navigator.push(
              c,
              MaterialPageRoute(
                builder: (_) => NotificationsScreen(api: widget.api, onRead: loadBadge),
              ),
            ),
            icon: Badge(
              isLabelVisible: unread > 0,
              label: Text(unread > 9 ? '9+' : '$unread'),
              child: const Icon(Icons.notifications_outlined),
            ),
          ),
          IconButton(
            tooltip: 'Search',
            onPressed: () => Navigator.push(
              c,
              MaterialPageRoute(builder: (_) => SearchScreen(api: widget.api)),
            ),
            icon: const Icon(Icons.search),
          ),
          PopupMenuButton<String>(
            onSelected: (v) async {
              if (v == 'profile')
                Navigator.push(
                  c,
                  MaterialPageRoute(
                    builder: (_) =>
                        ProfileScreen(api: widget.api, username: ''),
                  ),
                );
              if (v == 'theme') widget.onTheme(!widget.dark);
              if (v == 'add_account') widget.onAddAccount();
              if (v == 'switch_account') {
                final names=await widget.api.accountNames();
                final others=names.where((n)=>n!=widget.api.activeUsername).toList();
                if(others.isEmpty){if(c.mounted)snack(c,'No other saved account yet. Choose Add account first.');return;}
                final selected=await showDialog<String>(context:c,builder:(ctx)=>SimpleDialog(title:const Text('Switch account'),children:[for(final name in others)SimpleDialogOption(onPressed:()=>Navigator.pop(ctx,name),child:Text('@$name'))]));
                if(selected!=null){try{await widget.api.switchAccount(selected);widget.onSwitchAccount();}catch(e){if(c.mounted)snack(c,errorText(e));}}
              }
              if (v == 'logout') {
                await widget.api.signOut();
                widget.onSignOut();
              }
            },
            itemBuilder: (_) => const [
              PopupMenuItem(value: 'profile', child: Text('My profile')),
              PopupMenuItem(value: 'add_account', child: Text('Add account')),
              PopupMenuItem(value: 'switch_account', child: Text('Switch account')),
              PopupMenuItem(value: 'logout', child: Text('Sign out')),
            ],
          ),
        ],
      ),
      body: IndexedStack(index: tab, children: pages),
      bottomNavigationBar: NavigationBar(
        selectedIndex: tab,
        onDestinationSelected: (i) => setState(() => tab = i),
        destinations: [
          const NavigationDestination(
            icon: Icon(Icons.dynamic_feed_outlined),
            selectedIcon: Icon(Icons.dynamic_feed),
            label: 'Feed',
          ),
          const NavigationDestination(
            icon: Icon(Icons.forum_outlined),
            selectedIcon: Icon(Icons.forum),
            label: 'Chats',
          ),
          const NavigationDestination(
            icon: Icon(Icons.groups_outlined),
            selectedIcon: Icon(Icons.groups),
            label: 'Groups',
          ),
          const NavigationDestination(
            icon: Icon(Icons.play_circle_outline),
            selectedIcon: Icon(Icons.play_circle),
            label: 'News Shorts',
          ),
        ],
      ),
    );
  }
}

class NewsShortsScreen extends StatefulWidget {
  const NewsShortsScreen({super.key, required this.api});
  final CampusApi api;
  @override
  State<NewsShortsScreen> createState() => _NewsShortsScreenState();
}

class _NewsShortsScreenState extends State<NewsShortsScreen> {
  List shorts = [];
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    loadShorts();
  }

  Future<void> loadShorts() async {
    try {
      final result = await widget.api.get('/api/mobile/news-shorts/');
      if (mounted) setState(() { shorts = result['shorts'] ?? []; loading = false; error = null; });
    } catch (e) {
      if (mounted) setState(() { loading = false; error = '$e'; });
    }
  }

  @override
  Widget build(BuildContext context) => RefreshIndicator(
    onRefresh: loadShorts,
    child: loading
        ? const Center(child: CircularProgressIndicator())
        : error != null
            ? ListView(children: [const SizedBox(height: 100), Center(child: Text(error!))])
            : shorts.isEmpty
                ? ListView(children: const [SizedBox(height: 100), Center(child: Text('No news shorts are available yet.'))])
                : ListView.builder(
                    padding: const EdgeInsets.all(12),
                    itemCount: shorts.length,
                    itemBuilder: (context, index) => NewsShortClip(item: shorts[index]),
                  ),
  );
}

class NewsShortClip extends StatefulWidget {
  const NewsShortClip({super.key, required this.item});
  final dynamic item;
  @override
  State<NewsShortClip> createState() => _NewsShortClipState();
}

class _NewsShortClipState extends State<NewsShortClip> {
  VideoPlayerController? controller;
  bool failed = false;
  @override
  void initState() {
    super.initState();
    final url = (widget.item['video'] ?? '').toString();
    if (url.isEmpty) { failed = true; return; }
    controller = VideoPlayerController.networkUrl(Uri.parse(url))
      ..initialize().then((_) { if (mounted) setState(() {}); }).catchError((_) { if (mounted) setState(() => failed = true); });
  }
  @override
  void dispose() { controller?.dispose(); super.dispose(); }
  @override
  Widget build(BuildContext context) => Card(
    clipBehavior: Clip.antiAlias,
    margin: const EdgeInsets.only(bottom: 16),
    child: Column(crossAxisAlignment: CrossAxisAlignment.stretch, children: [
      if (failed) const SizedBox(height: 220, child: Center(child: Text('This video could not be loaded.')))
      else if (controller?.value.isInitialized == true)
        AspectRatio(aspectRatio: controller!.value.aspectRatio, child: Stack(alignment: Alignment.center, children: [
          VideoPlayer(controller!),
          IconButton.filledTonal(
            onPressed: () => setState(() => controller!.value.isPlaying ? controller!.pause() : controller!.play()),
            icon: Icon(controller!.value.isPlaying ? Icons.pause : Icons.play_arrow),
          ),
        ]))
      else const SizedBox(height: 220, child: Center(child: CircularProgressIndicator())),
      ListTile(
        leading: const CircleAvatar(child: Icon(Icons.person_outline)),
        title: Text('@${widget.item['username'] ?? 'campus'}'),
        subtitle: Text((widget.item['caption'] ?? '').toString()),
      ),
    ]),
  );
}

class FeedScreen extends StatefulWidget {
  const FeedScreen({super.key, required this.api});
  final CampusApi api;
  @override
  State<FeedScreen> createState() => _FeedScreenState();
}

class _FeedScreenState extends State<FeedScreen> {
  List posts = [];
  bool loading = true, publishing = false;
  String? error;
  final text = TextEditingController();
  PickedUpload? file;
  @override
  void initState() {
    super.initState();
    refresh();
  }

  Future<void> refresh() async {
    try {
      final d = await widget.api.get('/api/mobile/feed/');
      if (mounted) setState(() => posts = d['posts'] ?? []);
      error = null;
    } catch (e) {
      error = errorText(e);
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> publish() async {
    if (publishing || (text.text.trim().isEmpty && file == null)) return;
    setState(() => publishing = true);
    try {
      await widget.api.upload(
        '/api/mobile/feed/',
        fields: {'body': text.text.trim(), 'title': 'Campus update'},
        file: file,
      );
      text.clear();
      file = null;
      await refresh();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => publishing = false);
    }
  }

  Future<void> like(dynamic p) async {
    try {
      await widget.api.post('/api/mobile/feed/${p['id']}/like/', {});
      await refresh();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> share(dynamic p) async {
    try {
      await widget.api.post('/api/mobile/feed/${p['id']}/share/', {});
      await refresh();
      if (mounted) snack(context, 'Post shared to your feed.');
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> postActions(dynamic p, String action) async {
    final url='/api/mobile/feed/${p['id']}/';
    try {
      if(action=='delete'){
        final yes=await showDialog<bool>(context:context,builder:(ctx)=>AlertDialog(title:const Text('Delete post?'),content:const Text('This will remove the post and its comments.'),actions:[TextButton(onPressed:()=>Navigator.pop(ctx,false),child:const Text('Cancel')),FilledButton(onPressed:()=>Navigator.pop(ctx,true),child:const Text('Delete'))]));
        if(yes!=true)return; await widget.api.delete(url);
      } else {
        final edit=TextEditingController(text:(p['body']??'').toString());
        final body=await showDialog<String>(context:context,builder:(ctx)=>AlertDialog(title:const Text('Edit post'),content:TextField(controller:edit,maxLines:5,autofocus:true),actions:[TextButton(onPressed:()=>Navigator.pop(ctx),child:const Text('Cancel')),FilledButton(onPressed:()=>Navigator.pop(ctx,edit.text.trim()),child:const Text('Save'))]));
        edit.dispose(); if(body==null)return; await widget.api.patch(url,{'body':body});
      }
      await refresh();
    } catch(e){if(mounted)snack(context,errorText(e));}
  }

  Future<void> comments(dynamic p) async {
    await showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (_) => CommentsSheet(api: widget.api, post: p),
    );
    await refresh();
  }

  @override
  void dispose() {
    text.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext c) => RefreshIndicator(
    onRefresh: refresh,
    child: ListView(
      padding: const EdgeInsets.fromLTRB(14, 8, 14, 24),
      children: [
        StatusPanel(api: widget.api),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(14),
            child: Column(
              children: [
                Row(
                  children: [
                    const CircleAvatar(
                      backgroundColor: Color(0xffeeeeee),
                      child: Icon(Icons.edit, color: brand),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: TextField(
                        controller: text,
                        minLines: 2,
                        maxLines: 5,
                        decoration: const InputDecoration(
                          hintText: 'What is happening on campus?',
                          border: InputBorder.none,
                        ),
                      ),
                    ),
                  ],
                ),
                if (file != null)
                  ListTile(
                    dense: true,
                    leading: const Icon(Icons.attach_file),
                    title: Text(
                      file!.name,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    trailing: IconButton(
                      onPressed: () => setState(() => file = null),
                      icon: const Icon(Icons.close),
                    ),
                  ),
                const Divider(),
                Wrap(
                  spacing: 6,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    TextButton.icon(
                      onPressed: publishing
                          ? null
                          : () async {
                              final f = await chooseSocialMedia(context);
                              if (f != null && mounted)
                                setState(() => file = f);
                            },
                      icon: const Icon(Icons.photo_library_outlined),
                      label: const Text('Photo / video'),
                    ),
                    IconButton(
                      tooltip: 'Take selfie',
                      onPressed: publishing
                          ? null
                          : () async {
                              final f = await chooseSocialMedia(
                                context,
                                source: 'selfie',
                              );
                              if (f != null && mounted)
                                setState(() => file = f);
                            },
                      icon: const Icon(Icons.camera_alt_outlined),
                    ),
                    FilledButton.icon(
                      onPressed: publishing ? null : publish,
                      icon: const Icon(Icons.send, size: 17),
                      label: Text(publishing ? 'Posting…' : 'Post'),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ),
        const SizedBox(height: 8),
        if (loading)
          const Center(
            child: Padding(
              padding: EdgeInsets.all(32),
              child: CircularProgressIndicator(),
            ),
          ),
        if (error != null && !loading)
          Card(
            child: ListTile(
              leading: const Icon(Icons.cloud_off),
              title: Text(error!),
              trailing: TextButton(
                onPressed: refresh,
                child: const Text('Retry'),
              ),
            ),
          ),
        if (!loading && posts.isEmpty && error == null)
          const Padding(
            padding: EdgeInsets.all(35),
            child: Text(
              'No posts yet. Be the first to share something!',
              textAlign: TextAlign.center,
            ),
          ),
        ...posts.map(
          (p) => PostCard(
            post: p,
            onLike: () => like(p),
            onComments: () => comments(p),
            onShare: () => share(p),
            onEdit: p['is_mine']==true ? () => postActions(p,'edit') : null,
            onDelete: p['is_mine']==true ? () => postActions(p,'delete') : null,
            onProfile: () => Navigator.push(
              c,
              MaterialPageRoute(
                builder: (_) =>
                    ProfileScreen(api: widget.api, username: p['username']),
              ),
            ),
          ),
        ),
      ],
    ),
  );
}

class PostCard extends StatelessWidget {
  const PostCard({
    super.key,
    required this.post,
    required this.onLike,
    required this.onComments,
    required this.onProfile,
    this.onShare,
    this.onEdit,
    this.onDelete,
  });
  final dynamic post;
  final VoidCallback onLike, onComments, onProfile;
  final VoidCallback? onShare;
  final VoidCallback? onEdit;
  final VoidCallback? onDelete;
  @override
  Widget build(BuildContext c) {
    final a = post['author'] ?? {};
    final avatar = a['avatar'] ?? '';
    final attachment = post['attachment'] ?? '';
    return Card(
      clipBehavior: Clip.antiAlias,
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                GestureDetector(
                  onTap: onProfile,
                  child: CircleAvatar(
                    backgroundImage: avatar.toString().isNotEmpty
                        ? NetworkImage(avatar)
                        : null,
                    child: avatar.toString().isEmpty
                        ? Text(initials(post['username'] ?? ''))
                        : null,
                  ),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: InkWell(
                    onTap: onProfile,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          post['author']?['full_name'] ??
                              '@${post['username']}',
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        Text(
                          '@${post['username']} · ${stamp(post['created_at'])}',
                          style: Theme.of(c).textTheme.bodySmall,
                        ),
                      ],
                    ),
                  ),
                ),
                if (onEdit != null || onDelete != null)
                  PopupMenuButton<String>(onSelected:(v){if(v=='edit'){onEdit?.call();}else{onDelete?.call();}},itemBuilder:(_)=>[if(onEdit!=null)const PopupMenuItem(value:'edit',child:Text('Edit post')),if(onDelete!=null)const PopupMenuItem(value:'delete',child:Text('Delete post'))])
                else const Icon(Icons.more_horiz),
              ],
            ),
            if ((post['title'] ?? '').toString().isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: Text(
                  post['title'],
                  style: const TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            if ((post['body'] ?? '').toString().isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 8),
                child: Text(
                  post['body'],
                  style: const TextStyle(fontSize: 15, height: 1.4),
                ),
              ),
            if (attachment.toString().isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(top: 12),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: SocialMediaView(url: attachment),
                ),
              ),
            const Divider(height: 22),
            Row(
              children: [
                TextButton.icon(
                  onPressed: onLike,
                  icon: Icon(
                    post['liked'] == true
                        ? Icons.favorite
                        : Icons.favorite_border,
                    color: post['liked'] == true ? Colors.pink : null,
                  ),
                  label: Text('${post['likes'] ?? 0}'),
                ),
                TextButton.icon(
                  onPressed: onComments,
                  icon: const Icon(Icons.mode_comment_outlined),
                  label: Text('${post['comments_count'] ?? 0} comments'),
                ),
                if (onShare != null)
                  IconButton(
                    tooltip: 'Share post',
                    onPressed: onShare,
                    icon: const Icon(Icons.share_outlined),
                  ),
                const Spacer(),
                Text(
                  post['category'] ?? 'General',
                  style: Theme.of(c).textTheme.labelSmall,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

void snack(BuildContext c, String s) =>
    ScaffoldMessenger.of(c).showSnackBar(SnackBar(content: Text(s)));
Future<void> launchExternal(String url) async {
  final uri = Uri.tryParse(url);
  if (uri != null) await launchUrl(uri, mode: LaunchMode.externalApplication);
}

class CommentsSheet extends StatefulWidget {
  const CommentsSheet({super.key, required this.api, required this.post});
  final CampusApi api;
  final dynamic post;
  @override
  State<CommentsSheet> createState() => _CommentsSheetState();
}

class _CommentsSheetState extends State<CommentsSheet> {
  List comments = [];
  Map? replyTo;
  bool loading = true, sending = false;
  final text = TextEditingController();
  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    try {
      final d = await widget.api.get(
        '/api/mobile/feed/${widget.post['id']}/comments/',
      );
      if (mounted) setState(() => comments = d['comments'] ?? []);
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> send() async {
    if (text.text.trim().isEmpty) return;
    setState(() => sending = true);
    try {
      await widget.api.post('/api/mobile/feed/${widget.post['id']}/comments/', {
        'body': text.text.trim(),
        if (replyTo != null) 'parent_id': replyTo!['id'],
      });
      text.clear();
      replyTo = null;
      await load();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  Future<void> commentAction(Map comment, String action) async {
    final path='/api/mobile/feed/${widget.post['id']}/comments/${comment['id']}/';
    try {
      if(action=='reply'){setState(()=>replyTo=comment);return;}
      if(action=='delete'){
        await widget.api.delete(path);
      } else {
        final edit=TextEditingController(text:(comment['body']??'').toString());
        final body=await showDialog<String>(context:context,builder:(ctx)=>AlertDialog(title:const Text('Edit comment'),content:TextField(controller:edit,maxLines:4),actions:[TextButton(onPressed:()=>Navigator.pop(ctx),child:const Text('Cancel')),FilledButton(onPressed:()=>Navigator.pop(ctx,edit.text.trim()),child:const Text('Save'))]));
        edit.dispose(); if(body==null)return; await widget.api.patch(path,{'body':body});
      }
      await load();
    }catch(e){if(mounted)snack(context,errorText(e));}
  }

  @override
  void dispose() {
    text.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext c) => Padding(
    padding: EdgeInsets.only(bottom: MediaQuery.of(c).viewInsets.bottom),
    child: SizedBox(
      height: MediaQuery.of(c).size.height * .72,
      child: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16),
            child: Text('Comments', style: Theme.of(c).textTheme.titleLarge),
          ),
          Expanded(
            child: loading
                ? const Center(child: CircularProgressIndicator())
                : comments.isEmpty
                ? const Center(child: Text('No comments yet'))
                : ListView.builder(
                    itemCount: comments.length,
                    itemBuilder: (_, i) {
                      final x = comments[i];
                      return ListTile(
                        leading: CircleAvatar(
                          child: Text(initials(x['username'] ?? '')),
                        ),
                        title: Text(
                          x['username'],
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Column(crossAxisAlignment:CrossAxisAlignment.start,children:[if((x['parent_username']??'').toString().isNotEmpty)Text('Replying to @${x['parent_username']}',style:Theme.of(c).textTheme.labelSmall),Text(x['body'])]),
                        trailing: PopupMenuButton<String>(onSelected:(v)=>commentAction(Map<String,dynamic>.from(x),v),itemBuilder:(_)=>[
                          const PopupMenuItem(value:'reply',child:Text('Reply')),
                          if(x['is_mine']==true) const PopupMenuItem(value:'edit',child:Text('Edit')),
                          if(x['is_mine']==true||widget.post['is_mine']==true) const PopupMenuItem(value:'delete',child:Text('Delete')),
                        ]),
                      );
                    },
                  ),
          ),
          SafeArea(
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Column(mainAxisSize:MainAxisSize.min,children:[
                if(replyTo!=null) ListTile(dense:true,title:Text('Replying to @${replyTo!['username']}'),subtitle:Text('${replyTo!['body']}',maxLines:1,overflow:TextOverflow.ellipsis),trailing:IconButton(onPressed:()=>setState(()=>replyTo=null),icon:const Icon(Icons.close))),
                Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: text,
                      decoration: const InputDecoration(
                        hintText: 'Write a comment…',
                        border: OutlineInputBorder(),
                      ),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton.filled(
                    onPressed: sending ? null : send,
                    icon: const Icon(Icons.send),
                  ),
                ],
                ),
              ]),
            ),
          ),
        ],
      ),
    ),
  );
}

class ContactsScreen extends StatefulWidget {
  const ContactsScreen({super.key, required this.api});
  final CampusApi api;
  @override
  State<ContactsScreen> createState() => _ContactsScreenState();
}

class _ContactsScreenState extends State<ContactsScreen> {
  List people = [];
  bool loading = true;
  String q = '';
  String? error;
  Timer? debounce;
  int requestVersion = 0;

  @override
  void initState() {
    super.initState();
    load();
  }

  void onQueryChanged(String value) {
    q = value;
    debounce?.cancel();
    debounce = Timer(const Duration(milliseconds: 300), load);
  }

  Future<void> load() async {
    final version = ++requestVersion;
    if (mounted)
      setState(() {
        loading = true;
        error = null;
      });
    try {
      final d = await widget.api.get(
        '/api/mobile/contacts/?q=${Uri.encodeQueryComponent(q)}',
      );
      if (mounted && version == requestVersion)
        setState(() => people = d['people'] ?? []);
    } catch (e) {
      if (mounted && version == requestVersion)
        setState(() => error = errorText(e));
    } finally {
      if (mounted && version == requestVersion) setState(() => loading = false);
    }
  }

  @override
  void dispose() {
    debounce?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext c) => Column(
    children: [
      StatusPanel(api: widget.api),
      Padding(
        padding: const EdgeInsets.fromLTRB(14, 8, 14, 10),
        child: TextField(
          onChanged: onQueryChanged,
          decoration: InputDecoration(
            hintText: 'Search people',
            prefixIcon: const Icon(Icons.search),
            filled: true,
            fillColor: Colors.white,
            border: OutlineInputBorder(
              borderRadius: BorderRadius.circular(16),
              borderSide: BorderSide.none,
            ),
          ),
        ),
      ),
      if (error != null)
        ListTile(
          title: Text(error!),
          trailing: TextButton(onPressed: load, child: const Text('Retry')),
        ),
      Expanded(
        child: loading
            ? const Center(child: CircularProgressIndicator())
            : RefreshIndicator(
                onRefresh: load,
                child: people.isEmpty
                    ? ListView(
                        children: [
                          SizedBox(height: 180),
                          Center(child: Text('No people found')),
                        ],
                      )
                    : ListView.separated(
                        itemCount: people.length,
                        separatorBuilder: (_, __) =>
                            const Divider(height: 1, indent: 72),
                        itemBuilder: (_, i) {
                          final p = people[i];
                          final av = p['avatar'] ?? '';
                          return ListTile(
                            leading: Stack(
                              children: [
                                CircleAvatar(
                                  backgroundImage: av.toString().isNotEmpty
                                      ? NetworkImage(av)
                                      : null,
                                  child: av.toString().isEmpty
                                      ? Text(initials(p['username']))
                                      : null,
                                ),
                                if (p['online'] == true)
                                  const Positioned(
                                    right: 0,
                                    bottom: 0,
                                    child: CircleAvatar(
                                      radius: 5,
                                      backgroundColor: Colors.green,
                                    ),
                                  ),
                              ],
                            ),
                            title: Text(
                              p['full_name'] ?? p['username'],
                              style: const TextStyle(
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                            subtitle: Text(
                              p['last_message']?.toString().isNotEmpty == true
                                  ? p['last_message']
                                  : 'Tap to start chatting',
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            trailing: (p['unread'] ?? 0) > 0
                                ? Badge(label: Text('${p['unread']}'))
                                : const Icon(Icons.chevron_right),
                            onTap: () => Navigator.push(
                              c,
                              MaterialPageRoute(
                                builder: (_) =>
                                    ChatScreen(api: widget.api, person: p),
                              ),
                            ).then((_) => load()),
                          );
                        },
                      ),
              ),
      ),
    ],
  );
}

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key, required this.api, required this.person});
  final CampusApi api;
  final dynamic person;
  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final input = TextEditingController();
  final scroll = ScrollController();
  final recorder = AudioRecorder();
  bool recording = false;
  Map? currentPerson;
  Map? replyTo;
  List messages = [];
  bool loading = true, sending = false, online = false, typing = false;
  String lastSeen = '';
  String? error;
  Timer? timer;
  Timer? typingTimer;
  String get path =>
      '/api/mobile/chat/${Uri.encodeComponent(widget.person['username'])}/';
  @override
  void initState() {
    super.initState();
    load();
    timer = Timer.periodic(
      const Duration(seconds: 4),
      (_) => load(silent: true),
    );
  }

  Future<void> load({bool silent = false}) async {
    try {
      final d = await widget.api.get(path);
      if (mounted)
        setState(() {
          currentPerson = d['person'];
          messages = d['messages'] ?? [];
          online = d['online'] == true;
          typing = d['typing'] == true;
          lastSeen = (d['last_seen'] ?? '').toString();
          error = null;
          loading = false;
        });
    } catch (e) {
      if (mounted)
        setState(() {
          error = errorText(e);
          loading = false;
        });
    }
  }

  Future<void> send() async {
    final t = input.text.trim();
    if ((t.isEmpty) || sending) return;
    input.clear();
    setState(() => sending = true);
    try {
      await widget.api.post(path, {'message': t, if (replyTo != null) 'reply_to_id': replyTo!['id']});
      replyTo = null;
      await load();
    } catch (e) {
      if (mounted) {
        input.text = t;
        snack(context, errorText(e));
      }
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  Future<void> messageActions(Map m) async {
    final action = await showModalBottomSheet<String>(context: context, builder: (sheet) => SafeArea(child: Wrap(children: [
      ListTile(leading: const Icon(Icons.reply), title: const Text('Reply'), onTap: () => Navigator.pop(sheet, 'reply')),
      if (m['is_me'] == true && (m['attachment'] ?? '').toString().isEmpty && m['message'] != 'This message was deleted')
        ListTile(leading: const Icon(Icons.edit), title: const Text('Edit message'), onTap: () => Navigator.pop(sheet, 'edit')),
      if (m['is_me'] == true) ListTile(leading: const Icon(Icons.delete_outline), title: const Text('Delete message'), onTap: () => Navigator.pop(sheet, 'delete')),
    ])));
    if (!mounted || action == null) return;
    if (action == 'reply') { setState(() => replyTo = m); return; }
    final url = '$path${m['id']}/';
    try {
      if (action == 'delete') await widget.api.delete(url);
      if (action == 'edit') {
        final edit = TextEditingController(text: (m['message'] ?? '').toString());
        final value = await showDialog<String>(context: context, builder: (ctx) => AlertDialog(title: const Text('Edit message'), content: TextField(controller: edit, autofocus: true), actions: [TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(ctx, edit.text.trim()), child: const Text('Save'))]));
        edit.dispose();
        if (value == null || value.isEmpty) return;
        await widget.api.patch(url, {'message': value});
      }
      await load();
    } catch (e) { if (mounted) snack(context, errorText(e)); }
  }

  Future<void> clearChat() async {
    final ok = await showDialog<bool>(context: context, builder: (ctx) => AlertDialog(title: const Text('Delete chat from your inbox?'), content: const Text('This hides the conversation only for your account.'), actions: [TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')), FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Delete chat'))]));
    if (ok != true) return;
    try { await widget.api.delete('${path}clear/'); if (mounted) Navigator.pop(context); }
    catch (e) { if (mounted) snack(context, errorText(e)); }
  }

  Future<void> sendMedia(
    PickedUpload? media, {
    bool photoEdit = false,
    bool videoEdit = false,
  }) async {
    if (media == null || !mounted || sending) return;
    if (media.bytes.length > 25 * 1024 * 1024) {
      snack(context, 'Maximum file size is 25 MB.');
      return;
    }
    if (photoEdit) {
      media = await ChatMediaTools.editPhoto(context, media);
      if (media == null || !mounted) return;
    }
    if (videoEdit) {
      try {
        media = await ChatMediaTools.editVideo(context, widget.api, media);
      } catch (e) {
        if (mounted) snack(context, errorText(e));
        return;
      }
      if (media == null || !mounted) return;
    }
    setState(() => sending = true);
    try {
      await widget.api.upload(path, file: media);
      await load();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  Future<void> captureMedia(bool video) async {
    try {
      await sendMedia(
        await ChatMediaTools.capture(video: video),
        photoEdit: !video,
        videoEdit: video,
      );
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> toggleRecording() async {
    try {
      if (recording) {
        final filePath = await recorder.stop();
        if (mounted) setState(() => recording = false);
        if (filePath != null) {
          final data = await XFile(filePath).readAsBytes();
          await sendMedia(
            PickedUpload(
              'voice_${DateTime.now().millisecondsSinceEpoch}.${kIsWeb ? 'webm' : 'm4a'}',
              data,
              kIsWeb ? 'audio/webm' : 'audio/mp4',
            ),
          );
        }
      } else {
        if (!await recorder.hasPermission()) {
          if (mounted) snack(context, 'Microphone permission denied.');
          return;
        }
        final directory = kIsWeb
            ? ''
            : '${(await getTemporaryDirectory()).path}/';
        final extension = kIsWeb ? 'webm' : 'm4a';
        await recorder.start(
          RecordConfig(
            encoder: kIsWeb ? AudioEncoder.opus : AudioEncoder.aacLc,
          ),
          path:
              '${directory}voice_${DateTime.now().millisecondsSinceEpoch}.$extension',
        );
        if (mounted) setState(() => recording = true);
      }
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> shareLocation() async {
    try {
      final link = await ChatMediaTools.currentLocationLink();
      await widget.api.post(path, {'message': link});
      await load();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> mediaMenu() async {
    await showModalBottomSheet<void>(
      context: context,
      builder: (sheetContext) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.photo_camera),
              title: const Text('Take photo'),
              onTap: () {
                Navigator.pop(sheetContext);
                captureMedia(false);
              },
            ),
            ListTile(
              leading: const Icon(Icons.videocam),
              title: const Text('Record video'),
              onTap: () {
                Navigator.pop(sheetContext);
                captureMedia(true);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library_outlined),
              title: const Text('Choose photo from gallery'),
              onTap: () {
                Navigator.pop(sheetContext);
                ChatMediaTools.gallery(video: false).then((f) => sendMedia(f, photoEdit: true));
              },
            ),
            ListTile(
              leading: const Icon(Icons.video_library_outlined),
              title: const Text('Choose video from gallery'),
              onTap: () {
                Navigator.pop(sheetContext);
                ChatMediaTools.gallery(video: true).then((f) => sendMedia(f, videoEdit: true));
              },
            ),
            ListTile(
              leading: const Icon(Icons.attach_file),
              title: const Text('Choose file'),
              onTap: () {
                Navigator.pop(sheetContext);
                attach();
              },
            ),
            ListTile(
              leading: const Icon(Icons.location_on),
              title: const Text('Share current location'),
              onTap: () {
                Navigator.pop(sheetContext);
                shareLocation();
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> attach() async {
    final f = await pickUpload();
    if (f == null || !mounted) return;
    setState(() => sending = true);
    try {
      await widget.api.upload(path, file: f);
      await load();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  Future<void> sendPresence(bool active) async {
    try {
      await widget.api.post(
        '/api/mobile/chat/${Uri.encodeComponent(widget.person['username'])}/presence/',
        {'typing': active},
      );
    } catch (_) {}
  }

  void typingChanged(String value) {
    sendPresence(value.isNotEmpty);
    typingTimer?.cancel();
    if (value.isNotEmpty) {
      typingTimer = Timer(
        const Duration(seconds: 5),
        () => sendPresence(false),
      );
    }
  }

  @override
  void dispose() {
    timer?.cancel();
    typingTimer?.cancel();
    recorder.dispose();
    input.dispose();
    scroll.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext c) => Scaffold(
    appBar: AppBar(
      title: Row(
        children: [
          UserAvatar(
            url: (currentPerson ?? widget.person)['avatar'] ?? '',
            username: widget.person['username'],
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(widget.person['full_name'] ?? widget.person['username']),
                Text(
                  typing
                      ? 'typing…'
                      : online
                      ? 'online'
                      : lastSeen.isNotEmpty ? 'last seen ${stamp(lastSeen)}' : 'offline',
                  style: Theme.of(c).textTheme.labelSmall,
                ),
              ],
            ),
          ),
        ],
      ),
      actions: [PopupMenuButton<String>(onSelected: (v) { if (v == 'clear') clearChat(); }, itemBuilder: (_) => const [PopupMenuItem(value: 'clear', child: Text('Delete chat'))])],
    ),
    body: Column(
      children: [
        if (error != null)
          Material(
            color: Colors.red.shade50,
            child: ListTile(
              title: Text(error!),
              trailing: TextButton(onPressed: load, child: const Text('Retry')),
            ),
          ),
        Expanded(
          child: loading
              ? const Center(child: CircularProgressIndicator())
              : messages.isEmpty
              ? const Center(child: Text('No messages yet. Say hello!'))
              : ListView.builder(
                  reverse: true,
                  padding: const EdgeInsets.all(14),
                  itemCount: messages.length,
                  itemBuilder: (_, i) {
                    final m = messages[messages.length - 1 - i];
                    final mine = m['is_me'] == true;
                    final attachment = m['attachment'] ?? '';
                    return Dismissible(
                      key: ValueKey('dm-${m['id']}'),
                      direction: DismissDirection.startToEnd,
                      confirmDismiss: (_) async { setState(() => replyTo = Map<String,dynamic>.from(m)); return false; },
                      child: Align(
                      alignment: mine
                          ? Alignment.centerRight
                          : Alignment.centerLeft,
                      child: Container(
                        constraints: const BoxConstraints(maxWidth: 310),
                        margin: const EdgeInsets.only(bottom: 8),
                        padding: const EdgeInsets.all(11),
                        decoration: BoxDecoration(
                          color: mine ? const Color(0xffe8e8e8) : Colors.white,
                          borderRadius: BorderRadius.circular(17),
                        ),
                        child: GestureDetector(onLongPress: () => messageActions(Map<String,dynamic>.from(m)), child: Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            if (!mine)
                              Align(
                                alignment: Alignment.centerLeft,
                                child: Text(
                                  m['sender'] ?? '',
                                  style: TextStyle(fontSize: 11, color: brand),
                                ),
                              ),
                            if ((m['reply_to'] ?? '').toString().isNotEmpty)
                              Align(alignment: Alignment.centerLeft, child: Text('↳ ${m['reply_to']}', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 11, color: Colors.blueGrey))),
                            if ((m['message'] ?? '').toString().isNotEmpty)
                              Align(
                                alignment: Alignment.centerLeft,
                                child: Text(
                                  m['message'],
                                  style: TextStyle(color: Colors.black87),
                                ),
                              ),
                            if (attachment.toString().isNotEmpty)
                              chatAttachment(attachment.toString(), mine),
                            Text(
                              '${m['edited_at'] != null && m['edited_at'] != '' ? 'edited · ' : ''}${stamp(m['timestamp'])}${m['is_read'] == true ? '  ✓✓' : ''}',
                              style: TextStyle(
                                fontSize: 10,
                                color: Colors.black54,
                              ),
                            ),
                          ],
                        )),
                      ),
                    ));
                  },
                ),
        ),
        SafeArea(
          top: false,
          child: Padding(
            padding: const EdgeInsets.all(10),
            child: Column(mainAxisSize: MainAxisSize.min, children: [
              if (replyTo != null) ListTile(dense: true, title: Text('Replying to ${replyTo!['sender'] ?? 'message'}', maxLines: 1), subtitle: Text('${replyTo!['message'] ?? ''}', maxLines: 1, overflow: TextOverflow.ellipsis), trailing: IconButton(onPressed: () => setState(() => replyTo = null), icon: const Icon(Icons.close))),
              Row(
              children: [
                IconButton(
                  tooltip: "Camera, files and location",
                  onPressed: sending ? null : mediaMenu,
                  icon: const Icon(Icons.add_circle_outline),
                ),
                IconButton(
                  tooltip: recording
                      ? "Stop and send voice note"
                      : "Record voice note",
                  onPressed: sending ? null : toggleRecording,
                  icon: Icon(
                    recording ? Icons.stop_circle : Icons.mic,
                    color: recording ? Colors.red : null,
                  ),
                ),
                Expanded(
                  child: TextField(
                    controller: input,
                    minLines: 1,
                    maxLines: 4,
                    onChanged: typingChanged,
                    onSubmitted: (_) => send(),
                    decoration: InputDecoration(
                      hintText: 'Message',
                      filled: true,
                      fillColor: Colors.white,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(25),
                        borderSide: BorderSide.none,
                      ),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                IconButton.filled(
                  onPressed: sending ? null : send,
                  icon: const Icon(Icons.send),
                ),
              ],
              ),
            ]),
          ),
        ),
      ],
    ),
  );
}

class GroupsScreen extends StatefulWidget {
  const GroupsScreen({super.key, required this.api});
  final CampusApi api;
  @override
  State<GroupsScreen> createState() => _GroupsScreenState();
}

class _GroupsScreenState extends State<GroupsScreen> {
  List groups = [];
  bool loading = true;
  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    try {
      final d = await widget.api.get('/api/mobile/groups/');
      if (mounted) setState(() => groups = d['groups'] ?? []);
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> create() async {
    final made = await showDialog<bool>(
      context: context,
      builder: (_) => CreateGroupDialog(api: widget.api),
    );
    if (made == true) load();
  }

  @override
  Widget build(BuildContext c) => Scaffold(
    backgroundColor: Colors.transparent,
    floatingActionButton: FloatingActionButton.extended(
      onPressed: create,
      icon: const Icon(Icons.group_add),
      label: const Text('New group'),
    ),
    body: loading
        ? const Center(child: CircularProgressIndicator())
        : RefreshIndicator(
            onRefresh: load,
            child: groups.isEmpty
                ? ListView(
                    children: [
                      SizedBox(height: 180),
                      Center(child: Text('No groups yet. Create one!')),
                    ],
                  )
                : ListView.separated(
                    padding: const EdgeInsets.only(bottom: 90),
                    itemCount: groups.length,
                    separatorBuilder: (_, __) =>
                        const Divider(height: 1, indent: 74),
                    itemBuilder: (_, i) {
                      final g = groups[i];
                      return ListTile(
                        leading: const CircleAvatar(
                          backgroundColor: Color(0xffeeeeee),
                          child: Icon(Icons.groups, color: brand),
                        ),
                        title: Text(
                          g['name'],
                          style: const TextStyle(fontWeight: FontWeight.w700),
                        ),
                        subtitle: Text(
                          '${g['member_count']} members · ${g['last_message'] ?? 'Start a conversation'}',
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        onTap: () => Navigator.push(
                          c,
                          MaterialPageRoute(
                            builder: (_) =>
                                GroupChatScreen(api: widget.api, group: g),
                          ),
                        ).then((_) => load()),
                      );
                    },
                  ),
          ),
  );
}

class CreateGroupDialog extends StatefulWidget {
  const CreateGroupDialog({super.key, required this.api});
  final CampusApi api;
  @override
  State<CreateGroupDialog> createState() => _CreateGroupDialogState();
}

class _CreateGroupDialogState extends State<CreateGroupDialog> {
  final name = TextEditingController();
  List people = [];
  final selected = <int>{};
  bool loading = true, busy = false;
  @override
  void initState() {
    super.initState();
    widget.api
        .get('/api/mobile/contacts/')
        .then((d) {
          if (mounted) setState(() => people = d['people'] ?? []);
        })
        .catchError((_) {})
        .whenComplete(() {
          if (mounted) setState(() => loading = false);
        });
  }

  Future<void> save() async {
    if (name.text.trim().isEmpty) return;
    setState(() => busy = true);
    try {
      await widget.api.post('/api/mobile/groups/', {
        'name': name.text.trim(),
        'member_ids': selected.toList(),
      });
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  @override
  void dispose() {
    name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext c) => AlertDialog(
    title: const Text('Create group'),
    content: SizedBox(
      width: 420,
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: name,
            decoration: const InputDecoration(labelText: 'Group name'),
          ),
          const SizedBox(height: 12),
          const Align(
            alignment: Alignment.centerLeft,
            child: Text('Add members'),
          ),
          SizedBox(
            height: 230,
            child: loading
                ? const Center(child: CircularProgressIndicator())
                : ListView(
                    children: people
                        .map(
                          (p) => CheckboxListTile(
                            value: selected.contains(p['id']),
                            title: Text(p['username']),
                            onChanged: (v) {
                              setState(() {
                                if (v == true) {
                                  selected.add(p['id']);
                                } else {
                                  selected.remove(p['id']);
                                }
                              });
                            },
                          ),
                        )
                        .toList(),
                  ),
          ),
        ],
      ),
    ),
    actions: [
      TextButton(
        onPressed: () => Navigator.pop(c, false),
        child: const Text('Cancel'),
      ),
      FilledButton(
        onPressed: busy ? null : save,
        child: Text(busy ? 'Creating…' : 'Create'),
      ),
    ],
  );
}

class GroupChatScreen extends StatefulWidget {
  const GroupChatScreen({super.key, required this.api, required this.group});
  final CampusApi api;
  final dynamic group;
  @override
  State<GroupChatScreen> createState() => _GroupChatScreenState();
}

class _GroupChatScreenState extends State<GroupChatScreen> {
  List messages = [];
  List members = [];
  bool loading = true, sending = false;
  Map? replyTo;
  final input = TextEditingController();
  final recorder = AudioRecorder();
  bool recording = false;
  Timer? timer;
  String get path => '/api/mobile/groups/${widget.group['id']}/';
  @override
  void initState() {
    super.initState();
    load();
    timer = Timer.periodic(const Duration(seconds: 4), (_) => load());
  }

  Future<void> load() async {
    try {
      final d = await widget.api.get(path);
      if (mounted)
        setState(() {
          messages = d['messages'] ?? [];
          members = d['members'] ?? [];
        });
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> send() async {
    final t = input.text.trim();
    if (t.isEmpty || sending) return;
    input.clear();
    setState(() => sending = true);
    try {
      await widget.api.post(path, {'message': t, if (replyTo != null) 'reply_to_id': replyTo!['id']});
      replyTo = null;
      await load();
    } catch (e) {
      input.text = t;
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  Future<void> messageActions(Map m) async {
    final action=await showModalBottomSheet<String>(context:context,builder:(sheet)=>SafeArea(child:Wrap(children:[
      ListTile(leading:const Icon(Icons.reply),title:const Text('Reply'),onTap:()=>Navigator.pop(sheet,'reply')),
      if(m['is_me']==true && (m['attachment']??'').toString().isEmpty && m['message']!='This message was deleted') ListTile(leading:const Icon(Icons.edit),title:const Text('Edit message'),onTap:()=>Navigator.pop(sheet,'edit')),
      if(m['is_me']==true) ListTile(leading:const Icon(Icons.delete_outline),title:const Text('Delete message'),onTap:()=>Navigator.pop(sheet,'delete')),
    ])));
    if(!mounted||action==null)return;
    if(action=='reply'){setState(()=>replyTo=m);return;}
    final url='/api/mobile/groups/${widget.group['id']}/${m['id']}/';
    try{
      if(action=='delete')await widget.api.delete(url);
      if(action=='edit'){
        final edit=TextEditingController(text:(m['message']??'').toString());
        final value=await showDialog<String>(context:context,builder:(ctx)=>AlertDialog(title:const Text('Edit message'),content:TextField(controller:edit,autofocus:true),actions:[TextButton(onPressed:()=>Navigator.pop(ctx),child:const Text('Cancel')),FilledButton(onPressed:()=>Navigator.pop(ctx,edit.text.trim()),child:const Text('Save'))]));
        edit.dispose(); if(value==null||value.isEmpty)return; await widget.api.patch(url,{'message':value});
      }
      await load();
    }catch(e){if(mounted)snack(context,errorText(e));}
  }

  Future<void> showGroupInfo() async {
    final adminMembers=members.where((m)=>m['id']==widget.group['admin_id']).toList();
    final adminName=adminMembers.isEmpty?'Not set':(adminMembers.first['full_name']??adminMembers.first['username']).toString();
    await showModalBottomSheet<void>(context:context,isScrollControlled:true,builder:(sheet)=>SafeArea(child:DraggableScrollableSheet(expand:false,initialChildSize:.72,builder:(ctx,scroll)=>Column(children:[
      Padding(padding:const EdgeInsets.all(14),child:Text(widget.group['name']??'Group information',style:Theme.of(ctx).textTheme.titleLarge)),
      Expanded(child:ListView(controller:scroll,children:[
        ListTile(leading:const Icon(Icons.groups),title:Text('${members.length} members'),subtitle:Text('Admin: $adminName')),
        for(final member in members) ListTile(leading:UserAvatar(url:member['avatar']??'',username:member['username']??''),title:Text(member['full_name']??member['username']),subtitle:Text((member['bio']??'').toString(),maxLines:2,overflow:TextOverflow.ellipsis),trailing:member['id']==widget.group['admin_id']?const Chip(label:Text('Admin')):null),
      ])),
      Padding(padding:const EdgeInsets.all(12),child:OutlinedButton.icon(onPressed:()async{final confirm=await showDialog<bool>(context:ctx,builder:(c)=>AlertDialog(title:const Text('Leave group?'),content:const Text('You will stop receiving messages from this group.'),actions:[TextButton(onPressed:()=>Navigator.pop(c,false),child:const Text('Cancel')),FilledButton(onPressed:()=>Navigator.pop(c,true),child:const Text('Leave'))]));if(confirm==true){try{await widget.api.delete('/api/mobile/groups/${widget.group['id']}/leave/');if(mounted){Navigator.pop(sheet);Navigator.pop(context);}}catch(e){if(mounted)snack(context,errorText(e));}}},icon:const Icon(Icons.logout),label:const Text('Leave group'))),
    ]))));
  }

  Future<void> sendMedia(
    PickedUpload? media, {
    bool photoEdit = false,
    bool videoEdit = false,
  }) async {
    if (media == null || !mounted || sending) return;
    if (media.bytes.length > 25 * 1024 * 1024) {
      snack(context, 'Maximum file size is 25 MB.');
      return;
    }
    if (photoEdit) {
      media = await ChatMediaTools.editPhoto(context, media);
      if (media == null || !mounted) return;
    }
    if (videoEdit) {
      try {
        media = await ChatMediaTools.editVideo(context, widget.api, media);
      } catch (e) {
        if (mounted) snack(context, errorText(e));
        return;
      }
      if (media == null || !mounted) return;
    }
    setState(() => sending = true);
    try {
      await widget.api.upload(path, file: media);
      await load();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  Future<void> captureMedia(bool video) async {
    try {
      await sendMedia(
        await ChatMediaTools.capture(video: video),
        photoEdit: !video,
        videoEdit: video,
      );
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> toggleRecording() async {
    try {
      if (recording) {
        final filePath = await recorder.stop();
        if (mounted) setState(() => recording = false);
        if (filePath != null) {
          final data = await XFile(filePath).readAsBytes();
          await sendMedia(
            PickedUpload(
              'voice_${DateTime.now().millisecondsSinceEpoch}.${kIsWeb ? 'webm' : 'm4a'}',
              data,
              kIsWeb ? 'audio/webm' : 'audio/mp4',
            ),
          );
        }
      } else {
        if (!await recorder.hasPermission()) {
          if (mounted) snack(context, 'Microphone permission denied.');
          return;
        }
        final directory = kIsWeb
            ? ''
            : '${(await getTemporaryDirectory()).path}/';
        final extension = kIsWeb ? 'webm' : 'm4a';
        await recorder.start(
          RecordConfig(
            encoder: kIsWeb ? AudioEncoder.opus : AudioEncoder.aacLc,
          ),
          path:
              '${directory}voice_${DateTime.now().millisecondsSinceEpoch}.$extension',
        );
        if (mounted) setState(() => recording = true);
      }
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> shareLocation() async {
    try {
      final link = await ChatMediaTools.currentLocationLink();
      await widget.api.post(path, {'message': link});
      await load();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> mediaMenu() async {
    await showModalBottomSheet<void>(
      context: context,
      builder: (sheetContext) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.photo_camera),
              title: const Text('Take photo'),
              onTap: () {
                Navigator.pop(sheetContext);
                captureMedia(false);
              },
            ),
            ListTile(
              leading: const Icon(Icons.videocam),
              title: const Text('Record video'),
              onTap: () {
                Navigator.pop(sheetContext);
                captureMedia(true);
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library_outlined),
              title: const Text('Choose photo from gallery'),
              onTap: () {
                Navigator.pop(sheetContext);
                ChatMediaTools.gallery(video: false).then((f) => sendMedia(f, photoEdit: true));
              },
            ),
            ListTile(
              leading: const Icon(Icons.video_library_outlined),
              title: const Text('Choose video from gallery'),
              onTap: () {
                Navigator.pop(sheetContext);
                ChatMediaTools.gallery(video: true).then((f) => sendMedia(f, videoEdit: true));
              },
            ),
            ListTile(
              leading: const Icon(Icons.attach_file),
              title: const Text('Choose file'),
              onTap: () {
                Navigator.pop(sheetContext);
                attach();
              },
            ),
            ListTile(
              leading: const Icon(Icons.location_on),
              title: const Text('Share current location'),
              onTap: () {
                Navigator.pop(sheetContext);
                shareLocation();
              },
            ),
          ],
        ),
      ),
    );
  }

  Future<void> attach() async {
    if (sending) return;
    final f = await pickUpload();
    if (f == null || !mounted) return;
    setState(() => sending = true);
    try {
      await widget.api.upload(path, file: f);
      await load();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  Future<void> addMembers() async {
    final current = members.map((m) => m['id']).toSet();
    final people = await widget.api.get('/api/mobile/contacts/');
    if (!mounted) return;
    final candidates = (people['people'] as List)
        .where((p) => !current.contains(p['id']))
        .toList();
    final selected = <int>{};
    final ok = await showDialog<bool>(
      context: context,
      builder: (c) => StatefulBuilder(
        builder: (c, refresh) => AlertDialog(
          title: const Text('Add group members'),
          content: SizedBox(
            width: 380,
            height: 300,
            child: ListView(
              children: candidates
                  .map(
                    (p) => CheckboxListTile(
                      value: selected.contains(p['id']),
                      title: Text(p['username']),
                      onChanged: (v) => refresh(() {
                        if (v == true) {
                          selected.add(p['id']);
                        } else {
                          selected.remove(p['id']);
                        }
                      }),
                    ),
                  )
                  .toList(),
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(c, false),
              child: const Text('Cancel'),
            ),
            FilledButton(
              onPressed: () => Navigator.pop(c, true),
              child: const Text('Add'),
            ),
          ],
        ),
      ),
    );
    if (ok == true && selected.isNotEmpty) {
      try {
        await widget.api.post(
          '/api/mobile/groups/${widget.group['id']}/members/',
          {'member_ids': selected.toList()},
        );
        await load();
      } catch (e) {
        if (mounted) snack(context, errorText(e));
      }
    }
  }

  @override
  void dispose() {
    timer?.cancel();
    recorder.dispose();
    input.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext c) => Scaffold(
    appBar: AppBar(
      title: InkWell(onTap:showGroupInfo,child:Text(widget.group['name'])),
      actions: [
        if(widget.group['is_admin']==true) IconButton(
          tooltip: 'Add members',
          onPressed: addMembers,
          icon: const Icon(Icons.person_add_alt_1),
        ),
        IconButton(tooltip:'Group information',onPressed:showGroupInfo,icon:const Icon(Icons.info_outline)),
      ],
    ),
    body: Column(
      children: [
        Expanded(
          child: loading
              ? const Center(child: CircularProgressIndicator())
              : ListView.builder(
                  reverse: true,
                  itemCount: messages.length,
                  itemBuilder: (_, i) {
                    final m = messages[messages.length - 1 - i];
                    final mine = m['is_me'] == true;
                    return Dismissible(key:ValueKey('gm-${m['id']}'),direction:DismissDirection.startToEnd,confirmDismiss:(_)async{setState(()=>replyTo=Map<String,dynamic>.from(m));return false;},child:Align(
                      alignment: mine
                          ? Alignment.centerRight
                          : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.all(6),
                        padding: const EdgeInsets.all(12),
                        constraints: const BoxConstraints(maxWidth: 310),
                        decoration: BoxDecoration(
                          color: mine ? const Color(0xffe8e8e8) : Colors.white,
                          borderRadius: BorderRadius.circular(16),
                        ),
                        child: GestureDetector(onLongPress:()=>messageActions(Map<String,dynamic>.from(m)),child:Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            if (!mine)
                              Text(
                                m['sender'],
                                style: const TextStyle(
                                  fontSize: 11,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            if ((m['reply_to'] ?? '').toString().isNotEmpty)
                              Align(alignment:Alignment.centerLeft,child:Text('↳ ${m['reply_to']}',maxLines:1,overflow:TextOverflow.ellipsis,style:const TextStyle(fontSize:11,color:Colors.blueGrey))),
                            Text(
                              m['message'] ?? '',
                              style: TextStyle(color: Colors.black87),
                            ),
                            if ((m['attachment'] ?? '').toString().isNotEmpty)
                              chatAttachment(m['attachment'].toString(), mine),
                            Text(
                              stamp(m['timestamp']),
                              style: TextStyle(
                                fontSize: 10,
                                color: Colors.black54,
                              ),
                            ),
                          ],
                        )),
                      ),
                    ));
                  },
                ),
        ),
        SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(10),
            child: Column(mainAxisSize:MainAxisSize.min,children:[
              if(replyTo!=null) ListTile(dense:true,title:Text('Replying to ${replyTo!['sender']??'message'}'),subtitle:Text('${replyTo!['message']??''}',maxLines:1,overflow:TextOverflow.ellipsis),trailing:IconButton(onPressed:()=>setState(()=>replyTo=null),icon:const Icon(Icons.close))),
              Row(
              children: [
                IconButton(
                  tooltip: "Camera, files and location",
                  onPressed: sending ? null : mediaMenu,
                  icon: const Icon(Icons.add_circle_outline),
                ),
                IconButton(
                  tooltip: recording
                      ? "Stop and send voice note"
                      : "Record voice note",
                  onPressed: sending ? null : toggleRecording,
                  icon: Icon(
                    recording ? Icons.stop_circle : Icons.mic,
                    color: recording ? Colors.red : null,
                  ),
                ),
                Expanded(
                  child: TextField(
                    controller: input,
                    onSubmitted: (_) => send(),
                    decoration: const InputDecoration(
                      hintText: 'Message group',
                    ),
                  ),
                ),
                IconButton.filled(
                  onPressed: sending ? null : send,
                  icon: const Icon(Icons.send),
                ),
              ],
              ),
            ]),
          ),
        ),
      ],
    ),
  );
}

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({
    super.key,
    required this.api,
    required this.onRead,
  });
  final CampusApi api;
  final VoidCallback onRead;
  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  List items = [];
  bool loading = true;
  Future<void> load() async {
    try {
      final d = await widget.api.get('/api/mobile/notifications/');
      if (mounted) setState(() => items = d['notifications'] ?? []);
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> readAll() async {
    try {
      await widget.api.post('/api/mobile/notifications/', {});
      await load();
      widget.onRead();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  @override
  void initState() {
    super.initState();
    load();
  }

  @override
  Widget build(BuildContext c) => Scaffold(
    backgroundColor: Colors.transparent,
    body: loading
        ? const Center(child: CircularProgressIndicator())
        : RefreshIndicator(
            onRefresh: load,
            child: items.isEmpty
                ? ListView(
                    children: [
                      SizedBox(height: 180),
                      Center(child: Text('You are all caught up.')),
                    ],
                  )
                : ListView(
                    children: [
                      Align(
                        alignment: Alignment.centerRight,
                        child: TextButton(
                          onPressed: readAll,
                          child: const Text('Mark all read'),
                        ),
                      ),
                      ...items.map(
                        (n) => ListTile(
                          leading: CircleAvatar(
                            backgroundColor: n['is_read'] == true
                                ? Colors.grey.shade200
                                : const Color(0xffeeeeee),
                            child: Icon(
                              n['kind'] == 'like'
                                  ? Icons.favorite
                                  : n['kind'] == 'comment'
                                  ? Icons.mode_comment
                                  : n['kind'] == 'message'
                                  ? Icons.chat
                                  : Icons.notifications,
                              color: n['kind'] == 'like' ? Colors.pink : brand,
                            ),
                          ),
                          title: Text(n['text']),
                          subtitle: Text(
                            '${n['actor']} · ${stamp(n['created_at'])}',
                          ),
                          tileColor: n['is_read'] == true
                              ? null
                              : brand.withValues(alpha: .05),
                        ),
                      ),
                    ],
                  ),
          ),
  );
}

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key, required this.api});
  final CampusApi api;
  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final input = TextEditingController();
  List people = [], posts = [];
  bool loading = false;
  Timer? debounce;
  Future<void> search(String q) async {
    debounce?.cancel();
    if (q.trim().isEmpty) {
      setState(() {
        people = [];
        posts = [];
      });
      return;
    }
    debounce = Timer(const Duration(milliseconds: 350), () async {
      setState(() => loading = true);
      try {
        final d = await widget.api.get(
          '/api/mobile/search/?q=${Uri.encodeQueryComponent(q)}',
        );
        if (mounted)
          setState(() {
            people = d['people'] ?? [];
            posts = d['posts'] ?? [];
          });
      } catch (e) {
        if (mounted) snack(context, errorText(e));
      } finally {
        if (mounted) setState(() => loading = false);
      }
    });
  }

  @override
  void dispose() {
    debounce?.cancel();
    input.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext c) => Scaffold(
    appBar: AppBar(
      title: TextField(
        controller: input,
        autofocus: true,
        onChanged: search,
        decoration: const InputDecoration(
          hintText: 'Search people and posts',
          border: InputBorder.none,
        ),
      ),
    ),
    body: loading
        ? const Center(child: CircularProgressIndicator())
        : ListView(
            children: [
              if (people.isNotEmpty)
                const Padding(
                  padding: EdgeInsets.all(14),
                  child: Text(
                    'PEOPLE',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ...people.map(
                (p) => ListTile(
                  leading: CircleAvatar(child: Text(initials(p['username']))),
                  title: Text(p['full_name'] ?? p['username']),
                  subtitle: Text('@${p['username']}'),
                  onTap: () => Navigator.push(
                    c,
                    MaterialPageRoute(
                      builder: (_) => ProfileScreen(
                        api: widget.api,
                        username: p['username'],
                      ),
                    ),
                  ),
                ),
              ),
              if (posts.isNotEmpty)
                const Padding(
                  padding: EdgeInsets.all(14),
                  child: Text(
                    'POSTS',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ...posts.map(
                (p) => PostCard(
                  post: p,
                  onLike: () async {
                    await widget.api.post(
                      '/api/mobile/feed/${p['id']}/like/',
                      {},
                    );
                    search(input.text);
                  },
                  onComments: () => showModalBottomSheet(
                    context: c,
                    isScrollControlled: true,
                    builder: (_) => CommentsSheet(api: widget.api, post: p),
                  ),
                  onProfile: () => Navigator.push(
                    c,
                    MaterialPageRoute(
                      builder: (_) => ProfileScreen(
                        api: widget.api,
                        username: p['username'],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
  );
}

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key, required this.api, required this.username});
  final CampusApi api;
  final String username;
  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  Map profile = {};
  String username = '';
  bool loading = true, busy = false;
  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    try {
      final me = await widget.api.get('/api/mobile/me/');
      username = widget.username.isEmpty
          ? me['user']['username']
          : widget.username;
      final d = await widget.api.get(
        '/api/mobile/profile/${Uri.encodeComponent(username)}/',
      );
      if (mounted) setState(() => profile = d['profile'] ?? {});
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => loading = false);
    }
  }

  Future<void> editProfile() async {
    final fields = [
      'first_name',
      'last_name',
      'bio',
      'home_address',
      'relationship_status',
      'education_status',
    ];
    final labels = [
      'First name',
      'Last name',
      'Bio',
      'Home address',
      'Relationship status',
      'Education / studies',
    ];
    final controllers = {
      for (final f in fields)
        f: TextEditingController(text: (profile[f] ?? '').toString()),
    };
    final result = await showDialog<Map<String, String>>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Edit profile'),
        content: SizedBox(
          width: 440,
          child: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                for (var i = 0; i < fields.length; i++)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 12),
                    child: TextField(
                      controller: controllers[fields[i]],
                      maxLines: fields[i] == 'bio' ? 3 : 1,
                      decoration: InputDecoration(
                        labelText: labels[i],
                        border: const OutlineInputBorder(),
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, {
              for (final f in fields) f: controllers[f]!.text.trim(),
            }),
            child: const Text('Save'),
          ),
        ],
      ),
    );
    for (final c in controllers.values) {
      c.dispose();
    }
    if (result == null || !mounted) return;
    try {
      await widget.api.post(
        '/api/mobile/profile/${Uri.encodeComponent(username)}/',
        result,
      );
      await load();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> editPrivacy() async {
    String lastSeen=(profile['last_seen_privacy']??'everyone').toString();
    String status=(profile['status_privacy']??'everyone').toString();
    bool receipts=profile['read_receipts']!=false;
    final result=await showDialog<Map<String,dynamic>>(context:context,builder:(ctx)=>StatefulBuilder(builder:(ctx,setDialog)=>AlertDialog(title:const Text('Privacy settings'),content:Column(mainAxisSize:MainAxisSize.min,children:[
      DropdownButtonFormField<String>(value:lastSeen,decoration:const InputDecoration(labelText:'Last seen'),items:const [DropdownMenuItem(value:'everyone',child:Text('Everyone')),DropdownMenuItem(value:'followers',child:Text('Followers')),DropdownMenuItem(value:'nobody',child:Text('Nobody'))],onChanged:(v){if(v!=null)setDialog(()=>lastSeen=v);}),
      DropdownButtonFormField<String>(value:status,decoration:const InputDecoration(labelText:'Status privacy'),items:const [DropdownMenuItem(value:'everyone',child:Text('Everyone')),DropdownMenuItem(value:'followers',child:Text('Followers')),DropdownMenuItem(value:'nobody',child:Text('Nobody'))],onChanged:(v){if(v!=null)setDialog(()=>status=v);}),
      SwitchListTile(contentPadding:EdgeInsets.zero,title:const Text('Read receipts'),value:receipts,onChanged:(v)=>setDialog(()=>receipts=v)),
    ]),actions:[TextButton(onPressed:()=>Navigator.pop(ctx),child:const Text('Cancel')),FilledButton(onPressed:()=>Navigator.pop(ctx,{'last_seen_privacy':lastSeen,'status_privacy':status,'read_receipts':receipts}),child:const Text('Save'))])));
    if(result==null||!mounted)return;
    try{await widget.api.post('/api/mobile/profile/${Uri.encodeComponent(username)}/',result);await load();}catch(e){if(mounted)snack(context,errorText(e));}
  }

  Future<void> changeAvatar() async {
    final file = await pickUpload(imagesOnly: true);
    if (file == null || !mounted) return;
    setState(() => busy = true);
    try {
      await widget.api.upload(
        '/api/mobile/profile/${Uri.encodeComponent(username)}/',
        file: file,
        fileField: 'avatar',
      );
      await load();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => busy = false);
    }
  }

  Future<void> changePassword() async {
    final old = TextEditingController(),
        next = TextEditingController(),
        confirm = TextEditingController();
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Change password'),
        content: SizedBox(
          width: 400,
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              TextField(
                controller: old,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Current password',
                ),
              ),
              TextField(
                controller: next,
                obscureText: true,
                decoration: const InputDecoration(labelText: 'New password'),
              ),
              TextField(
                controller: confirm,
                obscureText: true,
                decoration: const InputDecoration(
                  labelText: 'Confirm new password',
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(ctx, false),
            child: const Text('Cancel'),
          ),
          FilledButton(
            onPressed: () => Navigator.pop(ctx, true),
            child: const Text('Update'),
          ),
        ],
      ),
    );
    final a = old.text, b = next.text, c = confirm.text;
    old.dispose();
    next.dispose();
    confirm.dispose();
    if (ok != true || !mounted) return;
    if (b != c) {
      snack(context, 'Passwords do not match');
      return;
    }
    try {
      await widget.api.post('/api/mobile/change-password/', {
        'old_password': a,
        'new_password': b,
      });
      if (mounted) snack(context, 'Password changed');
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> follow() async {
    try {
      await widget.api.post('/api/mobile/profile/$username/follow/', {});
      await load();
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  @override
  Widget build(BuildContext context) {
    if (loading)
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    final mine = widget.username.isEmpty;
    final avatar = (profile['avatar'] ?? '').toString();
    return Scaffold(
      appBar: AppBar(title: Text('@$username')),
      body: RefreshIndicator(
        onRefresh: load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Center(
              child: CircleAvatar(
                radius: 52,
                backgroundImage: avatar.isEmpty ? null : NetworkImage(avatar),
                child: avatar.isEmpty
                    ? Text(
                        initials(username),
                        style: const TextStyle(fontSize: 30),
                      )
                    : null,
              ),
            ),
            const SizedBox(height: 12),
            Center(
              child: Text(
                profile['full_name'] ?? username,
                style: Theme.of(context).textTheme.headlineSmall,
              ),
            ),
            for (final entry in {
              'bio': 'Bio',
              'home_address': 'Home address',
              'relationship_status': 'Relationship',
              'education_status': 'Studies',
            }.entries)
              if ((profile[entry.key] ?? '').toString().isNotEmpty)
                ListTile(
                  title: Text(entry.value),
                  subtitle: Text(profile[entry.key].toString()),
                ),
            if (mine) ...[
              FilledButton.icon(
                onPressed: busy ? null : changeAvatar,
                icon: const Icon(Icons.photo_camera),
                label: const Text('Change profile photo'),
              ),
              OutlinedButton.icon(
                onPressed: editProfile,
                icon: const Icon(Icons.edit),
                label: const Text('Edit profile details'),
              ),
              OutlinedButton.icon(onPressed:editPrivacy,icon:const Icon(Icons.privacy_tip_outlined),label:const Text('Privacy settings')),
              OutlinedButton.icon(
                onPressed: changePassword,
                icon: const Icon(Icons.lock),
                label: const Text('Change password'),
              ),
            ] else
              FilledButton(
                onPressed: follow,
                child: Text(
                  profile['is_following'] == true ? 'Unfollow' : 'Follow',
                ),
              ),
            const Divider(),
            Text('Posts', style: Theme.of(context).textTheme.titleLarge),
            for (final post in (profile['posts'] ?? []))
              PostCard(
                post: post,
                onLike: () async {
                  await widget.api.post(
                    '/api/mobile/feed/${post['id']}/like/',
                    {},
                  );
                  await load();
                },
                onComments: () => showModalBottomSheet(
                  context: context,
                  isScrollControlled: true,
                  builder: (_) => CommentsSheet(api: widget.api, post: post),
                ),
                onProfile: () {},
              ),
          ],
        ),
      ),
    );
  }
}

class ComplaintScreen extends StatefulWidget {
  const ComplaintScreen({super.key, required this.api});
  final CampusApi api;
  @override
  State<ComplaintScreen> createState() => _ComplaintScreenState();
}

class _ComplaintScreenState extends State<ComplaintScreen> {
  final description = TextEditingController();
  PickedUpload? attachment;
  List complaints = [];
  bool sending = false;
  @override
  void initState() {
    super.initState();
    load();
  }

  Future<void> load() async {
    try {
      final d = await widget.api.get('/api/mobile/complaints/');
      if (mounted) setState(() => complaints = d['complaints'] ?? []);
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    }
  }

  Future<void> submit() async {
    if (description.text.trim().length < 10) {
      snack(context, 'Please enter at least 10 characters');
      return;
    }
    setState(() => sending = true);
    try {
      await widget.api.upload(
        '/api/mobile/complaints/',
        fields: {'description': description.text.trim()},
        file: attachment,
      );
      description.clear();
      if (mounted) setState(() => attachment = null);
      await load();
      if (mounted) snack(context, 'Complaint submitted');
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => sending = false);
    }
  }

  @override
  void dispose() {
    description.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('Complaints')),
    body: ListView(
      padding: const EdgeInsets.all(16),
      children: [
        TextField(
          controller: description,
          maxLines: 5,
          maxLength: 5000,
          decoration: const InputDecoration(
            labelText: 'Describe your complaint',
            border: OutlineInputBorder(),
          ),
        ),
        OutlinedButton.icon(
          onPressed: () async {
            final f = await pickUpload();
            if (mounted) setState(() => attachment = f);
          },
          icon: const Icon(Icons.attach_file),
          label: Text(attachment?.name ?? 'Add attachment (up to 10 MB)'),
        ),
        FilledButton(
          onPressed: sending ? null : submit,
          child: Text(sending ? 'Submitting…' : 'Submit complaint'),
        ),
        const Divider(),
        Text('My complaints', style: Theme.of(context).textTheme.titleLarge),
        for (final c in complaints)
          Card(
            child: ListTile(
              title: Text(c['description'] ?? ''),
              subtitle: Text('${c['date']} · ${c['status']}'),
              trailing: (c['attachment'] ?? '').toString().isEmpty
                  ? null
                  : IconButton(
                      icon: const Icon(Icons.attach_file),
                      onPressed: () => launchExternal(c['attachment']),
                    ),
            ),
          ),
      ],
    ),
  );
}
