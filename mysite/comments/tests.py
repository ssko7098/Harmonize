from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Comment
from users.models import User, Profile

User = get_user_model()

class CommentViewsTestCase(TestCase):
    def setUp(self):
        # Create users
        self.user1 = User.objects.create_user(username='user1', password='password', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', password='password', email='user2@example.com')
        
        # Create profiles
        self.profile = Profile.objects.create(user=self.user2, bio='Bio of User Two')

        # Log in user1
        self.client.login(username='user1', password='password')

    def test_add_comment(self):
        response = self.client.post(reverse('add_comment', args=[self.user2.username]), {
            'message': 'This is a comment!'
        })
        self.assertEqual(response.status_code, 302)  # Check redirect
        self.assertEqual(Comment.objects.count(), 1)  # One comment should exist
        comment = Comment.objects.first()
        self.assertEqual(comment.message, 'This is a comment!')
        self.assertEqual(comment.user, self.user1)
        self.assertEqual(comment.profile, self.profile)

    def test_add_comment_to_own_profile(self):
        self.client.logout()
        self.client.login(username='user2', password='password')  # User2 logs in
        response = self.client.post(reverse('add_comment', args=[self.user2.username]), {
            'message': 'This should not be added.'
        })
        self.assertEqual(response.status_code, 302)  # Check redirect
        self.assertEqual(Comment.objects.count(), 0)  # No new comments should be added

