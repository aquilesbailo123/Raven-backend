import os
import django
import random

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from users.models import Profile, Incubator, IncubatorMember

User = get_user_model()

def create_incubators():
    incubator_data = [
        {
            "name": "TechStars",
            "email_prefix": "techstars",
            "members": [
                {"name": "David Cohen", "role": "INVESTOR"},
                {"name": "Brad Feld", "role": "MENTOR"},
                {"name": "Nicole Glaros", "role": "BOTH"}
            ]
        },
        {
            "name": "Y Combinator",
            "email_prefix": "ycombinator",
            "members": [
                {"name": "Paul Graham", "role": "INVESTOR"},
                {"name": "Jessica Livingston", "role": "MENTOR"},
                {"name": "Sam Altman", "role": "INVESTOR"}
            ]
        },
        {
            "name": "",
            "email_prefix": "500startups",
            "members": [
            ]
        }
    ]

    print("Creating Incubators...")

    for data in incubator_data:
        email = f"admin@{data['email_prefix']}.com"
        password = "password123"
        
        # Create User
        user, created = User.objects.get_or_create(
            email=email,
            defaults={'username': data['email_prefix']}
        )
        if created:
            user.set_password(password)
            user.save()
            print(f"Created User: {email}")
        else:
            print(f"User {email} already exists.")

        # Create or Update Profile
        profile, _ = Profile.objects.get_or_create(user=user)
        profile.user_type = Profile.INCUBATOR
        profile.save()

        # Create Incubator
        incubator, created = Incubator.objects.get_or_create(profile=profile)
        incubator.name = data['name']
        incubator.save()
        print(f"  -> Linked Incubator: {incubator.name}")

        # Create Members
        for member in data['members']:
            full_name = member['name']
            member_email = f"{full_name.lower().replace(' ', '.')}@{data['email_prefix']}.com"
            role = member['role']
            
            mem_obj, created = IncubatorMember.objects.get_or_create(
                incubator=incubator,
                email=member_email,
                defaults={
                    'full_name': full_name,
                    'phone': f"+1-555-{random.randint(1000, 9999)}",
                    'role': role
                }
            )
            if created:
                print(f"    -> Added Member: {full_name} ({role})")
            else:
                print(f"    -> Member {full_name} already exists.")

    print("\nDone! Created 3 incubators with members.")

if __name__ == "__main__":
    create_incubators()
