from django.urls import path
from . import views

urlpatterns = [
    path('albums/', views.album_list, name='album_list'),
    path('songs/', views.song_list, name='song_list'),
    path('playlists/<str:username>/', views.view_playlists, name='view_playlists'),
    path('upload/', views.upload_song, name='upload_song'),
    path('create_playlist/', views.create_playlist, name='create_playlist'),
    path('delete_playlist/<int:playlist_id>/', views.delete_playlist, name='delete_playlist'),


]
