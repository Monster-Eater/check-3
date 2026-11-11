# Render setup for live messaging and offline sync

This version serves HTTP and WebSockets through Daphne/ASGI. The Render service must use the repository root as its root directory.

## Render configuration

1. Create a Render **Key Value** service. Copy its **internal Redis URL** into the web service environment as `REDIS_URL`.
2. Keep the existing PostgreSQL `DATABASE_URL`. Add `DJANGO_DEBUG=0`, a strong `DJANGO_SECRET_KEY`, and `DJANGO_ALLOWED_HOSTS` containing the Render hostname (for example `check-2-yy78.onrender.com`). Set `DJANGO_CSRF_TRUSTED_ORIGINS=https://check-2-yy78.onrender.com`. If Flutter Web is hosted on another origin, include its full origin in `DJANGO_WS_ALLOWED_ORIGINS` (comma separated).
3. Add Cloudinary credentials (`CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, `CLOUDINARY_API_SECRET`) or configure S3. Production now refuses local-only media storage because Render's application filesystem is ephemeral and would make uploaded media disappear or return 404 after a restart/deploy.
4. Set Build Command to `pip install -r requirements.txt`.
5. Set Pre-Deploy Command to `python manage.py migrate`.
6. Set Start Command to `daphne -b 0.0.0.0 -p $PORT pr_campus_times.asgi:application`.

Do not use the old Gunicorn WSGI start command: it serves HTTP but cannot handle this app's WebSocket routes. Deploy after Redis and persistent media storage are configured.

## Flutter client

From the `mobile` directory run `flutter pub get` before building. The client stores retryable post and chat requests in a local Sembast database (IndexedDB on web and an app-private database file on Android). Text posts and text chat messages use the WebSocket when connected. Attachments are retained locally and retried as multipart uploads; the server uses client IDs to prevent duplicate posts/messages after a retry.

## Receipts

- Direct messages are marked delivered when the recipient connects or receives a live event, and seen when the conversation is open and the server records its read time.
- Group messages record per-member delivery and seen timestamps.
- Feed posts are marked delivered from the feed snapshot and marked seen when at least 55% of the card is visible. Authors see aggregate seen counts on their own posts.

Redis is required for cross-process socket delivery; the in-memory channel layer is only used for local `DJANGO_DEBUG=1` development.
