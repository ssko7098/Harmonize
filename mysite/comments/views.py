from django.shortcuts import render
from .models import Comment

# Create your views here.
def comment_list(request):
    comments = Comment.objects.all()
    return render(request, 'comments/comment_list.html', {'comments': comments})
