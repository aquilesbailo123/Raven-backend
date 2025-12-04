import os
import django
import sys

def delete_users():
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        django.setup()
    except ImportError:
        print("Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable?")
        sys.exit(1)

    from django.contrib.auth import get_user_model

    User = get_user_model()

    # Filter users who are NOT superusers and NOT staff
    # This ensures admin users are preserved
    users_to_delete = User.objects.filter(is_superuser=False, is_staff=False)
    count = users_to_delete.count()

    if count == 0:
        print("No non-admin users found to delete.")
        return

    print(f"Found {count} non-admin users.")
    print("These users will be permanently deleted.")
    
    # Ask for confirmation
    confirm = input("Are you sure you want to delete them? (yes/no): ")
    
    if confirm.lower() == 'yes':
        # Delete the users
        deleted_count, _ = users_to_delete.delete()
        print(f"Successfully deleted {deleted_count} users.")
    else:
        print("Operation cancelled.")

if __name__ == '__main__':
    delete_users()
