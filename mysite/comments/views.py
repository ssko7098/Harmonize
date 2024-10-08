from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Comment
from users.models import Profile, User
from .forms import CommentForm

@login_required
def add_comment(request, username):
    user_profile = get_object_or_404(Profile, user__username=username)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.profile = user_profile
            comment.save()
            messages.success(request, 'Your comment has been posted.')
        else:
            messages.error(request, 'There was an error in your comment.')
    
    return redirect('profile', username=username)

# Create your views here.
def comment_list(request):
    comments = Comment.objects.all()
    return render(request, 'comments/comment_list.html', {'comments': comments})
