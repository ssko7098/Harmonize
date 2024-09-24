from django.shortcuts import render, redirect
from .models import Album, Song, Playlist
from .forms import SongForm
from django.contrib.auth.decorators import login_required

# Create your views here.
def album_list(request):
    albums = Album.objects.all()
    return render(request, 'music/album_list.html', {'albums': albums})

def song_list(request):
    songs = Song.objects.all()
    return render(request, 'music/song_list.html', {'songs': songs})

def playlist_list(request):
    playlists = Playlist.objects.all()
    return render(request, 'music/playlist_list.html', {'playlists': playlists})

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