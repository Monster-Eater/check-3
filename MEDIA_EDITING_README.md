# Media editing update

New in private and group chats:
- Photos: rotate, square center crop, brightness, contrast, preview and cancel.
- Videos: select a trim range, preview where supported, and export an MP4 using the Django backend and FFmpeg.

Install FFmpeg on Kali: `sudo apt install ffmpeg`

Run Django on port 5000 and Flutter Web on 5500. Both endpoints require a valid bearer token. Files are limited to 25 MB, and clips must be at least 0.5 seconds long. Video processing may take time. The exported video is uploaded to the existing chat endpoint only after editing is accepted.

Important: Flutter SDK is not installed in this environment, so Flutter analyzer/build and real browser media tests could not be executed. Back up your working database and media before replacing project files.
