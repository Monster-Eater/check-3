import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0029_profile_complaints_mobile'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField('profile', 'last_seen_privacy', models.CharField(choices=[('everyone', 'Everyone'), ('followers', 'Followers'), ('nobody', 'Nobody')], default='everyone', max_length=16)),
        migrations.AddField('profile', 'read_receipts', models.BooleanField(default=True)),
        migrations.AddField('profile', 'status_privacy', models.CharField(choices=[('everyone', 'Everyone'), ('followers', 'Followers'), ('nobody', 'Nobody')], default='everyone', max_length=16)),
        migrations.AddField('meep', 'edited_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('comment', 'parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='replies', to='home.comment')),
        migrations.AddField('comment', 'updated_at', models.DateTimeField(auto_now=True)),
        migrations.AddField('comment', 'user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='social_comments', to=settings.AUTH_USER_MODEL)),
    ]
