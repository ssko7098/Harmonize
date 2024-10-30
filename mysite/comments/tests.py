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

    # tests if a comment can be added by a user to anothers profile
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

    #tests if a user is prevented from commenting on their own profile
    def test_add_comment_to_own_profile(self):
        self.client.logout()
        self.client.login(username='user2', password='password')  # User2 logs in
        response = self.client.post(reverse('add_comment', args=[self.user2.username]), {
            'message': 'This should not be added.'
        })
        self.assertEqual(response.status_code, 302)  # Check redirect
        self.assertEqual(Comment.objects.count(), 0)  # No new comments should be added
    
    #tests if a user can delete their own comment
    def test_delete_comment(self):
        comment = Comment.objects.create(message='A comment', user=self.user1, profile=self.user2.profile)
        response = self.client.post(reverse('delete_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        self.assertEqual(Comment.objects.count(), 0)  # Comment should be deleted

    #tests if a user can delete another persons comment
    def test_delete_comment_not_owner(self):
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        response = self.client.post(reverse('delete_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        self.assertEqual(Comment.objects.count(), 1)  # Comment should still exist

    #tests if a user can like a comment
    def test_like_comment(self):
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        response = self.client.post(reverse('like_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertIn(self.user1, comment.liked_by.all())  # User1 should like the comment
        self.assertEqual(comment.likes, 1)  # Likes should be 1

    #tests if a user likes a comment twice, the comment is unliked
    def test_double_like_comment(self):
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        self.client.post(reverse('like_comment', args=[comment.comment_id]))
        response = self.client.post(reverse('like_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertNotIn(self.user1, comment.liked_by.all())  # User1 shouldnt like the comment
        self.assertEqual(comment.likes, 0)  # Likes should be 0, since like was pressed again

    #tests if users can dislike a comment
    def test_dislike_comment(self):
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        response = self.client.post(reverse('dislike_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertIn(self.user1, comment.disliked_by.all())  # User1 should dislike the comment
        self.assertEqual(comment.dislikes, 1)  # Dislikes should be 1

    #tests if a user dislikes a comment twice,the comment is un-disliked
    def test_double_dislike_comment(self):
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        self.client.post(reverse('dislike_comment', args=[comment.comment_id]))
        response = self.client.post(reverse('dislike_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertNotIn(self.user1, comment.disliked_by.all())  # User1 shouldnt dislike the comment
        self.assertEqual(comment.dislikes, 0)  # Likes should be 1

    #tests if a user switches from like to dislike, the other actions is reversed
    def test_switch_like_comment(self):
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        self.client.post(reverse('like_comment', args=[comment.comment_id]))  # Like first
        response = self.client.post(reverse('dislike_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertNotIn(self.user1, comment.liked_by.all())  # User1 shouldnt like the comment
        self.assertEqual(comment.likes, 0)  # likes should be 0
        self.assertIn(self.user1, comment.disliked_by.all())  # User1 should dislike the comment
        self.assertEqual(comment.dislikes, 1)  # Dislikes should be 1

    #tests that users can report another users comment
    def test_report_comment(self):
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        response = self.client.post(reverse('report_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertEqual(comment.report_count, 1)  # Report count should be 1

    #tests that users can not report a comment more than once
    def test_report_comment_already_reported(self):
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        self.client.post(reverse('report_comment', args=[comment.comment_id]))  # First report
        response = self.client.post(reverse('report_comment', args=[comment.comment_id]))  # Second report
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertEqual(comment.report_count, 1)  # Report count should still be 1


class ReplyCommentTest(TestCase):
    def setUp(self):
        # Create a user and log them in
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password')
        
        # Create a profile and a comment
        self.profile = Profile.objects.create(user=self.user, bio='Bio of User')
        self.comment = Comment.objects.create(user=self.user, profile=self.profile, message='Original Comment')
        self.client.login(username='testuser', password='password')
    
    #tests a user can reply to a comment
    def test_add_reply_to_comment(self):
        # Add a reply to the original comment
        response = self.client.post(reverse('add_comment', args=[self.user.username]), {
            'message': 'Reply to Comment',
            'parent_comment_id': self.comment.comment_id  # Send the original comment's ID as parent
        })
        self.assertEqual(response.status_code, 302)  # Ensure redirection after success
        
        
        self.assertEqual(Comment.objects.count(), 2) # Should be 2 comments in total, parent and reply

        # Ensure the reply exists and is linked to the original comment
        self.assertTrue(Comment.objects.filter(message='Reply to Comment').exists())
        reply = Comment.objects.get(message='Reply to Comment')
        self.assertEqual(reply.parent_comment, self.comment)  # Ensure reply is linked to the parent

    #tests that a reply appears correctly on profile page
    def test_view_comment_with_replies(self):
        # Add a reply to the original comment
        reply = Comment.objects.create(user=self.user, profile=self.profile, message='Reply to Comment', parent_comment=self.comment)
        
        # View the profile to check if the comment and reply are displayed
        response = self.client.get(reverse('profile', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        
        # Check that the original comment and reply are displayed
        self.assertContains(response, 'Original Comment')
        self.assertContains(response, 'Reply to Comment')
        
        # Ensure the reply is correctly nested under the original comment
        comment_with_reply = Comment.objects.get(comment_id=self.comment.comment_id)
        self.assertIn(reply, comment_with_reply.replies.all())  # Check if the reply exists in the original comment's replies

    #tests that a reply can be deleted
    def test_delete_reply_to_comment(self):
        # Create a reply to the original comment
        reply = Comment.objects.create(user=self.user, profile=self.profile, message='Reply to Comment', parent_comment=self.comment)
        
        # Delete the reply
        response = self.client.post(reverse('delete_comment', args=[reply.comment_id]))
        self.assertEqual(response.status_code, 302)  # Ensure redirection after success
        
        # Ensure the reply no longer exists
        self.assertFalse(Comment.objects.filter(comment_id=reply.comment_id).exists())

    #tests that a if a comment is deleted, the replies to the comment are also deleted
    def test_delete_comment_with_replies(self):
        # Add a reply to the original comment
        reply = Comment.objects.create(user=self.user, profile=self.profile, message='Reply to Comment', parent_comment=self.comment)
        
        # Delete the original comment (which has replies)
        response = self.client.post(reverse('delete_comment', args=[self.comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Ensure redirection after success
        
        # Ensure the original comment and its replies no longer exist
        self.assertFalse(Comment.objects.filter(comment_id=self.comment.comment_id).exists())
        self.assertFalse(Comment.objects.filter(comment_id=reply.comment_id).exists())

    

class CommentModelTest(TestCase):
    def setUp(self):
        # Set up two users and profiles for testing
        self.user1 = User.objects.create_user(username='user1', password='password', email='user1@example.com')
        self.user2 = User.objects.create_user(username='user2', password='password', email='user2@example.com')
        self.profile1 = Profile.objects.create(user=self.user1, bio='User1 bio')
        self.profile2 = Profile.objects.create(user=self.user2, bio='User2 bio')

    def test_comment_default(self):
        """Test that a comment can be created with proper defaults."""
        comment = Comment.objects.create(profile=self.profile1, user=self.user1, message='Test comment')
        
        self.assertEqual(comment.message, 'Test comment')
        self.assertEqual(comment.profile, self.profile1)
        self.assertEqual(comment.user, self.user1)
        self.assertEqual(comment.likes, 0)  # Default likes should be 0
        self.assertEqual(comment.dislikes, 0)  # Default dislikes should be 0
        self.assertEqual(comment.report_count, 0)  # Default report count should be 0
        self.assertIsNone(comment.parent_comment)  # No parent comment (not a reply)

    def test_comment_with_reply(self):
        """Test that a reply can be correctly linked to a parent comment."""
        parent_comment = Comment.objects.create(profile=self.profile1, user=self.user1, message='Parent comment')
        reply_comment = Comment.objects.create(profile=self.profile1, user=self.user2, message='Reply to comment', parent_comment=parent_comment)
        
        self.assertEqual(reply_comment.parent_comment, parent_comment)
        self.assertIn(reply_comment, parent_comment.replies.all())  # The reply should be in the parent comment's replies

    def test_comment_like_dislike_relationship(self):
        """Test the liking and disliking functionality using ManyToMany relationships."""
        comment = Comment.objects.create(profile=self.profile1, user=self.user1, message='Liking test')
        
        comment.liked_by.add(self.user2)
        comment.disliked_by.add(self.user1)
        comment.likes+=1
        comment.dislikes+=1
        
        # Test liking
        self.assertIn(self.user2, comment.liked_by.all())
        self.assertEqual(comment.liked_by.count(), 1)
        self.assertEqual(comment.likes, 1)
        
        # Test disliking
        self.assertIn(self.user1, comment.disliked_by.all())
        self.assertEqual(comment.disliked_by.count(), 1)
        self.assertEqual(comment.dislikes, 1)

    def test_comment_report_count(self):
        """Test the report_count and reported_by functionality."""
        comment = Comment.objects.create(profile=self.profile2, user=self.user1, message='Report test')
        
        comment.reported_by.add(self.user1)  # User1 reports the comment
        comment.report_count += 1
        comment.save()

        self.assertEqual(comment.report_count, 1)
        self.assertIn(self.user1, comment.reported_by.all())
        
        # Ensure the same user cannot report again (or count doesn't increase)
        comment.reported_by.add(self.user1)  # User1 tries to report again
        self.assertEqual(comment.report_count, 1)  # Report count should not increase

    def test_comment_deletion(self):
        """Test that when a comment is deleted, replies and relationships are also cleaned up."""
        parent_comment = Comment.objects.create(profile=self.profile1, user=self.user1, message='Parent comment')
        reply_comment = Comment.objects.create(profile=self.profile1, user=self.user2, message='Reply to comment', parent_comment=parent_comment)
        
        parent_comment.delete()  # Deleting the parent comment
        
        # Ensure that the reply is also deleted
        self.assertFalse(Comment.objects.filter(pk=reply_comment.pk).exists())
        
    def test_comment_string_representation_method(self):
        """Test the string representation of the comment."""
        comment = Comment.objects.create(profile=self.profile1, user=self.user1, message='String rep test')
        self.assertEqual(str(comment), f'Comment by {comment.user.username}')
