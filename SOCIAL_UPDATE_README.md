# Campus Times social and theme update

## Install this update

Keep a backup of your existing `db.sqlite3` and `media` folder. When replacing an existing installation, keep those files so your current users, chats and uploads are preserved.

Activate your existing backend environment, then run from the Django project root:

```bash
python manage.py migrate
python manage.py runserver 0.0.0.0:5000
```

The migration adds status-view tracking. Update the backend before testing the new APK. Continue using your laptop's LAN address in Django's `DJANGO_ALLOWED_HOSTS` and the app's **Backend server** setting. See `mobile/README.md` for the Android toolchain and network setup.

## New behavior

- Profile photos no longer have the app's 5 MB file-size restriction. The backend validates the actual image rather than relying on an upload MIME header. Hardware, available memory/storage, timeouts and any reverse-proxy limits still apply.
- Feed posts can contain photos or videos. **Photo / video** opens gallery, front-camera selfie, rear-camera photo and video-recording choices. Videos play inline.
- Photos can be edited before posting or sharing: Original, Mono, Sepia, Warm, Cool, Vivid and Soft, plus brightness, contrast, rotation and square crop. These are photo effects applied after capture, not live face-tracking lenses or video effects.
- Direct chat headers display the user's current profile image, refreshed from the server, with initials when unavailable.
- The Feed and Chats screens share a status strip. Tap **Add status** to publish text, a photo, selfie or video. Tap a person's circle to open their updates, and use previous/next controls to browse.
- Statuses disappear from the active list after 24 hours. Authors can see viewers and delete their own statuses. Viewing the same status repeatedly counts once. Other users cannot see the author's viewer list or delete their status.
- Statuses are visible to signed-in Campus Times users, as stated in the composer. Contact-only audience controls are not part of this update.
- The app uses a fixed white/light-gray theme. Previously stored dark-mode preferences no longer change its appearance. Message text and controls use gray/charcoal for readability.

Feed/chat/status media retain the existing 25 MB attachment limit; the removed 5 MB limit applies specifically to profile photos.

## Checks

Backend: seven tests cover a real image larger than 5 MB with generic upload MIME type, invalid image rejection, status creation, expiry, unique/private view tracking, deletion ownership, chat avatars and feed video attachments.

Flutter: eight tests cover backend configuration, light theme/media detection, narrow-phone feed layout, status viewing/posting and exported grayscale photo pixels. Android camera hardware, native video codecs and a live laptop-to-phone network still require device testing.

Run:

```bash
python manage.py test chat.tests_social
cd mobile
flutter test
flutter analyze --no-fatal-infos
flutter build apk --release
```

The Android build remains locally test-signed. Use your own release key before store distribution. Existing third-party CKEditor/Kotlin migration warnings are separate from this feature update.
