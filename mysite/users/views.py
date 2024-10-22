from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.db.models import Q
from allauth.account.models import EmailAddress
from allauth.account.utils import send_email_confirmation
from .models import User, Profile
from comments.models import Comment
from comments.forms import CommentForm
from django.db.models import Count
from .forms import RegisterForm, ProfileForm
from django.contrib.auth.decorators import user_passes_test, login_required
from music.models import Song, Album, Playlist
from django.core.exceptions import ValidationError
import users.urls
from django.http import JsonResponse

# Create your views here.
def home(request):
    if request.user.is_authenticated and request.user.is_admin:
        users = User.objects.filter(is_active=True, is_admin=False)  # Only fetch active users
        total_users = User.objects.filter(is_active=True, is_admin=False).count()  # Count total users not including admins and inactive
        total_songs = Song.objects.count()  # Count total songs

        return render(request, 'users/admin_dashboard.html', {
            'users': users,
            'total_users': total_users,
            'total_songs': total_songs
        })
    return render(request, 'base.html')

def is_admin(user):
    return user.is_superuser

def is_verified(user):
    return user.is_verified

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
        comments_to_delete = Comment.objects.filter(user=user)

        songs_to_delete.delete()
        albums_to_delete.delete()
        playlists_to_delete.delete()
        comments_to_delete.delete()
    
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
        
        if 'clear_reports' in request.POST:
            song_id = request.POST.get('song_id')

            if not song_id:
                messages.error(request, 'No song selected for clearing.')
                return redirect('reported_songs')
            
            song = get_object_or_404(Song, pk=song_id)

            song.report_count = 0
            song.reported_by.clear()
            song.save()
            messages.success(request, f"Song reports have been cleared for {song.title}.")

    return render(request, 'users/reported_songs.html', {'reported_songs': reported_songs})

@user_passes_test(is_admin)
def manage_reported_profiles(request):
    reported_profiles = Profile.objects.filter(report_count__gt=0, user__is_active=True).order_by('-report_count')
    if request.method == 'POST':
        if 'clear_reports' in request.POST:
            profile_id = request.POST.get('profile_id')

            if not profile_id:
                messages.error(request, 'No Profile selected for clearing.')
                return redirect('reported_profiles')
            
            profile = get_object_or_404(Profile, pk=profile_id)

            profile.report_count = 0
            profile.reported_by.clear()
            profile.save()
            messages.success(request, f"Profile reports have been cleared for {profile.user.username}.")
    
    return render(request, 'users/reported_profiles.html', {'reported_profiles': reported_profiles})

@user_passes_test(is_admin)
def manage_reported_comments(request):
    # Fetch comments that have been reported
    reported_comments = Comment.objects.filter(report_count__gt=0, user__is_active=True).order_by('-report_count')

    if request.method == 'POST':
        if 'clear_reports' in request.POST:
            comment_id = request.POST.get('comment_id')

            if not comment_id:
                messages.error(request, 'No comment selected for clearing.')
                return redirect('reported_comments')
            
            comment = get_object_or_404(Comment, pk=comment_id)

            comment.report_count = 0
            comment.reported_by.clear()
            comment.save()
            messages.success(request, f"Comment reports have been cleared for {comment.user.username}'s comment.")
    
    return render(request, 'users/reported_comments.html', {'reported_comments': reported_comments})


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

                # For AJAX requests, return a JSON response
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({
                        'status': 'success',
                        'message': 'Registration successful. A verification email has been sent to your email address. '
                    }, status=200)

        else:
            # Return validation errors for AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'errors': form.errors
                }, status=400)

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
                
                if email_address and not user.is_verified:
                    user.is_verified = True
                    user.save()
                
                login(request, user)

                if user.username == 'admin':
                    return redirect('admin_dashboard')
                
                return redirect('home')
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
    show_all = request.GET.get('show_all', 'false') == 'true'
    show_lyrics = request.GET.get('show_lyrics', 'false') == 'true'

    if show_all:
        top_singles = singles.annotate(likes_count=Count('liked_by')).order_by('-likes_count')[:5]
    else:
        top_singles = singles.annotate(likes_count=Count('liked_by')).order_by('-likes_count')[:5]

    is_own_profile = (user == request.user)
    is_admin = request.user.is_admin
    is_verified = request.user.is_verified

    filter_type = request.GET.get('filter', 'timestamp')

    if filter_type == 'likes':
        comments = Comment.objects.filter(profile=profile, parent_comment__isnull=True).annotate(total_likes=Count('liked_by')).order_by('-likes')
    else:
        comments = Comment.objects.filter(profile=profile, parent_comment__isnull=True).order_by('-created_at')  
    
    comment_form = CommentForm()
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
            if request.user in profile.reported_by.all():
                messages.warning(request, "You have already reported this profile.")
            else:
                profile.report_count += 1
                profile.reported_by.add(request.user)
                profile.save()
                messages.success(request, "Profile has been reported.")

    return render(request, 'users/profile.html', {
        'user_profile': profile,
        'top_singles': top_singles,
        'show_all': show_all,         
        'singles': singles,
        'albums': albums,
        'is_own_profile': is_own_profile,
        'is_admin': is_admin,
        'comments': comments,
        'comment_form': comment_form,
        'is_verified': is_verified,
        'show_lyrics': show_lyrics,
    })



@login_required
def profile_settings_view(request):
    profile = request.user.profile  # Get the profile of the logged-in user
    user = request.user  # Get the current logged-in user

    # if the user wants to change the profile, check if this is valid and save 
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            form.save()
            
            # Check if it's an AJAX request
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                # Return JSON response for AJAX
                return JsonResponse({'status': 'success', 'message': 'Profile updated successfully!'})
            else:
                messages.success(request, 'Your profile has been updated.')
                return redirect('profile_settings')  # Non-AJAX request, perform normal redirect
        
        else:
            # If form is not valid, return errors for AJAX requests
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'Invalid form data.', 'errors': form.errors}, status=400)

    else:
        form = ProfileForm(instance=profile)

    # send the user details and form details to be viewed in profile.html
    context = {
        'form': form,
        'user': user, 
    }

    return render(request, 'users/profile_settings.html', context)

def logout_view(request):
    print("Logout view triggered")
    logout(request)
    print(users.urls.urlpatterns[0])
    return redirect('home')  # Redirect to the home page after logging out

