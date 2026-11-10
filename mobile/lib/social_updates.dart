part of 'main.dart';

ThemeData campusLightTheme() => ThemeData(
  useMaterial3: true,
  brightness: Brightness.light,
  scaffoldBackgroundColor: const Color(0xfff5f5f5),
  colorScheme: const ColorScheme.light(
    primary: Color(0xff555555),
    onPrimary: Colors.white,
    secondary: Color(0xff777777),
    onSecondary: Colors.white,
    surface: Colors.white,
    onSurface: Color(0xff292929),
    primaryContainer: Color(0xffeeeeee),
    onPrimaryContainer: Color(0xff333333),
    secondaryContainer: Color(0xffeeeeee),
    onSecondaryContainer: Color(0xff333333),
    surfaceTint: Colors.transparent,
  ),
  appBarTheme: const AppBarTheme(
    backgroundColor: Colors.white,
    surfaceTintColor: Colors.transparent,
  ),
  navigationBarTheme: const NavigationBarThemeData(
    backgroundColor: Colors.white,
    indicatorColor: Color(0xffe7e7e7),
  ),
  dividerColor: const Color(0xffdddddd),
);

class UserAvatar extends StatelessWidget {
  const UserAvatar({
    super.key,
    required this.url,
    required this.username,
    this.radius = 22,
  });
  final String url, username;
  final double radius;
  @override
  Widget build(BuildContext context) => CircleAvatar(
    radius: radius,
    backgroundColor: const Color(0xffe6e6e6),
    child: ClipOval(
      child: url.isEmpty
          ? Text(initials(username), style: const TextStyle(color: brand))
          : Image.network(
              url,
              width: radius * 2,
              height: radius * 2,
              fit: BoxFit.cover,
              errorBuilder: (_, __, ___) => Text(
                initials(username),
                style: const TextStyle(color: brand),
              ),
            ),
    ),
  );
}

bool socialVideo(String name, [String filename='']) => isVideoMedia(name,filename);
bool socialPhoto(String name, [String filename='']) => isImageMedia(name,filename);

class SocialMediaView extends StatelessWidget {
  const SocialMediaView({super.key, required this.url, this.filename=''});
  final String url;
  final String filename;
  @override
  Widget build(BuildContext context) {
    if (socialVideo(url,filename))
      return Center(
        child: InlineVideoPlayer(key: ValueKey(url), url: url),
      );
    if (socialPhoto(url,filename))
      return InkWell(
        onTap: () => showDialog<void>(
          context: context,
          builder: (dialogContext) => Dialog(
            child: Stack(
              children: [
                InteractiveViewer(
                  minScale: .5,
                  maxScale: 5,
                  child: Image.network(
                    url,
                    fit: BoxFit.contain,
                    errorBuilder: (_, __, ___) => const Center(
                      child: Text('Photo unavailable'),
                    ),
                  ),
                ),
                Positioned(
                  right: 4,
                  top: 4,
                  child: IconButton(
                    onPressed: () => Navigator.pop(dialogContext),
                    icon: const Icon(Icons.close),
                  ),
                ),
              ],
            ),
          ),
        ),
        child: Image.network(
          url,
          width: double.infinity,
          fit: BoxFit.contain,
          errorBuilder: (_, __, ___) => const Padding(
            padding: EdgeInsets.all(24),
            child: Text('Photo unavailable'),
          ),
        ),
      );
    return TextButton.icon(
      onPressed: () => launchExternal(url),
      icon: const Icon(Icons.attach_file),
      label: const Text('Open attachment'),
    );
  }
}

