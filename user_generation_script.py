"""
This script is used to generate random users for testing purposes.
"""

import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "social_networking_app.settings")
django.setup()

from django.contrib.auth.models import User


def create_users(num_users=100):
    for i in range(num_users):
        first_name = f"user_{i}"
        username = f"{first_name}@example.com"
        email = f"{first_name}@example.com"
        password = "Test@123"

        # Create the user
        user = User.objects.create_user(
            first_name=first_name, username=username, email=email, password=password
        )
        print(f"Created user: {username}")


if __name__ == "__main__":
    create_users()
