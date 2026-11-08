# Campus Times signup update

This update adds a **Create a new account** button to the Flutter login screen and a Django `POST /api/mobile/signup/` endpoint. New accounts are created in the existing Django auth database, with password validation, username/email uniqueness checks, and a token for automatic sign-in.

## Run on Kali

From the directory containing `manage.py`:

```bash
python3 manage.py check
python3 manage.py migrate
python3 manage.py runserver 0.0.0.0:5000
```

From `mobile/` in another terminal:

```bash
flutter pub get
flutter analyze
flutter run -d web-server --web-port 5500 --dart-define=API_BASE_URL=http://127.0.0.1:5000
```

Go to http://127.0.0.1:5500, select **Create a new account**, complete the form and submit.

## Validation and scope

- Backend Python syntax checked.
- Existing database and media preserved.
- Flutter SDK and Django runtime unavailable here: `flutter analyze`, Flutter build, `manage.py check`, migrations and end-to-end tests were **not** run.
- This update implements signup only. Previously requested advanced chat features — microphone voice recording/playback, direct camera capture, media editing before sending, and device-location sharing — remain **not implemented**. Existing private/group chat file attachments remain in the project.
- Browser microphone, camera and geolocation require user permissions and generally a secure HTTPS origin outside localhost.
