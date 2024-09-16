import os
import django
import sqlite3

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()

from app.models import User, Profile

def main():
    
    user = User(username="test_user", full_name="Test User", email="test@uni.sydney.edu.au", password="test")
    user.save()

    print(user.id, user)
    User.objects.all()

if __name__ == "__main__":
    main()

