import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('chat', '0010_mobileapitoken'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name='SocialNotification', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('kind', models.CharField(choices=[('like','like'),('comment','comment'),('follow','follow'),('message','message'),('group','group'),('system','system')], default='system', max_length=20)), ('text', models.CharField(max_length=255)), ('target_url', models.CharField(blank=True, max_length=500)), ('is_read', models.BooleanField(default=False)), ('created_at', models.DateTimeField(auto_now_add=True)), ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_social_notifications', to=settings.AUTH_USER_MODEL)), ('recipient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='social_notifications', to=settings.AUTH_USER_MODEL))], options={'ordering': ['-created_at']})]
