# Campus Times — complete social + messaging project

Campus Times is the existing Django campus portal extended with a Flutter Web/mobile social feed and messaging client. It reuses the existing Django authentication, users, feed posts, follows, comments, private messages, groups, status updates, SQLite database and uploaded media.

## Included features

### Social feed
- Create text posts and posts with a file/image attachment.
- Feed history, likes/unlikes, comments and reshare-to-feed.
- People search, profiles, follower/following counts and follow/unfollow.
- Profile bio editing and 24-hour text status updates.

### Messaging
- One-to-one text messages and file/image/document attachments.
- Existing private message history is read from the existing `chat.Message` table; messages are not copied into a new table.
- Group creation, selecting initial members, adding members and group message history.
- Online/last-seen and typing indicators, direct-message read state and unread counts.
- In-app notification inbox for likes, comments, follows, private messages and group messages.

### Explicitly not included
- No voice or video calling.
- No Firebase/browser push notification setup; notifications are in-app and the app polls for updates.
- No end-to-end encryption. Do not treat this as a secure messenger for confidential communications.
- This is a practical campus social app foundation, not a replica of every Facebook/WhatsApp feature.

## Preserve your existing data

The project bundle includes the existing `db.sqlite3` and `media/` directory. Back them up before applying migrations or replacing files. The current database contains existing users, feed posts, comments, private chat messages and groups. The API reads those same records.

**Never delete `db.sqlite3` or `media/` when updating the code.** The new migrations only add a feed attachment field and a notification table.

## Run on Kali Linux (Flutter Web)

Django and Flutter cannot both listen on port 5000. This configuration uses Django on **5000** and Flutter Web on **5500**.

### 1. Backend dependencies

From the directory containing `manage.py`:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

If you already have a working virtual environment, activate it instead of creating another one. Copy `.env.example` to `.env` and set a private `DJANGO_SECRET_KEY`. The default key is only for local development.

### 2. Database migrations

```bash
python manage.py migrate
python manage.py check
```

This applies `chat.0010_mobileapitoken`, `chat.0011_socialnotification`, and `home.0028_meep_attachment` as needed. It does not reset existing messages or users.

### 3. Start Django

```bash
python manage.py runserver 0.0.0.0:5000
```

### 4. Start Flutter Web in a second terminal

```bash
cd mobile
flutter clean
flutter pub get
flutter analyze
flutter run -d web-server --web-hostname 0.0.0.0 --web-port 5500 \
  --dart-define=API_BASE_URL=http://127.0.0.1:5000
```

Open the Flutter URL (normally `http://localhost:5500`). Sign in using an existing Django username and password. Do not use port 5000 for Flutter while Django is running on port 5000.

## Android emulator / physical phone

- Android emulator: `--dart-define=API_BASE_URL=http://10.0.2.2:5000`
- Physical phone: use your Kali machine's LAN IP, e.g. `--dart-define=API_BASE_URL=http://192.168.1.20:5000`, allow that port through your local firewall, and add that LAN IP to `DJANGO_ALLOWED_HOSTS` in `.env` (for example `DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,192.168.1.20`).
- For Flutter Web opened from a LAN address, the development CORS middleware accepts private-network origins. Restrict the allowed origins before deploying publicly.

## API endpoints added/used

All endpoints except login require `Authorization: Bearer <token>`.

| Endpoint | Purpose |
|---|---|
| `POST /api/mobile/login/` | Existing-user login and token issue |
| `GET/PATCH/DELETE /api/mobile/me/` | Current user, profile updates, logout |
| `GET/POST /api/mobile/feed/` | Feed history and post creation |
| `POST /api/mobile/feed/<id>/like/` | Like/unlike |
| `GET/POST /api/mobile/feed/<id>/comments/` | Comments |
| `POST /api/mobile/feed/<id>/share/` | Reshare into the current user's feed |
| `GET /api/mobile/contacts/` | People list, latest message and unread count |
| `GET/POST /api/mobile/chat/<username>/` | Direct message history and send |
| `POST /api/mobile/chat/<username>/presence/` | Typing/presence update |
| `GET/POST /api/mobile/groups/` | Group list and creation |
| `GET/POST /api/mobile/groups/<id>/` | Group message history and send |
| `POST /api/mobile/groups/<id>/members/` | Add members |
| `GET/POST /api/mobile/notifications/` | Notification list and mark-all-read |
| `GET/POST /api/mobile/status/` | 24-hour status updates |
| `GET /api/mobile/search/?q=...` | Search users and posts |
| `GET/POST /api/mobile/profile/<username>/` | Profile view and own bio update |
| `POST /api/mobile/profile/<username>/follow/` | Follow/unfollow |

Attachments are limited to 25 MB per request by the API. Increase this only after configuring Django/web-server upload limits and validating file types for your deployment.

## Before production deployment

- Set `DJANGO_DEBUG=0`, a strong secret key and explicit `DJANGO_ALLOWED_HOSTS`.
- Configure HTTPS, secure cookies, reverse-proxy upload limits, rate limiting and backups.
- Replace development CORS allowances with the exact trusted frontend origin(s).
- Add server-side file-type scanning/validation and storage controls.
- Configure a push provider (e.g. Firebase) if real device push notifications are required.
- Use PostgreSQL for multi-user production traffic and consider WebSockets for true real-time chat.

## Validation status

See `PROJECT_AUDIT.md` for the detailed verification record, remaining migrations, and known feature gaps. This package has not been represented as a fully built/tested production Facebook/WhatsApp clone: run the Flutter and Django checks on the Kali machine before relying on it.
