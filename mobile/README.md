# Latest social update

See `../SOCIAL_UPDATE_README.md`. Run `python manage.py migrate` in the backend project before using the updated app.

# Campus Times: Android testing

## Tested toolchain

Use Flutter **3.47.5** (Dart 3.13.4), JDK **21**, and Android SDK installed through Android Studio. The project uses Android Gradle Plugin 9.1.0, Kotlin 2.4.0 and Gradle 9.3.1. Keep pubspec.lock so package versions stay consistent. Older Flutter installations are rejected explicitly by pubspec.yaml instead of failing later in Gradle.

Run `flutter doctor -v` and resolve Android toolchain problems, then accept licenses with `flutter doctor --android-licenses`. Select JDK 21 using `flutter config --jdk-dir=/absolute/path/to/jdk-21` if necessary. Initial builds need internet to download packages and Android tools.

## Build your APK on Kali/Linux

From the extracted project:

```bash
cd Campus-Times-Complete/mobile
flutter clean
flutter pub get
flutter build apk --release
```

APK: `build/app/outputs/flutter-apk/app-release.apk`.

This release-mode APK uses a debug signing key for local testing. It is not a Play Store release. Resource shrinking is disabled and Gradle uses one worker to reduce build memory pressure. Do not run `flutter create .` over the project or replace its Gradle files.

## Connect a physical Android phone

1. Connect the phone and computer to the same Wi-Fi network.
2. Find the computer's LAN address with `hostname -I` (for example `192.168.1.20`).
3. In the Django project root, activate your existing Python environment and run:

```bash
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,10.0.2.2,192.168.1.20
python manage.py migrate
python manage.py runserver 0.0.0.0:5000
```

Replace `192.168.1.20` with your computer's actual address in both places.

4. Verify `http://192.168.1.20:5000` opens in the phone's browser. If it does not, check the Wi-Fi network and computer firewall for port 5000.
5. Install the APK, open **Backend server** on the login screen, and save `http://192.168.1.20:5000`. Sign in with your Django account.

`localhost` on the phone means the phone itself. `10.0.2.2` is only for the Android emulator. The APK contains the Flutter client; Django must stay running separately. Local HTTP is enabled for testing; use HTTPS for deployment.

## Changes in this repair

- Fixed the saved dark-theme option so the app actually switches themes.
- Android now defaults to the latest known Render service; use **Backend server** to enter another deployment or a local LAN address.
- Chat and feed media viewers now resolve relative Django media paths and use attachment MIME metadata when the API provides it.
- Aligned plugin compile SDKs to API 36 to fix file_picker AAR metadata validation.
- Updated record to 6.2.1-compatible dependencies and retained resolved versions.
- Added path_provider and writable temporary paths for Android voice recordings.
- Used AAC/M4A on Android while retaining Opus/WebM on web.
- Added microphone and coarse/fine location permissions.
- Added persistent backend URL configuration on the login screen.
- Lowered Gradle memory use and worker count; disabled release shrinking for test builds.
- Declared the Flutter/Dart toolchain requirement explicitly.

Device testing is still needed for login, chats, microphone, location and media. Compilation alone does not verify a live Django connection or phone permissions.
