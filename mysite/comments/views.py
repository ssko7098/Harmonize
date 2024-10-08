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

