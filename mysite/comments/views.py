from django.shortcuts import render, redirect, get_object_or_404
from users.models import User, Profile
from .models import Comment
from .forms import CommentForm  # Assuming you've created a form for comments
from django.contrib.auth.decorators import login_required
from django.contrib import messages

@login_required
def add_comment(request, username):
    profile = get_object_or_404(Profile, user__username=username)

    # Prevent a user from commenting on their own profile but allow replies
    if request.user == profile.user and 'parent_comment_id' not in request.POST:
        return redirect('profile', username=username)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.profile = profile
            comment.user = request.user

            # Check if it's a reply to another comment
            parent_comment_id = request.POST.get('parent_comment_id')
            if parent_comment_id:
                parent_comment = get_object_or_404(Comment, pk=parent_comment_id)
                comment.parent_comment = parent_comment

            comment.save()
            return redirect('profile', username=username)

    return redirect('profile', username=username)

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    profile = comment.profile

    if request.user == comment.user or request.user == profile.user or request.user.is_admin:
        comment.delete()
    else:
        pass

    return redirect('profile', username=profile.user.username)

@login_required
def like_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    user = request.user

    if user in comment.liked_by.all():
        comment.liked_by.remove(user)
        comment.likes -= 1
    else:
        if user in comment.disliked_by.all():
            comment.disliked_by.remove(user)
            comment.dislikes -= 1
        comment.liked_by.add(user)
        comment.likes += 1

    comment.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def dislike_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    user = request.user
    
    if user in comment.disliked_by.all():
        comment.disliked_by.remove(user)
        comment.dislikes -= 1
    else:
        if user in comment.liked_by.all():
            comment.liked_by.remove(user)
            comment.likes -= 1
        comment.disliked_by.add(user)
        comment.dislikes += 1

    comment.save()
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def report_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    
    # Increment the report count
    comment.report_count += 1
    comment.save()

    commenter = comment.user.username

    messages.success(request, f"{commenter}'s comment has been reported.")
    return redirect('profile', username=comment.profile.user.username)