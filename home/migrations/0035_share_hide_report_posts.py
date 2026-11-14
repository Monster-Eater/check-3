from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('home', '0034_profile_cover_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='meep',
            name='shared_post',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reshares', to='home.meep'),
        ),
        migrations.CreateModel(
            name='HiddenPost',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hidden_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hidden_by', to='home.meep')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hidden_posts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PostReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(choices=[('spam', 'Spam'), ('harassment', 'Harassment or bullying'), ('hate', 'Hate speech or abuse'), ('violence', 'Violence or dangerous content'), ('misinformation', 'False information'), ('other', 'Other')], max_length=24)),
                ('details', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('open', 'Open'), ('reviewing', 'Reviewing'), ('resolved', 'Resolved'), ('dismissed', 'Dismissed')], default='open', max_length=16)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reports', to='home.meep')),
                ('reporter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_reports', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddConstraint(
            model_name='hiddenpost',
            constraint=models.UniqueConstraint(fields=('user', 'post'), name='unique_hidden_post_per_user'),
        ),
        migrations.AddConstraint(
            model_name='postreport',
            constraint=models.UniqueConstraint(fields=('reporter', 'post'), name='unique_post_report_per_user'),
        ),
    ]
