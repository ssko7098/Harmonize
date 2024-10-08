from django.shortcuts import render, redirect
from .models import Album, Song, Playlist, User, PlaylistSong
from .forms import SongForm, PlaylistForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404



def album_list(request):
    albums = Album.objects.all()
    return render(request, 'music/album_list.html', {'albums': albums})

@login_required
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
def delete_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)

    if request.method == 'POST':
        playlist.delete()
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
            return redirect('song_details', song_id=song.song_id)
    else:
        form = SongForm()

    return render(request, 'music/upload_song.html', {'form': form})

@login_required
def song_details(request, song_id):
    song = Song.objects.get(song_id=song_id)
    return render(request, 'music/song_details.html', {'song': song}) 

@login_required
def view_playlist_songs(request, username, playlist_id):
    user = get_object_or_404(User, username=username)

    playlist = get_object_or_404(Playlist, pk=playlist_id, user=user)

    if playlist.user != request.user:
        raise Http404("You do not have permission to view this playlist.")
    
    return render(request, 'music/in_playlist.html', {'playlist': playlist})

@login_required
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
def delete_song_from_playlist(request, playlist_id, song_id):
    playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
    song = get_object_or_404(Song, pk=song_id)

    if request.method == 'POST':
        playlist_song = get_object_or_404(PlaylistSong, playlist=playlist, song=song)
        playlist_song.delete()
    
    return redirect('view_playlist_songs', username=request.user.username, playlist_id=playlist.pk)

@login_required
def view_playlist_songs(request, username, playlist_id):
    user = get_object_or_404(User, username=username)
    playlist = get_object_or_404(Playlist, pk=playlist_id, user=user)

    # Ensure the logged-in user is the owner of the playlist
    if playlist.user != request.user:
        raise Http404("You do not have permission to view this playlist.")

    search_query = request.GET.get('search', '')

    if search_query:
        filtered_songs = PlaylistSong.objects.filter(playlist=playlist, song__title__icontains=search_query)
    else:
        filtered_songs = playlist.playlistsong_set.all()

    # Render the in_playlist.html template with the playlist data
    return render(request, 'music/in_playlist.html', {'playlist': playlist, 'filtered_songs': filtered_songs})

@login_required
def report_song(request, song_id):
    song = get_object_or_404(Song, song_id=song_id)
    
    # Increment the report count
    song.report_count += 1
    song.save()

    # Redirect back to search with the original query
    query = request.session.get('last_search_query', '')
    if query:
        return redirect(f'/search/?query={query}')
    return redirect('home')


@login_required
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
