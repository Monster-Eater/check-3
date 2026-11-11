# Render and Cloudinary setup

The Django project uses Cloudinary as its media storage when Cloudinary credentials are present. Without credentials it uses local media storage for development. Production now stops at startup if Cloudinary or S3 is missing: Render's app filesystem is temporary, and local media URLs would disappear or return 404 after restarts/deploys.

## Configure Render

1. Create a Cloudinary account and copy the cloud name, API key, and API secret from its dashboard.
2. In Render, open the Django web service and choose **Environment**.
3. Add these environment variables as secret values:
   - `CLOUDINARY_CLOUD_NAME`
   - `CLOUDINARY_API_KEY`
   - `CLOUDINARY_API_SECRET`
4. Save the changes and deploy the service. Alternatively, set `CLOUDINARY_URL` instead of the three separate values.
5. After the deployment, verify that newly uploaded profile pictures, feed attachments, statuses, chat files, and group icons appear on the app.

Do not commit the real credentials or put them in this ZIP. Keep them only in Render's environment settings. Existing uploads in Render's local disk are not copied automatically; this change affects new uploads after Cloudinary is configured.

## Database migrations

The added group, privacy, message, post, and comment fields require Django migrations. Run `python manage.py migrate` as a Render pre-deploy command or from the deployed service shell after the code is deployed.

For Django Channels, Redis, Daphne and Flutter offline-sync setup, see [RENDER_REALTIME_SETUP.md](RENDER_REALTIME_SETUP.md).
