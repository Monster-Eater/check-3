from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('home', '0033_delete_donate'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='cover_image',
            field=models.ImageField(blank=True, null=True, upload_to='profile-covers/'),
        ),
    ]
