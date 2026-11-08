from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('home', '0027_alter_meep_body_comment')]
    operations = [migrations.AddField(model_name='meep', name='attachment', field=models.FileField(blank=True, null=True, upload_to='feed_attachments/'))]