Future<PickedUpload?> chooseSocialMedia(
  BuildContext context, {
  String? source,
}) async {
  final choice =
      source ??
      await showModalBottomSheet<String>(
        context: context,
        builder: (sheet) => SafeArea(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.photo_library_outlined),
                title: const Text('Choose photo'),
                onTap: () => Navigator.pop(sheet, 'photo'),
              ),
              ListTile(
                leading: const Icon(Icons.video_library_outlined),
                title: const Text('Choose video'),
                onTap: () => Navigator.pop(sheet, 'video'),
              ),
              ListTile(
                leading: const Icon(Icons.camera_front_outlined),
                title: const Text('Take selfie'),
                onTap: () => Navigator.pop(sheet, 'selfie'),
              ),
              ListTile(
                leading: const Icon(Icons.camera_alt_outlined),
                title: const Text('Take photo'),
                onTap: () => Navigator.pop(sheet, 'camera'),
              ),
              ListTile(
                leading: const Icon(Icons.videocam_outlined),
                title: const Text('Record video'),
                onTap: () => Navigator.pop(sheet, 'record'),
              ),
            ],
          ),
        ),
      );
  if (choice == null || !context.mounted) return null;
  try {
    final picker = ImagePicker();
    final XFile? picked;
    if (choice == 'video' || choice == 'record') {
      picked = await picker.pickVideo(
        source: choice == 'record' ? ImageSource.camera : ImageSource.gallery,
        maxDuration: const Duration(minutes: 2),
      );
    } else {
      picked = await picker.pickImage(
        source: choice == 'photo' ? ImageSource.gallery : ImageSource.camera,
        preferredCameraDevice: choice == 'selfie'
            ? CameraDevice.front
            : CameraDevice.rear,
        imageQuality: 95,
      );
    }
    if (picked == null || !context.mounted) return null;
    final media = PickedUpload(
      picked.name,
      await picked.readAsBytes(),
      picked.mimeType,
    );
    if (choice == 'video' || choice == 'record') return media;
    if (!context.mounted) return null;
    return await ChatMediaTools.editPhoto(context, media);
  } catch (e) {
    if (context.mounted) snack(context, errorText(e));
    return null;
  }
}

class PhotoFilterEditor extends StatefulWidget {
  const PhotoFilterEditor({super.key, required this.file});
  final PickedUpload file;
  @override
  State<PhotoFilterEditor> createState() => _PhotoFilterEditorState();
}

class _PhotoFilterEditorState extends State<PhotoFilterEditor> {
  img.Image? original;
  String filter = 'Original';
  double brightness = 1, contrast = 1;
  int turns = 0;
  bool square = false, saving = false;
  Uint8List? preview;
  String? error;
  final filters = [
    'Original',
    'Mono',
    'Sepia',
    'Warm',
    'Cool',
    'Vivid',
    'Soft',
  ];
  @override
  void initState() {
    super.initState();
    try {
      original = img.decodeImage(widget.file.bytes);
      if (original == null) {
        error = 'This image format cannot be edited.';
      } else {
        updatePreview();
      }
    } catch (_) {
      error = 'Could not decode this photo.';
    }
  }

  img.Image render({bool small = false}) {
    var result = img.Image.from(original!);
    if (small && result.width > 800)
      result = img.copyResize(result, width: 800);
    result = img.copyRotate(result, angle: turns * 90);
    if (square) {
      final side = result.width < result.height ? result.width : result.height;
      result = img.copyCrop(
        result,
        x: (result.width - side) ~/ 2,
        y: (result.height - side) ~/ 2,
        width: side,
        height: side,
      );
    }
    if (filter == 'Mono') result = img.grayscale(result);
    if (filter == 'Sepia') result = img.sepia(result);
    result = img.adjustColor(
      result,
      brightness: brightness,
      contrast: contrast,
      saturation: filter == 'Vivid'
          ? 1.6
          : filter == 'Soft'
          ? 0.65
          : 1,
      gamma: filter == 'Soft' ? 1.15 : 1,
    );
    if (filter == 'Warm' || filter == 'Cool') {
      for (final pixel in result) {
        final red = pixel.r.toDouble(), blue = pixel.b.toDouble();
        pixel.r = (red * (filter == 'Warm' ? 1.12 : 0.90)).clamp(0, 255);
        pixel.b = (blue * (filter == 'Cool' ? 1.12 : 0.90)).clamp(0, 255);
      }
    }
    return result;
  }

  void updatePreview() {
    preview = Uint8List.fromList(
      img.encodeJpg(render(small: true), quality: 80),
    );
  }

  void change(VoidCallback edit) {
    setState(() {
      edit();
      updatePreview();
    });
  }

