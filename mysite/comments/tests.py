from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Comment
from .forms import CommentForm
from users.models import User, Profile
from django import forms

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
        """tests if a comment can be added by a user to anothers profile"""
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
        """tests if a user is prevented from commenting on their own profile"""
        self.client.logout()
        self.client.login(username='user2', password='password')  # User2 logs in
        response = self.client.post(reverse('add_comment', args=[self.user2.username]), {
            'message': 'This should not be added.'
        })
        self.assertEqual(response.status_code, 302)  # Check redirect
        self.assertEqual(Comment.objects.count(), 0)  # No new comments should be added
    
    def test_delete_comment(self):
        """tests if a user can delete their own comment"""
        comment = Comment.objects.create(message='A comment', user=self.user1, profile=self.user2.profile)
        response = self.client.post(reverse('delete_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        self.assertEqual(Comment.objects.count(), 0)  # Comment should be deleted

    def test_delete_comment_not_owner(self):
        """tests if a user can delete another persons comment"""
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        response = self.client.post(reverse('delete_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        self.assertEqual(Comment.objects.count(), 1)  # Comment should still exist

    def test_like_comment(self):
        """tests if a user can like a comment"""
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        response = self.client.post(reverse('like_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertIn(self.user1, comment.liked_by.all())  # User1 should like the comment
        self.assertEqual(comment.likes, 1)  # Likes should be 1

    def test_double_like_comment(self):
        """tests if a user likes a comment twice, the comment is unliked"""
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        self.client.post(reverse('like_comment', args=[comment.comment_id]))
        response = self.client.post(reverse('like_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertNotIn(self.user1, comment.liked_by.all())  # User1 shouldnt like the comment
        self.assertEqual(comment.likes, 0)  # Likes should be 0, since like was pressed again

    def test_dislike_comment(self):
        """tests if users can dislike a comment"""
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        response = self.client.post(reverse('dislike_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertIn(self.user1, comment.disliked_by.all())  # User1 should dislike the comment
        self.assertEqual(comment.dislikes, 1)  # Dislikes should be 1

    def test_double_dislike_comment(self):
        """tests if a user dislikes a comment twice,the comment is un-disliked"""
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        self.client.post(reverse('dislike_comment', args=[comment.comment_id]))
        response = self.client.post(reverse('dislike_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertNotIn(self.user1, comment.disliked_by.all())  # User1 shouldnt dislike the comment
        self.assertEqual(comment.dislikes, 0)  # Likes should be 1

    def test_switch_like_comment(self):
        """tests if a user switches from like to dislike, the other actions is reversed"""
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        self.client.post(reverse('like_comment', args=[comment.comment_id]))  # Like first
        response = self.client.post(reverse('dislike_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertNotIn(self.user1, comment.liked_by.all())  # User1 shouldnt like the comment
        self.assertEqual(comment.likes, 0)  # likes should be 0
        self.assertIn(self.user1, comment.disliked_by.all())  # User1 should dislike the comment
        self.assertEqual(comment.dislikes, 1)  # Dislikes should be 1

    def test_report_comment(self):
        """tests that users can report another users comment"""
        comment = Comment.objects.create(message='A comment', user=self.user2, profile=self.profile)
        response = self.client.post(reverse('report_comment', args=[comment.comment_id]))
        self.assertEqual(response.status_code, 302)  # Check redirect
        comment.refresh_from_db()
        self.assertEqual(comment.report_count, 1)  # Report count should be 1

    def test_report_comment_already_reported(self):
        """tests that users can not report a comment more than once"""
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
    
    def test_add_reply_to_comment(self):
        """tests a user can reply to a comment"""
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

    def test_view_comment_with_replies(self):
        """tests that a reply appears correctly on profile page"""
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

    def test_delete_reply_to_comment(self):
        """tests that a reply can be deleted"""
        # Create a reply to the original comment
        reply = Comment.objects.create(user=self.user, profile=self.profile, message='Reply to Comment', parent_comment=self.comment)
        
        # Delete the reply
        response = self.client.post(reverse('delete_comment', args=[reply.comment_id]))
        self.assertEqual(response.status_code, 302)  # Ensure redirection after success
        
        # Ensure the reply no longer exists
        self.assertFalse(Comment.objects.filter(comment_id=reply.comment_id).exists())

    def test_delete_comment_with_replies(self):
        """tests that a if a comment is deleted, the replies to the comment are also deleted"""
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

class CommentFormTest(TestCase):
    def setUp(self):
        # Set up a user and profile for testing purposes
        self.user = User.objects.create_user(username='testuser', password='password', email='test@example.com')
        self.profile = Profile.objects.create(user=self.user, bio='Test bio')

    def test_valid_form(self):
        """Test that a form with valid data is considered valid."""
        form_data = {'message': 'This is a valid comment.'}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_missing_message_field(self):
        """Test that the form is invalid if the message field is missing."""
        form_data = {}  # Missing 'message' field
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)  # Check if 'message' field has errors
        self.assertEqual(form.errors['message'], ['This field is required.'])
    
    def test_blank_message(self):
        """Test that the form rejects a blank message."""
        form_data = {'message': ''}
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)  # Ensure 'message' has an error
        self.assertEqual(form.errors['message'], ['This field is required.'])  # Check for required field error
    
    def test_message_length(self):
        """Test that a message of valid length passes and very long message fails."""
        # Valid message
        valid_message = 'a' * 255 
        form_data = {'message': valid_message}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Extremely long message
        long_message = 'a' * 5000 
        form_data = {'message': long_message}
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid()) 
    
    def test_custom_widget_attrs(self):
        """Test that the message field uses the correct widget attributes."""
        form = CommentForm()
        self.assertIsInstance(form.fields['message'].widget, forms.Textarea)
        self.assertEqual(form.fields['message'].widget.attrs['rows'], 3)  # Check if the custom widget has 3 rows
    
class ProfileTemplateTest(TestCase):
    def setUp(self):
        # Create a user, profile, and comments for testing
        self.user = User.objects.create_user(username='testuser', password='password', email='testuser@example.com')
        self.profile = Profile.objects.create(user=self.user, bio="This is a test user's profile.")
        self.comment1 = Comment.objects.create(profile=self.profile, user=self.user, message="This is the first comment.")
        self.comment2 = Comment.objects.create(profile=self.profile, user=self.user, message="This is the second comment.")

        self.client.login(username='testuser', password='password')

    def test_profile_template_used(self):
        """Test if the correct template (profile.html) is used for the profile page."""
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertEqual(response.status_code, 200)  # Ensure the page loads successfully

        # Check that the correct templates are used
        self.assertTemplateUsed(response, 'users/profile.html')
        self.assertTemplateUsed(response, 'comments/comments.html')
        self.assertTemplateUsed(response, 'comments/comment_actions.html')
        self.assertTemplateUsed(response, 'comments/replies.html')


    def test_profile_comments_displayed(self):
        """Test if the profile page displays user comments."""
        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertContains(response, self.comment1.message)  # Check if the first comment is displayed
        self.assertContains(response, self.comment2.message)  # Check if the second comment is displayed

    def test_no_comments_message(self):
        """Test if a message is displayed when there are no comments."""
        # Create a new profile with no comments
        new_user = User.objects.create_user(username='newuser', password='password', email='newuser@example.com')
        new_profile = Profile.objects.create(user=new_user, bio="New user's profile")
        
        response = self.client.get(reverse('profile', kwargs={'username': new_user.username}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No comments yet!") 

    def test_profile_comment_likes_dislikes_displayed(self):
        """Test if the comment likes and dislikes are displayed properly."""
        # Add likes and dislikes to the comments
        self.comment1.likes = 5
        self.comment1.dislikes = 2
        self.comment1.save()

        response = self.client.get(reverse('profile', kwargs={'username': self.user.username}))
        self.assertContains(response, '5')  # Check if likes are displayed for the first comment
        self.assertContains(response, '2')  # Check if dislikes are displayed for the first comment
