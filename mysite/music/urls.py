from django.urls import path
from . import views
from .views import PlaylistListCreateView, ViewUserPlaylists, RemovePlaylistView, UpdatePlaylistView, get_csrf
from .views import ViewPlaylistSongs, AddSongToPlaylistView
from .views import get_csrf 

urlpatterns = [
    path('playlists/create/', PlaylistListCreateView.as_view(), name='playlist-list-create'),
    path('playlists/<str:username>/', ViewUserPlaylists.as_view(), name='playlist-detail'),
    path('playlists/<int:playlist_id>/remove/', RemovePlaylistView.as_view(), name='remove-playlist'),
    path('playlists/<int:playlist_id>/update/', UpdatePlaylistView.as_view(), name='update-playlist'),
    path('playlists/<int:playlist_id>/songs/', ViewPlaylistSongs.as_view(), name='view-playlist-songs'),
    path('playlists/<int:playlist_id>/songs/<int:song_id>/add/', AddSongToPlaylistView.as_view(), name='add-song-to-playlist'),
    path('albums/', views.album_list, name='album_list'),
    path('<str:username>/playlists/', views.view_playlists, name='view_playlists'),  
    path('upload/', views.upload_song, name='upload_song'),
    path('create_playlist/', views.create_playlist, name='create_playlist'),
    path('delete_playlist/<int:playlist_id>/', views.delete_playlist, name='delete_playlist'),
    path('playlists/<str:username>/<int:playlist_id>/', views.view_playlist_songs, name='view_playlist_songs'),  
    path('add_to_playlist/', views.add_to_playlist, name='add_to_playlist'),
    path('delete_song_from_playlist/<int:playlist_id>/<int:song_id>/', views.delete_song_from_playlist, name='delete_song_from_playlist'), 
    path('playlists/<str:username>/<int:playlist_id>/', views.view_playlist_songs, name='view_playlist_songs'),  # Shows songs in a playlist
    path('report_song/<int:song_id>/', views.report_song, name='report_song'),
    path('song/<int:song_id>/', views.song_details, name='song_details'),
    path('playlists/<str:username>/liked/', views.liked_songs, name='liked_songs'),
    path('add_to_liked_songs/<int:song_id>/', views.add_to_liked_songs, name='add_to_liked_songs'),
    path('remove_liked_song/<int:song_id>/', views.remove_liked_song, name='remove_liked_song'),
    path('get-csrf/', get_csrf, name='get-csrf')
] 