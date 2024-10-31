from django.test import TestCase, Client
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from .models import User, Profile
from .forms import RegisterForm, ProfileForm
from comments.models import Comment
from music.models import Song, Playlist, PlaylistSong
from django.urls import reverse
from django.contrib.messages import get_messages

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

class UserViewsTest(TestCase):
    def setUp(self):
        # Create a user and admin user
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='admin', password='adminpass', email='admin@example.com')
        self.user = User.objects.create_user(username='testuser', password='userpass', email='user@example.com')
        self.profile=Profile.objects.create(user=self.user)
        Profile.objects.create(user=self.admin_user)

    def test_home_view_as_admin(self):
        # Log in as admin
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('home'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/admin_dashboard.html')
        self.assertIn('users', response.context)
        self.assertIn('total_users', response.context)
        self.assertIn('total_songs', response.context)

    def test_home_view_as_regular_user(self):
        # Log in as regular user
        self.client.login(username='testuser', password='userpass')
        response = self.client.get(reverse('home'))
        
        # Regular users should be redirected to their profile settings
        self.assertRedirects(response, reverse('profile_settings'))

    def test_admin_dashboard_search(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('admin_dashboard') + '?search=testuser')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['users'].count(), 1)  # Only 'testuser' should match search

    def test_delete_user_view(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('delete_user', args=[self.user.id]))

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertEqual(self.user.username, f'deactivated_user_{self.user.id}')
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_manage_songs_view(self):
        # Test GET request with no songs added
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('manage_songs'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/manage_songs.html')
        self.assertEqual(response.context['songs'].count(), 0)  # No songs added yet

    def test_manage_reported_comments_view(self):
        # Create a reported comment and test admin access to reported comments
        comment = Comment.objects.create(user=self.user, profile=self.profile, message="Reported comment", report_count=2)
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('reported_comments'))
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/reported_comments.html')
        self.assertEqual(response.context['reported_comments'].count(), 1)

    def test_register_view(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'email': 'newuser@example.com',
            'full_name': 'new user'
        })

        self.assertEqual(response.status_code, 200)  # Success
        new_user = User.objects.filter(username='newuser').exists()
        self.assertTrue(new_user)

    def test_login_view_with_valid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'userpass'
        })

        self.assertEqual(response.status_code, 302) 

    def test_login_view_with_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 200)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Invalid login details." in str(msg) for msg in messages))

    def test_search_view(self):
        self.client.login(username='testuser', password='userpass')
        response = self.client.get(reverse('search') + '?query=testuser')
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/search_results.html')
        self.assertEqual(response.context['users'].count(), 1)

    def test_profile_view(self):
        self.client.login(username='testuser', password='userpass')
        response = self.client.get(reverse('profile', args=['testuser']))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertEqual(response.context['user_profile'].user.username, 'testuser')

    def test_profile_settings_view(self):
        self.client.login(username='testuser', password='userpass')
        response = self.client.get(reverse('profile_settings'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile_settings.html')

class RegisterFormTest(TestCase):
    
    def test_valid_registration_form(self):
        form_data = {
            'full_name': 'Test User',
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'securePassword123',
            'password2': 'securePassword123'
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_missing_email(self):
        form_data = {
            'full_name': 'Test User',
            'username': 'testuser',
            'password1': 'securePassword123',
            'password2': 'securePassword123'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
    def test_invalid_email_format(self):
        form_data = {
            'full_name': 'Test User',
            'username': 'testuser',
            'email': 'invalid-email-format',
            'password1': 'securePassword123',
            'password2': 'securePassword123'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_email_already_exists(self):
        User.objects.create_user(username='existinguser', email='existing@example.com', password='password123')
        form_data = {
            'full_name': 'New User',
            'username': 'newuser',
            'email': 'existing@example.com',
            'password1': 'securePassword123',
            'password2': 'securePassword123'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_password_mismatch(self):
        form_data = {
            'full_name': 'Test User',
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password1': 'securePassword123',
            'password2': 'differentPassword123'
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

class ProfileFormTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com',  password='password123')
        self.profile = Profile.objects.create(user=self.user)
    
    def test_valid_profile_form(self):
        form_data = {
            'bio': 'This is a test bio',
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
    
    def test_avatar_file_upload_optional(self):
        form_data = {
            'bio': 'Another test bio',
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
    
    def test_empty_bio(self):
        form_data = {
            'bio': '',
        }
        form = ProfileForm(data=form_data, instance=self.profile)
        self.assertTrue(form.is_valid())
    
    def test_invalid_avatar_file_type(self):
        # Simulating invalid file type by passing non-image data
        form_data = {
            'bio': 'Valid bio',
        }
        form_files = {
            'avatar_file': 'not_an_image.txt'  # Simulating a non-image file input
        }
        form = ProfileForm(data=form_data, files=form_files, instance=self.profile)
        self.assertFalse(form.is_valid())
        self.assertIn('avatar_file', form.errors)