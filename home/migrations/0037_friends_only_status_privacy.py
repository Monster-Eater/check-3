from django.db import migrations, models


def make_existing_statuses_friends_only(apps, schema_editor):
    Profile = apps.get_model('home', 'Profile')
    Profile.objects.filter(status_privacy__in=['everyone', 'followers']).update(status_privacy='friends')


class Migration(migrations.Migration):
    dependencies = [('home', '0036_store_catalog_orders')]

    operations = [
        migrations.RunPython(make_existing_statuses_friends_only, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='profile',
            name='status_privacy',
            field=models.CharField(
                choices=[('friends', 'Friends only'), ('nobody', 'Nobody')],
                default='friends',
                max_length=16,
            ),
        ),
    ]
