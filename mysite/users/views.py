from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from .models import User, Profile

from .forms import RegisterForm, ProfileForm
from django.contrib.auth.decorators import user_passes_test, login_required

from music.models import Song, Album, Playlist

# Create your views here.
def home(request):
    return render(request, 'base.html')

def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    users = User.objects.filter(is_active=True, is_admin=False)  # Only fetch active users
    total_users = User.objects.filter(is_active=True, is_admin=False).count()  # Count total users not including admins and inactive
    total_songs = Song.objects.count()  # Count total songs

    return render(request, 'users/admin_dashboard.html', {
        'users': users,
        'total_users': total_users,
        'total_songs': total_songs
    })

@user_passes_test(is_admin)
def delete_user(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)

        # delete all songs, albums and playlists associated with the user
        songs_to_delete = Song.objects.filter(user=user)
        albums_to_delete = Album.objects.filter(user=user)
        playlists_to_delete = Playlist.objects.filter(user=user)

        songs_to_delete.delete()
        albums_to_delete.delete()
        playlists_to_delete.delete()
    
        user.is_active = False
        user.username = f"deactivated_user_{user_id}" # Anonymize the username
        user.set_unusable_password()
        email_address = EmailAddress.objects.filter(user=user).first()
        if email_address:
            email_address.verified = False
            email_address.save()

        user.email = f"deactivated_user_{user_id}_{user.email}"
        user.save()
        return redirect('admin_dashboard')
    else:
        messages.error(request, "Invalid request.")
        return redirect('admin_dashboard')

@user_passes_test(is_admin)
def manage_reported_songs(request):
    reported_songs = Song.objects.filter(report_count__gt=0).order_by('-report_count')  # Fetch songs with reports
    
    if request.method == 'POST':
        # Handle song deletion
        if 'delete_song' in request.POST:
            song_id = request.POST.get('song_id')
            
            if not song_id:
                messages.error(request, 'No song selected for deletion.')
                return redirect('reported_songs')
            
            song = get_object_or_404(Song, pk=song_id)
            song.delete()
            messages.success(request, 'Song deleted successfully.')
            return redirect('reported_songs')
    return render(request, 'users/reported_songs.html', {'reported_songs': reported_songs})

@user_passes_test(is_admin)
def manage_reported_profiles(request):
    reported_profiles = Profile.objects.filter(report_count__gt=0, user__is_active=True).order_by('-report_count')
    return render(request, 'users/reported_profiles.html', {'reported_profiles': reported_profiles})


# Registration
def register(request):
    form = RegisterForm()

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():  # Check if the form is valid
            user = form.save()  # Save the user to the database

            if user is not None:  # Check if authentication was successful

                Profile.objects.create(user=user)

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

    if request.user.is_authenticated:
        # If the user is already logged in, redirect to the home page
        return redirect('home')

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



# function which allows users to search
def search_view(request):
    query = request.GET.get('query', '')  # Get the query string from the GET parameters
    if query:
        request.session['last_search_query'] = query  # Save the query in the session
    users = User.objects.filter(Q(username__icontains=query) 
                                & Q(is_active=True)  & Q(is_admin=False))  # Search for active users by username
    
    singles = Song.objects.filter(Q(title__icontains=query))
    
    albums = Album.objects.filter(Q(title__icontains=query))

    user_playlists = Playlist.objects.filter(user=request.user)


    return render(request, 'users/search_results.html', {'users': users, 
                                                         'query': query,
                                                         'singles': singles,
                                                         'albums': albums,
                                                         'playlists': user_playlists})


@login_required
def profile_view(request, username):
    # Get the user and profile by username
    user = get_object_or_404(User, username=username)
    profile = Profile.objects.get(user=user)
    singles = Song.objects.filter(user=user)
    albums = Album.objects.filter(user=user)

    # Check if the logged-in user is viewing their own profile
    is_own_profile = (user == request.user)

    is_admin = request.user.is_admin

    if request.method == 'POST':
        # Handle song deletion
        if 'delete_song' in request.POST:
            song_id = request.POST.get('song_id')
            song = get_object_or_404(Song, song_id=song_id, user=request.user)
            song.delete()
            messages.success(request, 'Song deleted successfully.')
            return redirect('profile', username=username)

        # Handle profile report
        if 'report_profile' in request.POST and not is_own_profile:
            profile.report_count += 1
            profile.save()
            messages.success(request, 'Profile has been reported.')

        # if 'delete_profile' in request.POST and user.is_admin:

    return render(request, 'users/profile.html', {
        'user_profile': profile,
        'singles': singles,
        'albums': albums,
        'is_own_profile': is_own_profile,
        'is_admin': is_admin
    })



@login_required
def profile_settings_view(request):
    profile = request.user.profile  # Get the profile of the logged-in user
    user = request.user  # Get the current logged-in user

    # if the user wants to change the profile, check if this is valid and save 
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('profile_settings')  # Redirect back to the profile page
    else:
        form = ProfileForm(instance=profile)

    # send the user details and form details to be viewed in profile.html
    context = {
        'form': form,
        'user': user, 
    }

    return render(request, 'users/profile_settings.html', context)

def logout_view(request):
    logout(request)
    return redirect('home')  # Redirect to the home page after logging out


