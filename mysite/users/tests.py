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
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from unittest.mock import patch
import tempfile

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

    def test_post_valid_profile_update(self):
        self.client.login(username='testuser', password='userpass')
        url = reverse('profile_settings')
        # Simulate POST request with valid data
        with tempfile.NamedTemporaryFile(suffix=".jpg") as temp_image:
            temp_image.write(b'sample image content')
            temp_image.seek(0)
            data = {'bio': 'Updated bio'}
            files = {'avatar_file': temp_image}
            response = self.client.post(url, data, files=files, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        
        # Check that the profile bio is updated and avatar is set
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.bio, 'Updated bio')
        
        # Check for AJAX JSON response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['status'], 'success')
        self.assertEqual(response.json()['message'], 'Profile updated successfully!')

    def test_manage_songs_view_no_permission(self):
        # Regular user tries to access admin-only view
        self.client.login(username='testuser', password='userpass')
        response = self.client.get(reverse('manage_songs'))
        self.assertEqual(response.status_code, 302)  # redirect
    
    def test_clear_profile_reports(self):
        reported_user = User.objects.create_user(username='reporteduser', password='userpass', email='reported@example.com')
        profile = Profile.objects.create(user=reported_user, report_count=3)

        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('admin_dashboard'), {'clear_reports': 'true', 'profile_id': self.profile.id})
       
        # Refresh the profile and check that the report count is cleared
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.report_count, 0)
        self.assertEqual(self.profile.reported_by.count(), 0)
        self.assertEqual(response.status_code, 200)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Profile reports have been cleared" in str(msg) for msg in messages))

    def test_clear_reports_no_profile_id(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('admin_dashboard'), {'clear_reports': 'true'})
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("No Profile selected for clearing." in str(msg) for msg in messages))
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_clear_song_reports(self):
        # Load the actual file from 'music/mp3/test.mp3' as mp3_file
        with open("music/mp3/test.mp3", "rb") as mp3_file:
            mock_mp3_file = SimpleUploadedFile("test.mp3", mp3_file.read(), content_type="audio/mpeg")
        
        song = Song.objects.create(user=self.user, title='Test Song', mp3_file=mock_mp3_file, report_count=2)

        # Log in as admin and clear song reports
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('manage_songs'), {'clear_reports': 'true', 'song_id': song.song_id})

        # Refresh the song and check that the report count is cleared
        song.refresh_from_db()
        self.assertEqual(song.report_count, 0)
        self.assertEqual(song.reported_by.count(), 0)
        self.assertEqual(response.status_code, 200)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Song reports have been cleared" in str(msg) for msg in messages))

    def test_delete_song_as_admin(self):
        with open("music/mp3/test.mp3", "rb") as mp3_file:
            mock_mp3_file = SimpleUploadedFile("test.mp3", mp3_file.read(), content_type="audio/mpeg")
        
        song = Song.objects.create(user=self.user, title='Test Song', mp3_file=mock_mp3_file, report_count=2)

        # Log in as admin and delete the song
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('manage_songs'), {'delete_song': True, 'song_id': song.song_id})
    
        # Check that the song has been deleted
        with self.assertRaises(Song.DoesNotExist):
            Song.objects.get(song_id=song.song_id)
        
        # Confirm the response redirected to the appropriate page after deletion
        self.assertEqual(response.status_code, 302)
        
        # Check success message for deletion
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Song deleted successfully." in str(msg) for msg in messages))

    def test_clear_comment_reports(self):
        comment = Comment.objects.create(user=self.user, profile=self.profile, message="Reported comment", report_count=4)

        # Log in as admin and clear comment reports
        self.client.login(username='admin', password='adminpass')
        response = self.client.post(reverse('reported_comments'), {'clear_reports': 'true', 'comment_id': comment.comment_id})

        # Refresh the comment and check that the report count is cleared
        comment.refresh_from_db()
        self.assertEqual(comment.report_count, 0)
        self.assertEqual(comment.reported_by.count(), 0)
        self.assertEqual(response.status_code, 200)
        
        # Check success message
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("Comment reports have been cleared" in str(msg) for msg in messages))

    def test_admin_dashboard_empty_search(self):
        self.client.login(username='admin', password='adminpass')
        response = self.client.get(reverse('admin_dashboard') + '?search=nonexistentuser')
        self.assertEqual(response.context['users'].count(), 0)  # No users should match
        self.assertEqual(response.status_code, 200)

    def test_profile_view_nonexistent_user(self):
        # Access profile view with a username that does not exist
        self.client.login(username='testuser', password='userpass')
        response = self.client.get(reverse('profile', args=['nonexistentuser']))
        self.assertEqual(response.status_code, 404)  # Page not found
    
    def test_report_other_profile(self):
        reported_user = User.objects.create_user(username='reporteduser', email='reported@example.com', password='password')
        profile=Profile.objects.create(user=reported_user)
        profile_url = reverse('profile', args=[reported_user.username])
        

        self.client.login(username='testuser', password='userpass')

        # Simulate reporting another user's profile
        response = self.client.post(profile_url, {'report_profile': True})
        
        # Refresh the profile and check the report count and reported_by field
        reported_profile = Profile.objects.get(user=reported_user)
        self.assertEqual(reported_profile.report_count, 1)
        self.assertIn(self.user, reported_profile.reported_by.all())
        
    def test_logout_view(self):
        url = reverse('logout')
        # Log the user in
        self.client.login(username='testuser', password='password')
        
        # Check user is logged in before calling logout
        self.assertTrue(self.user.is_authenticated)
        
        # Call logout view
        response = self.client.get(url)

        # Check that the user is logged out
        response = self.client.get(reverse('profile_settings'))
        self.assertNotIn('_auth_user_id', self.client.session)

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

class AdminDashboardTemplateTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(username="adminuser", password="adminpassword", email="admin@example.com")
        self.client.login(username="adminuser", password="adminpassword")
        self.user1 = User.objects.create_user(username="user1", email="user1@example.com")
        self.user2 = User.objects.create_user(username="user2", email="user2@example.com")
        
        self.user1.profile = Profile.objects.create(user=self.user1, report_count=3)
        self.user2.profile = Profile.objects.create(user=self.user2)

    def test_admin_dashboard_template_rendering(self):
        url = reverse("admin_dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Dashboard")
        self.assertContains(response, "Total Users")
        self.assertContains(response, "Total Songs")
        self.assertContains(response, "All Active Users")
        self.assertTemplateUsed(response, "users/admin_dashboard.html")
        self.assertTemplateUsed(response, "base.html")

    def test_user_table_content_display(self):
        url = reverse("admin_dashboard")
        response = self.client.get(url)

        self.assertContains(response, self.user1.username)
        self.assertContains(response, self.user1.email)
        self.assertContains(response, self.user1.profile.report_count)
        self.assertContains(response, self.user2.username)
        self.assertContains(response, self.user2.email)

    def test_no_users_message_display(self):
        User.objects.exclude(username="adminuser").delete()

        url = reverse("admin_dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No active users found.")
    
    def test_reported_comments_template_rendering(self):
        response = self.client.get(reverse("reported_comments"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/admin_dashboard.html")
        self.assertTemplateUsed(response, "users/reported_comments.html")
        self.assertContains(response, "Reported Comments")
        self.assertContains(response, "Comment")
        self.assertContains(response, "Profile")


class ProfileSettingsTemplateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.profile = Profile.objects.create(user=self.user)
        self.client.login(username="testuser", password="password")

    def test_profile_settings_template_rendering(self):
        response = self.client.get(reverse("profile_settings"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.username)
        self.assertContains(response, "My Profile Information")
        self.assertTemplateUsed(response, "users/profile_settings.html")



class ProfileTemplateTests(TestCase):
    @patch("mutagen.mp3.MP3")  
    def setUp(self, mock_mp3):
        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.profile = Profile.objects.create(user=self.user, bio="User biography")
        self.client.login(username="testuser", password="password")

        # Load the actual file from 'music/mp3/test.mp3' as mp3_file
        with open("music/mp3/test.mp3", "rb") as mp3_file:
            self.mock_mp3_file = SimpleUploadedFile("test.mp3", mp3_file.read(), content_type="audio/mpeg")
        
        # Create a song for the user with the mp3 file
        self.song = Song.objects.create(user=self.user, title="Test Song", mp3_file=self.mock_mp3_file)

    def test_profile_template_rendering(self):
        response = self.client.get(reverse("profile", kwargs={"username": self.user.username}))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/profile.html")
        self.assertContains(response, self.user.username)  
        self.assertContains(response, "User biography")    
        self.assertContains(response, "Top 5 Most Liked Singles")  
    

    def test_register_template_rendering(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "users/register.html")
        self.assertContains(response, "Full Name")
        self.assertContains(response, "Username")
        self.assertContains(response, "Email")
        self.assertContains(response, "Password")
        self.assertContains(response, "Confirm Password")
        self.assertContains(response, "terms and conditions")


User = get_user_model()

class SearchResultsTemplateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.user.is_verified = True
        self.user.save()
        self.client.login(username="testuser", password="password")

    def test_search_results_template_rendering_with_singles(self):
        response = self.client.get(reverse('search') + "?query=Sample")
        
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/search_results.html')
        self.assertTemplateUsed(response, 'base.html')