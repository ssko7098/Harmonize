from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation

# Create your views here.
def home(request):
    return render(request, 'users/home.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.save()

            email_address = EmailAddress.objects.create(
                user=user, 
                email=user.email, 
                verified=False, 
                primary=True
            )
            send_email_confirmation(request, user, signup=True)

            messages.success(request, 'We have sent a verification email to your email address. Please check your inbox and click the confirmation link.')

            # Instead of redirecting, stay on the register page
            return render(request, 'users/register.html', {'form': form})
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Logged in as {user.username}")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid login details.")
    
    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the home page after logging out