  Future<void> save() async {
    setState(() => saving = true);
    await Future<void>.delayed(Duration.zero);
    try {
      final result = PickedUpload(
        'photo_${DateTime.now().millisecondsSinceEpoch}.jpg',
        Uint8List.fromList(img.encodeJpg(render(), quality: 92)),
        'image/jpeg',
      );
      if (mounted) Navigator.pop(context, result);
    } catch (e) {
      if (mounted) {
        setState(() => saving = false);
        snack(context, errorText(e));
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(
      title: const Text('Photo filters'),
      actions: [
        TextButton(
          onPressed: saving || original == null ? null : save,
          child: Text(saving ? 'Saving…' : 'Use photo'),
        ),
      ],
    ),
    body: error != null
        ? Center(child: Text(error!))
        : ListView(
            padding: const EdgeInsets.all(16),
            children: [
              if (preview != null)
                SizedBox(
                  height: 300,
                  child: Image.memory(
                    preview!,
                    gaplessPlayback: true,
                    fit: BoxFit.contain,
                  ),
                ),
              const SizedBox(height: 16),
              Wrap(
                spacing: 8,
                children: filters
                    .map(
                      (name) => ChoiceChip(
                        label: Text(name),
                        selected: filter == name,
                        onSelected: saving
                            ? null
                            : (_) => change(() => filter = name),
                      ),
                    )
                    .toList(),
              ),
              Row(
                children: [
                  IconButton(
                    tooltip: 'Rotate',
                    onPressed: saving
                        ? null
                        : () => change(() => turns = (turns + 1) % 4),
                    icon: const Icon(Icons.rotate_right),
                  ),
                  FilterChip(
                    label: const Text('Square crop'),
                    selected: square,
                    onSelected: saving ? null : (v) => change(() => square = v),
                  ),
                ],
              ),
              const Text('Brightness'),
              Slider(
                value: brightness,
                min: 0.5,
                max: 1.5,
                onChanged: saving ? null : (v) => change(() => brightness = v),
              ),
              const Text('Contrast'),
              Slider(
                value: contrast,
                min: 0.5,
                max: 1.5,
                onChanged: saving ? null : (v) => change(() => contrast = v),
              ),
            ],
          ),
  );
}

class StatusPanel extends StatefulWidget {
  const StatusPanel({super.key, required this.api});
  final CampusApi api;
  @override
  State<StatusPanel> createState() => _StatusPanelState();
}

class _StatusPanelState extends State<StatusPanel> {
  List statuses = [];
  String? error;
  Timer? timer;
  bool loading = true;
  @override
  void initState() {
    super.initState();
    load();
    timer = Timer.periodic(const Duration(seconds: 30), (_) => load());
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  Future<void> load() async {
    try {
      final d = await widget.api.get('/api/mobile/status/');
      if (mounted)
        setState(() {
          statuses = d['statuses'] ?? [];
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

  Future<void> compose() async {
    await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => StatusComposer(api: widget.api)),
    );
    await load();
  }

  @override
  Widget build(BuildContext context) {
    final groups = <String, List<dynamic>>{};
    for (final status in statuses) {
      groups.putIfAbsent(status['username'], () => []).add(status);
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Expanded(child: Padding(
              padding: EdgeInsets.only(left: 14),
              child: Text(
                'Status · 24 hours',
                style: TextStyle(fontWeight: FontWeight.w600),
              ),
            )),
            IconButton(
              tooltip: 'Refresh statuses',
              onPressed: load,
              icon: const Icon(Icons.refresh, size: 20),
            ),
          ],
        ),
        if (error != null)
          ListTile(
            dense: true,
            title: Text(error!),
            trailing: TextButton(onPressed: load, child: const Text('Retry')),
          ),
        SizedBox(
          height: 100,
          child: ListView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 14),
            children: [
              SizedBox(
                width: 78,
                child: InkWell(
                  onTap: compose,
                  child: const Column(
                    children: [
                      CircleAvatar(
                        radius: 27,
                        backgroundColor: Color(0xffe5e5e5),
                        child: Icon(Icons.add, color: brand),
                      ),
                      SizedBox(height: 6),
                      Text('Add status', style: TextStyle(fontSize: 12)),
                    ],
                  ),
                ),
              ),
              if (loading)
                const Padding(
                  padding: EdgeInsets.all(20),
                  child: SizedBox(
                    width: 24,
                    height: 24,
                    child: CircularProgressIndicator(),
                  ),
                ),
              ...groups.entries.map((entry) {
                final first = entry.value.first;
                final unread = entry.value.any((s) => s['viewed'] != true);
                return SizedBox(
                  width: 80,
                  child: InkWell(
                    onTap: () async {
                      await Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (_) => StatusViewer(
                            api: widget.api,
                            statuses: entry.value,
                          ),
                        ),
                      );
                      await load();
                    },
                    child: Column(
                      children: [
                        Container(
                          padding: const EdgeInsets.all(3),
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            border: Border.all(
                              color: unread ? brand : const Color(0xffcccccc),
                              width: unread ? 3 : 1,
                            ),
                          ),
                          child: UserAvatar(
                            url: first['avatar'] ?? '',
                            username: entry.key,
                            radius: 23,
                          ),
                        ),
                        const SizedBox(height: 5),
                        Text(
                          first['is_mine'] == true ? 'My status' : entry.key,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                );
              }),
            ],
          ),
        ),
      ],
    );
  }
}

class StatusComposer extends StatefulWidget {
  const StatusComposer({super.key, required this.api});
  final CampusApi api;
  @override
  State<StatusComposer> createState() => _StatusComposerState();
}

class _StatusComposerState extends State<StatusComposer> {
  final caption = TextEditingController();
  PickedUpload? media;
  bool busy = false;
  @override
  void dispose() {
    caption.dispose();
    super.dispose();
  }

