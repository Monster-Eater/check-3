import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0030_social_edit_privacy_and_comment_replies'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(model_name='meep', name='client_id', field=models.UUIDField(blank=True, db_index=True, null=True)),
        migrations.AddConstraint(model_name='meep', constraint=models.UniqueConstraint(condition=models.Q(('client_id__isnull', False)), fields=('user', 'client_id'), name='unique_post_client_id')),
        migrations.CreateModel(
            name='PostReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('seen_at', models.DateTimeField(blank=True, null=True)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='home.meep')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_receipts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(model_name='postreceipt', constraint=models.UniqueConstraint(fields=('post', 'user'), name='unique_post_receipt')),
    ]
