import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def set_group_admins(apps, schema_editor):
    Group = apps.get_model('chat', 'Group')
    for group in Group.objects.filter(admin__isnull=True):
        first_member = group.members.order_by('id').first()
        if first_member:
            group.admin_id = first_member.id
            group.save(update_fields=['admin'])


class Migration(migrations.Migration):
    dependencies = [
        ('chat', '0012_statusview_statusview_unique_status_viewer'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField('group', 'admin', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='administered_chat_groups', to=settings.AUTH_USER_MODEL)),
        migrations.AddField('message', 'edited_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('message', 'is_deleted', models.BooleanField(default=False)),
        migrations.AddField('message', 'reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='chat.message')),
        migrations.AddField('message', 'hidden_for', models.ManyToManyField(blank=True, related_name='hidden_chat_messages', to=settings.AUTH_USER_MODEL)),
        migrations.AddField('groupmessage', 'edited_at', models.DateTimeField(blank=True, null=True)),
        migrations.AddField('groupmessage', 'is_deleted', models.BooleanField(default=False)),
        migrations.AddField('groupmessage', 'reply_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='replies', to='chat.groupmessage')),
        migrations.RunPython(set_group_admins, migrations.RunPython.noop),
    ]
