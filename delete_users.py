import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fileshare.settings')
django.setup()

from django.contrib.auth import get_user_model

def delete_all_non_superusers():
    User = get_user_model()
    # Delete all non-superuser accounts
    deleted = User.objects.filter(is_superuser=False).delete()
    print(f"Successfully deleted {deleted[0]} users")

if __name__ == "__main__":
    delete_all_non_superusers()
