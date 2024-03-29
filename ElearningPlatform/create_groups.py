# create_groups.py

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth.models import Group


def create_groups():
    # List of group names to create
    group_names = ['Student', 'Teacher', 'Admin', 'Specialist']

    for name in group_names:
        group, created = Group.objects.get_or_create(name=name)
        if created:
            print(f"Group '{name}' created successfully.")
        else:
            print(f"Group '{name}' already exists.")


if __name__ == "__main__":
    create_groups()
