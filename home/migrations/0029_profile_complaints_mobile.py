from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [('home','0028_meep_attachment'), ('auth','0012_alter_user_first_name_max_length')]
    operations = [
        migrations.AddField(model_name='profile', name='home_address', field=models.CharField(max_length=300, blank=True, default='')),
        migrations.AddField(model_name='profile', name='relationship_status', field=models.CharField(max_length=80, blank=True, default='')),
        migrations.AddField(model_name='profile', name='education_status', field=models.CharField(max_length=300, blank=True, default='')),
        migrations.AddField(model_name='complaint', name='user', field=models.ForeignKey(to='auth.user', null=True, blank=True, on_delete=django.db.models.deletion.SET_NULL, related_name='campus_complaints')),
        migrations.AddField(model_name='complaint', name='attachment', field=models.FileField(upload_to='complaints/', null=True, blank=True)),
        migrations.AddField(model_name='complaint', name='status', field=models.CharField(max_length=20, default='open', choices=[('open','Open'),('in_progress','In progress'),('resolved','Resolved')])),
    ]
