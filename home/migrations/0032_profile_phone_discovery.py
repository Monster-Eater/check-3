from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
    ('home', '0001_initial'),
]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='phone_number',
            field=models.CharField(blank=True, default='', max_length=32),
        ),
        migrations.AddField(
            model_name='profile',
            name='phone_discoverable',
            field=models.BooleanField(default=False),
        ),
    ]
