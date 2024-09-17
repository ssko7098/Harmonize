from django.shortcuts import render, HttpResponse, get_object_or_404
from django.template import loader
from .models import User, Profile

# Create your views here.
def user_list(request):
    users = User.objects.all()  # Fetch all users from the database
    template = loader.get_template("app/user_list.html")
    context = {
        "users": users,
    }

    return HttpResponse(template.render(context, request))


def register(request):
    # Logic for user registration
    pass


def profile(request, pk):
    user_profile = get_object_or_404(Profile, pk=pk)
    return render(request, 'users/profile.html', {'profile': user_profile})