  Future<void> choose({String? source}) async {
    final picked = await chooseSocialMedia(context, source: source);
    if (picked != null && mounted) setState(() => media = picked);
  }

  Future<void> publish() async {
    if (busy) return;
    if (media == null && caption.text.trim().isEmpty) {
      snack(context, 'Add text, a photo or a video.');
      return;
    }
    setState(() => busy = true);
    try {
      await widget.api.upload(
        '/api/mobile/status/',
        fields: {'text': caption.text.trim()},
        file: media,
        fileField: 'media',
      );
      if (mounted) Navigator.pop(context, true);
    } catch (e) {
      if (mounted) {
        setState(() => busy = false);
        snack(context, errorText(e));
      }
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Text('New status')),
    body: ListView(
      padding: const EdgeInsets.all(20),
      children: [
        const Text('Visible to signed-in Campus Times users for 24 hours.'),
        const SizedBox(height: 16),
        TextField(
          controller: caption,
          maxLength: 500,
          minLines: 3,
          maxLines: 6,
          decoration: const InputDecoration(
            hintText: 'Share a moment or write an update…',
            border: OutlineInputBorder(),
          ),
        ),
        if (media != null) ...[
          if (socialPhoto(media!.name))
            Image.memory(media!.bytes, height: 250, fit: BoxFit.contain),
          ListTile(
            leading: Icon(socialVideo(media!.name) ? Icons.movie : Icons.photo),
            title: Text(media!.name),
            trailing: IconButton(
              onPressed: busy ? null : () => setState(() => media = null),
              icon: const Icon(Icons.close),
            ),
          ),
        ],
        Wrap(
          spacing: 8,
          children: [
            OutlinedButton.icon(
              onPressed: busy ? null : () => choose(),
              icon: const Icon(Icons.photo_library_outlined),
              label: const Text('Photo / video'),
            ),
            OutlinedButton.icon(
              onPressed: busy ? null : () => choose(source: 'selfie'),
              icon: const Icon(Icons.camera_front),
              label: const Text('Selfie'),
            ),
          ],
        ),
        const SizedBox(height: 20),
        FilledButton(
          onPressed: busy ? null : publish,
          child: Text(busy ? 'Sharing…' : 'Share status'),
        ),
      ],
    ),
  );
}

class StatusViewer extends StatefulWidget {
  const StatusViewer({super.key, required this.api, required this.statuses});
  final CampusApi api;
  final List statuses;
  @override
  State<StatusViewer> createState() => _StatusViewerState();
}

class _StatusViewerState extends State<StatusViewer> {
  late List items;
  int index = 0;
  String? error;
  bool deleting = false;
  @override
  void initState() {
    super.initState();
    items = List.from(widget.statuses);
    mark();
  }

  Future<void> mark() async {
    if (items.isEmpty) return;
    final id = items[index]['id'];
    try {
      final d = await widget.api.post('/api/mobile/status/$id/', {});
      if (mounted && items.isNotEmpty && items[index]['id'] == id)
        setState(() {
          items[index] = d['status'];
          error = null;
        });
    } catch (e) {
      if (mounted) setState(() => error = errorText(e));
    }
  }

