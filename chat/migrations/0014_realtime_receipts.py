import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0013_chat_actions_privacy'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(model_name='message', name='client_id', field=models.UUIDField(blank=True, db_index=True, null=True)),
        migrations.AddField(model_name='message', name='delivered_at', field=models.DateTimeField(blank=True, null=True)),
        migrations.AddField(model_name='groupmessage', name='client_id', field=models.UUIDField(blank=True, db_index=True, null=True)),
        migrations.AddConstraint(model_name='message', constraint=models.UniqueConstraint(condition=models.Q(('client_id__isnull', False)), fields=('sender', 'client_id'), name='unique_direct_client_message')),
        migrations.AddConstraint(model_name='groupmessage', constraint=models.UniqueConstraint(condition=models.Q(('client_id__isnull', False)), fields=('group', 'sender', 'client_id'), name='unique_group_client_message')),
        migrations.CreateModel(
            name='GroupMessageReceipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delivered_at', models.DateTimeField(blank=True, null=True)),
                ('seen_at', models.DateTimeField(blank=True, null=True)),
                ('message', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receipts', to='chat.groupmessage')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='group_message_receipts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddConstraint(model_name='groupmessagereceipt', constraint=models.UniqueConstraint(fields=('message', 'user'), name='unique_group_message_receipt')),
    ]
