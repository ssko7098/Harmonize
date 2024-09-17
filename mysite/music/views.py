from django.shortcuts import render
from .models import Album, Song, Playlist

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
