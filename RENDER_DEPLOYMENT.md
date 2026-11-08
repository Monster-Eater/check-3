# Deploy Campus Times on Render

This project is configured as a Render Blueprint. Push the project to GitHub, then in Render choose **New + → Blueprint**, connect the repository, and apply `render.yaml`. It creates a Django web service and PostgreSQL database. The blueprint generates a secret key; do not put secrets in Git. If you deployed the web service manually, create a Render PostgreSQL database and set the service's `DATABASE_URL` to that database's **Internal Database URL**.

The Render build command must run `./build.sh`; it installs `requirements.txt`, applies migrations, and collects static files. After the first deploy, open the service URL ending in `.onrender.com`. The root page should load, and Flutter can use the same HTTPS URL as its API server.

## APK build

From `mobile/` on a computer with the Android toolchain installed:

```bash
flutter pub get
flutter build apk --release --dart-define=API_BASE_URL=https://YOUR-SERVICE.onrender.com
```

The APK is created at `mobile/build/app/outputs/flutter-apk/app-release.apk`. Replace `YOUR-SERVICE` with the exact Render hostname. Alternatively, leave out the define and have each user set the HTTPS server URL under **Backend server** on the login screen. Keep the signing configuration for private testing; Play Store distribution needs your own release keystore.

## Before inviting users

- Render's local filesystem is temporary. To preserve profile photos, videos, chat attachments and complaint files across deploys, configure an S3-compatible bucket in the Render service environment with `AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, and `AWS_SECRET_ACCESS_KEY`. Set `AWS_S3_REGION_NAME`; for providers such as Cloudflare R2, also set `AWS_S3_ENDPOINT_URL`. Without this, uploads use the temporary local filesystem. Static site files are collected and served by WhiteNoise.
- Create an admin account with `python manage.py createsuperuser` using a one-off shell after deployment.
- If Flutter Web is hosted on a different domain, add its exact HTTPS origin to `DJANGO_CORS_ALLOWED_ORIGINS` and `DJANGO_CSRF_TRUSTED_ORIGINS` in the Render service environment, then redeploy.
- Render free services may sleep when idle, so the first request after inactivity can take a little longer.
