from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from .models import User

from .forms import RegisterForm
from django.contrib.auth.decorators import user_passes_test

# Create your views here.
def home(request):
    return render(request, 'users/home.html')

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.filter(is_active=True, is_admin=False)  # Only fetch active users
    return render(request, 'users/admin_dashboard.html', {'users': users})


@user_passes_test(is_admin)
def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
    
        user.is_active = False
        user.username = f"deactivated_user_{user_id}" # Anonymize the username
        user.set_unusable_password()
        user.email = f"deactivated_user_{user.email}"
        user.save()
        return redirect('admin_dashboard')
    else:
        messages.error(request, "Invalid request.")
        return redirect('admin_dashboard')

# Registration
def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():  # Check if the form is valid
            user = form.save()  # Save the user to the database

            if user is not None:  # Check if authentication was successful
                email_address = EmailAddress.objects.create(
                user=user, 
                email=user.email, 
                verified=False, 
                primary=True)

                send_email_confirmation(request, user, signup=True)

                messages.success(request, 'We have sent a verification email to your email address. Please check your inbox and click the confirmation link.')

    return render(request, 'users/register.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from allauth.account.models import EmailAddress  # Required to check email verification status

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Check if the email address is verified
                email_address = EmailAddress.objects.filter(user=user, verified=True).first()
                
                if email_address:  # If a verified email address exists
                    login(request, user)

                    if user.username == 'admin':
                        return redirect('admin_dashboard')
                    
                    return redirect('home')
                else:
                    messages.error(request, "Your email address has not been verified. Please verify your email before logging in.")
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login details.")
    
    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})



def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the home page after logging out
