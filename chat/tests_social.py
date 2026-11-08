import io
import shutil
import tempfile
from datetime import timedelta
from PIL import Image
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone
from chat.models import StatusUpdate, StatusView
from home.models import Profile

class SocialUpdatesTests(TestCase):
    def setUp(self):
        self.media = tempfile.mkdtemp()
        self.settings_override = override_settings(MEDIA_ROOT=self.media)
        self.settings_override.enable()
        self.addCleanup(self.settings_override.disable)
        self.addCleanup(shutil.rmtree, self.media)
        self.owner = User.objects.create_user('owner', password='ExamplePass123!')
        self.viewer = User.objects.create_user('viewer', password='ExamplePass123!')
        self.client.force_login(self.owner)

    def test_large_profile_image_with_generic_upload_content_type(self):
        image = io.BytesIO()
        Image.new('RGB', (1500, 1500), 'gray').save(image, format='PNG', compress_level=0)
        self.assertGreater(len(image.getvalue()), 5*1024*1024)
        response = self.client.post('/api/mobile/profile/owner/', {
            'avatar': SimpleUploadedFile('large.png', image.getvalue(), content_type='application/octet-stream')})
        self.assertEqual(response.status_code, 200)
        self.assertIn('large', response.json()['profile']['avatar'])

    def test_invalid_profile_image_rejected(self):
        response = self.client.post('/api/mobile/profile/owner/', {'avatar': SimpleUploadedFile('fake.png', b'not a photo', content_type='image/png')})
        self.assertEqual(response.status_code, 400)

    def test_status_views_are_unique_and_private(self):
        status = StatusUpdate.objects.create(user=self.owner, text='Campus today')
        self.client.force_login(self.viewer)
        for _ in range(2):
            response = self.client.post(f'/api/mobile/status/{status.id}/', {}, content_type='application/json')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(response.json()['status']['viewed'])
            self.assertIsNone(response.json()['status']['view_count'])
        self.assertEqual(StatusView.objects.filter(status=status).count(), 1)
        self.client.force_login(self.owner)
        item = self.client.get('/api/mobile/status/').json()['statuses'][0]
        self.assertEqual(item['view_count'], 1)
        self.assertEqual(item['viewers'][0]['username'], 'viewer')

    def test_status_expiration_and_deletion_permissions(self):
        old = StatusUpdate.objects.create(user=self.owner, text='Expired')
        StatusUpdate.objects.filter(pk=old.pk).update(created_at=timezone.now()-timedelta(hours=25))
        live = StatusUpdate.objects.create(user=self.owner, text='Live')
        self.assertEqual([s['id'] for s in self.client.get('/api/mobile/status/').json()['statuses']], [live.pk])
        self.assertEqual(self.client.post(f'/api/mobile/status/{old.pk}/').status_code, 404)
        self.client.force_login(self.viewer)
        self.assertEqual(self.client.delete(f'/api/mobile/status/{live.pk}/').status_code, 403)
        self.client.force_login(self.owner)
        self.assertEqual(self.client.delete(f'/api/mobile/status/{live.pk}/').status_code, 200)
        self.assertFalse(StatusUpdate.objects.filter(pk=live.pk).exists())

    def test_text_and_media_status_creation(self):
        response = self.client.post('/api/mobile/status/', {'text':'Hello'}, content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()['status']['is_mine'])
        response = self.client.post('/api/mobile/status/', {'media':SimpleUploadedFile('clip.mp4', b'video fixture', content_type='video/mp4')})
        self.assertEqual(response.status_code, 201)
        self.assertIn('.mp4', response.json()['status']['media'])
        self.assertEqual(self.client.post('/api/mobile/status/', {}).status_code, 400)

    def test_chat_returns_current_profile_avatar(self):
        profile, _ = Profile.objects.get_or_create(user=self.viewer)
        profile.profile_image = 'profile-images/viewer.jpg'
        profile.save()
        response = self.client.get('/api/mobile/chat/viewer/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['person']['avatar'].endswith('/profile-images/viewer.jpg'))

    def test_feed_accepts_video_attachment(self):
        response = self.client.post('/api/mobile/feed/', {'body':'Video post', 'attachment':SimpleUploadedFile('video.mp4', b'video fixture', content_type='video/mp4')})
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json()['post']['attachment'].endswith('.mp4'))
