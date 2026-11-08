# Campus Times repair report — 2026-11-07

## Changes made
- Corrected the three `const_with_non_const` analyzer errors in `mobile/lib/main.dart` (contacts, groups, and notifications empty-state ListViews).
- Replaced the deprecated `withOpacity(.05)` call with `withValues(alpha: .05)`.
- Added `mounted` checks to relevant asynchronous UI paths, including chat attachments, group-member dialog, login, and file selection; guarded snackbar calls after asynchronous operations.
- Preserved the existing SQLite database and media directory.

## Checks performed here
- Python `compileall` on Django application and configuration modules: passed.
- SQLite `PRAGMA integrity_check`: `ok`.
- ZIP archive test: see package creation check.

## Checks not performed here
- Flutter SDK is not installed in this environment; `flutter analyze`, `flutter test`, and `flutter build web` could not be executed.
- Django is not installed in this environment; `manage.py check`, migrations, and API integration tests could not be executed.
- Full end-to-end feature verification and security review are still outstanding. No guarantee of zero runtime errors is made.

## Kali commands
From the project root, activate your Python environment and run:

```bash
python -m pip install -r requirements.txt
python manage.py check
python manage.py migrate
python manage.py runserver 0.0.0.0:5000
```

In another terminal:

```bash
cd mobile
flutter pub get
flutter analyze
flutter test
flutter run -d web-server --web-hostname 0.0.0.0 --web-port 5500 --dart-define=API_BASE_URL=http://127.0.0.1:5000
```

Do not expose the development server publicly; configure security settings and production CORS restrictions before deployment.
