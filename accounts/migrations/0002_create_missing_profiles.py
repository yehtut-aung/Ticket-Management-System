from django.db import migrations
from django.contrib.auth.models import User

def create_user_profiles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    UserProfile = apps.get_model('accounts', 'UserProfile')
    
    for user in User.objects.all():
        UserProfile.objects.get_or_create(
            user=user,
            defaults={'role': 'customer'}
        )

class Migration(migrations.Migration):
    dependencies = [
        ('accounts', '0001_initial'),  # Adjust to your last migration
    ]

    operations = [
        migrations.RunPython(create_user_profiles),
    ]