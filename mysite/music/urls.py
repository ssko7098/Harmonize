from django.urls import path
from . import views

urlpatterns = [
    path('albums/', views.album_list, name='album_list'),
    path('songs/', views.song_list, name='song_list'),
    path('playlists/<str:username>/', views.view_playlists, name='view_playlists'),  
    path('upload/', views.upload_song, name='upload_song'),
    path('create_playlist/', views.create_playlist, name='create_playlist'),
    path('delete_playlist/<int:playlist_id>/', views.delete_playlist, name='delete_playlist'),
    path('playlists/<str:username>/<int:playlist_id>/', views.view_playlist_songs, name='view_playlist_songs'),  
    path('add_to_playlist/', views.add_to_playlist, name='add_to_playlist'),
    path('delete_song_from_playlist/<int:playlist_id>/<int:song_id>/', views.delete_song_from_playlist, name='delete_song_from_playlist'),  # Delete song from playlist

]
