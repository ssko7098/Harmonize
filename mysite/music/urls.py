from django.urls import path
from . import views

urlpatterns = [
    path('albums/', views.album_list, name='album_list'),
    path('songs/', views.song_list, name='song_list'),
    path('playlists/', views.playlist_list, name='playlist_list'),
    path('upload/', views.upload_song, name='upload_song'),
]
