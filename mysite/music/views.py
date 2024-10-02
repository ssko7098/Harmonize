from django.shortcuts import render, redirect
from .models import Album, Song, Playlist, User
from .forms import SongForm, PlaylistForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404



def album_list(request):
    albums = Album.objects.all()
    return render(request, 'music/album_list.html', {'albums': albums})

def song_list(request):
    songs = Song.objects.all()
    return render(request, 'music/song_list.html', {'songs': songs})

@login_required
def view_playlists(request, username):
    user = get_object_or_404(User, username=username)
    playlists = Playlist.objects.filter(user=user)
    return render(request, 'music/view_playlists.html', {'playlists': playlists, 'user': user})

@login_required
def create_playlist(request):
    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.user = request.user
            playlist.save()
            messages.success(request, 'Playlist created successfully!')
            return redirect('view_playlists', username=request.user.username)
    else:
        form = PlaylistForm()

    return render(request, 'music/create_playlist.html', {'form': form})

@login_required
def delete_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)

    if request.method == 'POST':
        playlist.delete()
        messages.success(request, 'Playlist deleted successfully!')
        return redirect('view_playlists', username=request.user.username)

    return render(request, 'music/confirm_delete_playlist.html', {'playlist': playlist})


@login_required
def upload_song(request):
    if request.method == 'POST':
        form = SongForm(request.POST, request.FILES)
        if form.is_valid():
            song = form.save(commit=False)
            song.user = request.user
            song.save()
            return redirect('song_list')  # Redirect to a song list page or another view
    else:
        form = SongForm()

    return render(request, 'music/upload_song.html', {'form': form})


@login_required
def view_playlist_songs(request, username, playlist_id):
    # Get the user by username
    user = get_object_or_404(User, username=username)

    # Retrieve the playlist by ID, ensuring it belongs to the correct user
    playlist = get_object_or_404(Playlist, pk=playlist_id, user=user)

    # Ensure the logged-in user is the owner of the playlist
    if playlist.user != request.user:
        raise Http404("You do not have permission to view this playlist.")

    # Render the in_playlist.html template with the playlist data
    return render(request, 'music/in_playlist.html', {'playlist': playlist})
