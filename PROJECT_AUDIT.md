# Campus Times — project audit (2026-11-07)

## Scope inspected
- Django project configuration, URL routing, models, API handlers and migrations.
- Flutter application source, package manifest/lockfile, Android and iOS project files.
- Bundled SQLite database and archive integrity.

## Changes made in this audit copy
1. Added the missing `matplotlib` and `seaborn` runtime dependencies. `home/views.py` imports both at module import time; without them a clean Django installation can fail while importing the URL configuration.
2. Updated Flutter API URL normalization so a configured base URL with a trailing slash does not create malformed double-slash endpoints.
3. Added 30-second timeouts to JSON API calls.
4. Changed saved-token restoration so a temporary network/server outage does not erase a valid local login token. A confirmed HTTP 401 still clears it.
5. Fixed the direct-chat initial loading state so a failed first request stops the infinite spinner and exposes the retry action.
6. Added debounce and stale-response protection to contacts search, preventing one HTTP request per keystroke and preventing older search results from overwriting newer results.
7. Prevented duplicate group-file uploads while an upload is already in progress.
8. Added Flutter-generated, machine-specific paths and caches to `.gitignore`; removed generated cache files from this distribution so they are recreated on the target machine.

## Existing data verified in the supplied database
`PRAGMA integrity_check` returns `ok`. The database contains:
- 6 user accounts
- 16 feed posts
- 79 direct chat messages
- 1 group
- 19 group messages
- 3 status updates

The database is included unchanged in this audit package. Do not delete it.

## Migrations still required on the target database
The supplied database has not yet applied these migrations:
- `chat.0010_mobileapitoken`
- `chat.0011_socialnotification`
- `home.0028_meep_attachment`

Run `python manage.py migrate` against this same database file before using the mobile API. These migrations add API-token storage, notifications and feed attachments; they do not recreate the existing users/messages.

## Static checks completed here
- ZIP archive CRC/integrity: passed.
- Python `compileall`: passed.
- SQLite integrity check: passed.
- Android manifest and iOS Info.plist XML parsing: passed.
- Source-level inspection of Flutter/Django API routes and response fields: completed.

## Checks that could not be executed here
This environment does not contain the Flutter or Dart SDK, and Django is not installed. Network access to install missing packages is unavailable. Therefore these commands have **not** been executed here:
- `flutter analyze`
- `flutter test`
- `flutter build web`
- `python manage.py check`
- `python manage.py migrate` against the bundled DB
- authenticated end-to-end tests through a running Django server and browser

Do not interpret source inspection as a successful Flutter build or runtime test. Run the verification commands in the README on the Kali machine where Flutter/Django are installed.

## Known feature gaps — not a full Facebook/WhatsApp feature-equivalent clone
The present app is a working-scope foundation, not feature parity with either commercial service. The following remain unimplemented or partial:
- No voice/video calling (intentionally excluded).
- Notifications are in-app polling only; no Firebase/Web Push delivery.
- Chat uses HTTP polling, not WebSockets; real-time delivery/typing/presence can lag.
- No end-to-end encryption; do not use for confidential communications.
- No message edit/delete, message search, reactions, reply/thread, forwarding, pinning, disappearing messages, or per-message read receipts in group chats.
- No group roles/admin controls, invite links, group descriptions/rules editing, or leave-group workflow in Flutter.
- No image/video inline preview in chat; attachments open by URL. Feed attachment rendering currently treats attachments as images first and falls back to a file link.
- No Flutter UI for uploading profile avatars or media statuses, although the backend accepts those fields.
- No post edit/delete, privacy audience controls, blocking/reporting/moderation workflow, or feed pagination.
- No registration/password-reset UI; sign-in uses existing Django accounts.
- Uploaded media is served using Django's normal media URL configuration; production deployments must secure private chat attachments and use HTTPS/object storage, file-type validation and malware scanning.
- No automated test suite currently exercises the added mobile API endpoints.

## Local Kali run configuration
Django API: `http://127.0.0.1:5000`
Flutter Web: `http://localhost:5500`

The Flutter web origin `http://localhost:5500` and `http://127.0.0.1:5500` is allowed by the development CORS middleware. For a phone or LAN client, configure `API_BASE_URL` to the Kali machine's LAN address and add that host to `DJANGO_ALLOWED_HOSTS`; do not use `127.0.0.1` on a separate device.

## Production warning
The current settings default to `DEBUG=1` and a development secret key. Do not expose this server to the public internet until `DEBUG=0`, a strong secret, strict `ALLOWED_HOSTS`/CORS, HTTPS, rate limiting, secure media access and production database/storage configuration are in place.