  void move(int step) {
    if (index + step < 0) return;
    if (index + step >= items.length) {
      Navigator.pop(context);
      return;
    }
    setState(() => index += step);
    mark();
  }

  Future<void> remove() async {
    final yes = await showDialog<bool>(
      context: context,
      builder: (c) => AlertDialog(
        title: const Text('Delete this status?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(c, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(c, true),
            child: const Text('Delete'),
          ),
        ],
      ),
    );
    if (yes != true || !mounted) return;
    setState(() => deleting = true);
    try {
      widget.api.decode(
        await http
            .delete(
              widget.api.uri('/api/mobile/status/${items[index]['id']}/'),
              headers: widget.api.headers,
            )
            .timeout(const Duration(seconds: 30)),
      );
      if (!mounted) return;
      setState(() {
        items.removeAt(index);
        if (index >= items.length) index = items.length - 1;
      });
      if (items.isEmpty) {
        Navigator.pop(context);
      } else {
        await mark();
      }
    } catch (e) {
      if (mounted) snack(context, errorText(e));
    } finally {
      if (mounted) setState(() => deleting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    if (items.isEmpty) return const Scaffold();
    final s = items[index];
    return Scaffold(
      appBar: AppBar(
        title: Row(
          children: [
            UserAvatar(url: s['avatar'] ?? '', username: s['username']),
            const SizedBox(width: 10),
            Expanded(
              child: Text(s['is_mine'] == true ? 'My status' : s['username']),
            ),
          ],
        ),
      ),
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
              child: Row(
                children: List.generate(
                  items.length,
                  (i) => Expanded(
                    child: Container(
                      height: 4,
                      margin: const EdgeInsets.symmetric(horizontal: 2),
                      color: i <= index ? brand : const Color(0xffdddddd),
                    ),
                  ),
                ),
              ),
            ),
            if (error != null)
              ListTile(
                title: Text(error!),
                trailing: TextButton(
                  onPressed: mark,
                  child: const Text('Retry'),
                ),
              ),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Text(stamp(s['created_at'])),
                    const SizedBox(height: 16),
                    if ((s['media'] ?? '').isNotEmpty)
                      SocialMediaView(
                        key: ValueKey(s['id']),
                        url: s['media'],
                        filename: (s['media_name'] ?? '').toString(),
                      ),
                    if ((s['text'] ?? '').isNotEmpty)
                      Padding(
                        padding: const EdgeInsets.all(20),
                        child: Text(
                          s['text'],
                          textAlign: TextAlign.center,
                          style: TextStyle(
                            fontSize: (s['media'] ?? '').isEmpty ? 28 : 18,
                          ),
                        ),
                      ),
                    if (s['is_mine'] == true)
                      TextButton.icon(
                        onPressed: () => showModalBottomSheet(
                          context: context,
                          builder: (_) => SafeArea(
                            child: ListView(
                              shrinkWrap: true,
                              children: [
                                const ListTile(title: Text('Viewed by')),
                                if ((s['viewers'] ?? []).isEmpty)
                                  const ListTile(title: Text('No views yet')),
                                for (final v in (s['viewers'] ?? []))
                                  ListTile(
                                    leading: const Icon(Icons.person_outline),
                                    title: Text(v['username']),
                                    subtitle: Text(stamp(v['viewed_at'])),
                                  ),
                              ],
                            ),
                          ),
                        ),
                        icon: const Icon(Icons.visibility_outlined),
                        label: Text('${s['view_count'] ?? 0} views'),
                      ),
                  ],
                ),
              ),
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                IconButton(
                  tooltip: 'Previous status',
                  onPressed: index == 0 ? null : () => move(-1),
                  icon: const Icon(Icons.chevron_left),
                ),
                Text('${index + 1} / ${items.length}'),
                if (s['is_mine'] == true)
                  IconButton(
                    tooltip: 'Delete status',
                    onPressed: deleting ? null : remove,
                    icon: const Icon(Icons.delete_outline),
                  ),
                IconButton(
                  tooltip: 'Next status',
                  onPressed: () => move(1),
                  icon: const Icon(Icons.chevron_right),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
