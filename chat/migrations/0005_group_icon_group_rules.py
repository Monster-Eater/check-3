from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_alter_groupmessage_message'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='icon',
            field=models.FileField(blank=True, null=True, upload_to='group_icons/'),
        ),
        migrations.AddField(
            model_name='group',
            name='rules',
            field=models.TextField(blank=True),
        ),
    ]
