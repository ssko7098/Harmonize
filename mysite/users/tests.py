from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from .models import User, Profile

class UserModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
    
    def test_user_creation(self):
        """Test that a user is created with correct field values."""
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.check_password('password123'))
        self.assertTrue(self.user.is_active)
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_superuser)

    def test_create_superuser(self):
        """Test that a superuser is created with is_admin and is_superuser set to True."""
        superuser = User.objects.create_superuser(username='superuser', email='super@example.com', password='superpass')
        self.assertTrue(superuser.is_admin)
        self.assertTrue(superuser.is_superuser)
        self.assertEqual(superuser.email, 'super@example.com')

    def test_user_string_representation(self):
        """Test that the string representation of the user model is the email."""
        self.assertEqual(str(self.user), 'test@example.com')

    def test_is_staff_property(self):
        """Test that the is_staff property reflects the is_admin field value."""
        self.assertFalse(self.user.is_staff)
        self.user.is_admin = True
        self.assertTrue(self.user.is_staff)

    def test_user_email_unique_constraint(self):
        """Test that creating a user with an existing email raises an error."""
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='testuser2', email='test@example.com', password='password123')


class ProfileModelTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')
        self.profile = Profile.objects.create(user=self.user)

    def test_profile_creation(self):
        """Test that a profile is created with default values"""
        self.assertEqual(self.profile.user, self.user)
        self.assertEqual(self.profile.bio, None)
        self.assertEqual(self.profile.report_count, 0)

    def test_profile_string_representation(self):
        """Test that the string representation of the profile model is the username."""
        self.assertEqual(str(self.profile), 'testuser')

    def test_reported_by_relationship(self):
        """Test that a user can be added to the reported_by ManyToMany field of a profile."""
        reporting_user = User.objects.create_user(username='reportinguser', email='reporting@example.com', password='password')
        self.profile.reported_by.add(reporting_user)
        self.assertIn(reporting_user, self.profile.reported_by.all())

