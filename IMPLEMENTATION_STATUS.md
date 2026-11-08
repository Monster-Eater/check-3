# Campus Times feature implementation — 2026-11-07

This archive is a **partial implementation**, not a production-verified finished app.

## Implemented in source
- Profile fields: home address, relationship status, education/studies, existing bio and photo upload.
- Password change endpoint with current-password verification and Django password validators.
- Flutter profile editor and profile photo picker.
- Light/dark theme toggle, persisted in SharedPreferences.
- Top-right complaints button, complaint form, optional file upload, user complaint history.
- Django admin complaint list, filtering and status management.
- Existing private/group file attachments remain supported.

## Not yet implemented
- Native camera capture and post-capture photo/video editing.
- Microphone recording, voice-note playback and upload.
- Device location permission and sharing.
- Full Flutter build and end-to-end runtime verification.

## Database and startup
Do not overwrite an existing production database. The supplied SQLite file is retained.
Run `python manage.py migrate` to apply `home/migrations/0029_profile_complaints_mobile.py`.
Run Django on port 5000 and Flutter Web on port 5500.

## Tests performed
Python source compilation passed. ZIP integrity verified after packaging.
Flutter and Django runtime tests not run: Flutter/Django SDK dependencies are not available here.
