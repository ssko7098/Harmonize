from django.shortcuts import render, redirect
from .models import Album, Song, Playlist, User
from .forms import SongForm, PlaylistForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404


# Create your views here.
def album_list(request):
    albums = Album.objects.all()
    return render(request, 'music/album_list.html', {'albums': albums})

def song_list(request):
    songs = Song.objects.all()
    return render(request, 'music/song_list.html', {'songs': songs})

def view_playlists(request, username):
    user = get_object_or_404(User, username=username)
    playlists = Playlist.objects.filter(user=user)
    return render(request, 'music/view_playlists.html', {'playlists': playlists})


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