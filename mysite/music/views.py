from django.shortcuts import render, redirect
from .models import Album, Song, Playlist, User, PlaylistSong
from .forms import SongForm, PlaylistForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.contrib import messages
from users.views import is_verified
from .models import Playlist, PlaylistSong, Song
from django.shortcuts import get_object_or_404
from .external_api import upload_mp3_to_assemblyai, get_transcription 


def album_list(request):
    albums = Album.objects.all()
    return render(request, 'music/album_list.html', {'albums': albums})

@login_required
@user_passes_test(is_verified)
def view_playlists(request, username):
    user = get_object_or_404(User, username=username)
    playlists = Playlist.objects.filter(user=user)

    # Handle search functionality
    search_query = request.GET.get('search_query', '')
    if search_query:
        playlists = playlists.filter(name__icontains=search_query)

    # Handle creating a new playlist
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            return redirect('view_playlists', username=request.user.username)
    else:
        form = PlaylistForm()

    return render(request, 'music/view_playlists.html', {
        'playlists': playlists,
        'user': user,
        'form': form,
        'search_query': search_query
    })

@login_required
@user_passes_test(is_verified)
def create_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            return redirect('view_playlists', username=request.user.username)
    else:
        form = PlaylistForm()

    return render(request, 'music/create_playlist.html', {'form': form})

@login_required
@user_passes_test(is_verified)
def delete_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)

    if request.method == 'POST':
        playlist.delete()
        return redirect('view_playlists', username=request.user.username)

    return redirect('view_playlists', username=request.user.username)
  

@login_required
@user_passes_test(is_verified)
def upload_song(request):
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.user = request.user
            song.save()
            mp3_file_path = song.mp3_file.path
            upload_url = upload_mp3_to_assemblyai(mp3_file_path)
            lyrics = get_transcription(upload_url)

            # Store the lyrics in the song model
            if lyrics:
                song.lyrics = lyrics
                song.save()

            return redirect('song_details', song_id=song.song_id)
    else:
        form = SongForm()

    return render(request, 'music/upload_song.html', {'form': form})

@login_required
def song_details(request, song_id):
    song = Song.objects.get(song_id=song_id)
    return render(request, 'music/song_details.html', {'song': song}) 

@login_required
@user_passes_test(is_verified)
def view_playlist_songs(request, username, playlist_id):
    user = get_object_or_404(User, username=username)

    playlist = get_object_or_404(Playlist, pk=playlist_id, user=user)

    if playlist.user != request.user:
        raise Http404("You do not have permission to view this playlist.")
    
    return render(request, 'music/in_playlist.html', {'playlist': playlist})

@login_required
@user_passes_test(is_verified)
def add_to_playlist(request):
    if request.method == 'POST':
        playlist_id = request.POST.get('playlist')
        song_id = request.POST.get('song_id')

        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        song = get_object_or_404(Song, pk=song_id)

        if not PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
            PlaylistSong.objects.create(playlist=playlist, song=song)

    # Redirect back to search with the original query
    query = request.session.get('last_search_query', '')
    if query:
        return redirect(f'/search/?query={query}')
    return redirect('home')


@login_required
@user_passes_test(is_verified)
def delete_song_from_playlist(request, playlist_id, song_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
    song = get_object_or_404(Song, pk=song_id)

    if request.method == 'POST':
        playlist_song = get_object_or_404(PlaylistSong, playlist=playlist, song=song)
        playlist_song.delete()
    
    return redirect('view_playlist_songs', username=request.user.username, playlist_id=playlist.pk)

@login_required
@user_passes_test(is_verified)
def view_playlist_songs(request, username, playlist_id):
    user = get_object_or_404(User, username=username)
    playlist = get_object_or_404(Playlist, pk=playlist_id, user=user)

    # Ensure the logged-in user is the owner of the playlist
    if playlist.user != request.user:
        raise Http404("You do not have permission to view this playlist.")

    search_query = request.GET.get('search', '')

    sort_by = request.GET.get('sort_by', 'title')  # Default sorting by title
    order = request.GET.get('order', 'v')  # Default order is ascending

    # Apply search filter
    if search_query:
        filtered_songs = PlaylistSong.objects.filter(playlist=playlist, song__title__icontains=search_query)
    else:
        filtered_songs = playlist.playlistsong_set.all()

    # Apply sorting based on query parameters
    if sort_by == 'title':
        filtered_songs = filtered_songs.order_by('song__title' if order == 'v' else '-song__title')
    elif sort_by == 'user':
        filtered_songs = filtered_songs.order_by('song__user__username' if order == 'v' else '-song__user__username')

    # Flip the order for the next toggle
    next_order = '^' if order == 'v' else 'v'

    return render(request, 'music/in_playlist.html', {
        'playlist': playlist,
        'filtered_songs': filtered_songs,
        'search_query': search_query,
        'sort_by': sort_by,
        'order': order,
        'next_order': next_order,
    })

@login_required
@user_passes_test(is_verified)
def report_song(request, song_id):
    song = get_object_or_404(Song, song_id=song_id)
    
    if request.user in song.reported_by.all():
        messages.warning(request, f"You have already reported the song '{song.title}'.")
    else:
        song.report_count += 1
        song.reported_by.add(request.user)  # Add the user to the list of reporters
        song.save()
        messages.success(request, f"The song '{song.title}' has been reported.")

    # If the report came from the profile page, redirect to this page not the search page.
    if request.POST.get('from_profile'):
        return redirect('profile', username=song.user.username)
    
    # Redirect back to search with the original query
    query = request.session.get('last_search_query', '')
    if query:
        return redirect(f'/search/?query={query}')
    return redirect('home')

@login_required
@user_passes_test(is_verified)
def liked_songs(request, username):
    user = get_object_or_404(User, username=username)
    liked_songs = Song.objects.filter(liked_by=user)
    search_query = request.GET.get('search', '')
    if search_query:
        filtered_liked_songs = liked_songs.filter(title__icontains=search_query)
    else:
        filtered_liked_songs = liked_songs

    return render(request, 'music/liked_songs.html', {
        'user': user,
        'filtered_liked_songs': filtered_liked_songs,
    })

@login_required
@user_passes_test(is_verified)
def add_to_liked_songs(request, song_id):
    song = get_object_or_404(Song, pk=song_id)

    if request.user not in song.liked_by.all():
        song.liked_by.add(request.user)
    query = request.session.get('last_search_query', '')
    if query:
        return redirect(f'/search/?query={query}')  # Redirect back to the search page with the same query
    return redirect('home')

@login_required
@user_passes_test(is_verified)
def remove_liked_song(request, song_id):
    song = get_object_or_404(Song, pk=song_id)
    
    if request.user in song.liked_by.all():
        song.liked_by.remove(request.user)

    return redirect('liked_songs', username=request.user.username)
