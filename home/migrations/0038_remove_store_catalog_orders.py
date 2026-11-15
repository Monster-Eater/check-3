from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [('home', '0037_friends_only_status_privacy')]

    operations = [
        migrations.DeleteModel(name='StoreOrderItem'),
        migrations.DeleteModel(name='StoreOrder'),
        migrations.DeleteModel(name='StoreProduct'),
        migrations.DeleteModel(name='StoreSubcategory'),
        migrations.DeleteModel(name='StoreCategory'),
    ]
