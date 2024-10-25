from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import PlaylistSerializer, SongSerializer
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.permissions import IsAuthenticated
from .models import Playlist, PlaylistSong, Song
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.shortcuts import render, redirect
from .models import Song, Playlist, User, PlaylistSong

# ------------------------- REST API FUNCTIONS ------------------------- #
def get_csrf(request):
    token = get_token(request)
    return JsonResponse({'csrfToken': token})


class ViewUserPlaylists(generics.ListAPIView):
    serializer_class = PlaylistSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        username = self.kwargs.get('username')
        
        if self.request.user.username != username:
            raise Http404("You are not allowed to view this user's playlists.")
        return Playlist.objects.filter(user__username=username)
    

class PlaylistListCreateView(generics.ListCreateAPIView):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RemovePlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)

        playlist.delete()
        return Response({'message': 'Playlist removed successfully.'}, status=status.HTTP_204_NO_CONTENT)

class UpdatePlaylistView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Playlist.objects.all()
    serializer_class = PlaylistSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'playlist_id'  

    def get_queryset(self):
        return Playlist.objects.filter(user=self.request.user)  

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)

        if serializer.is_valid():
            serializer.save(user=self.request.user) 
            return Response({'message': 'Playlist updated successfully.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ViewPlaylistSongs(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, playlist_id):
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        playlist_songs = PlaylistSong.objects.filter(playlist=playlist)
        songs = [ps.song for ps in playlist_songs]  # Get the list of songs in the playlist
        song_serializer = SongSerializer(songs, many=True)

        return Response(song_serializer.data, status=status.HTTP_200_OK)

class AddSongToPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, playlist_id, song_id):
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        song = get_object_or_404(Song, pk=song_id)

        # Check if the song is already in the playlist
        if PlaylistSong.objects.filter(playlist=playlist, song=song).exists():
            return Response({'message': 'Song already in the playlist.'}, status=status.HTTP_400_BAD_REQUEST)

        PlaylistSong.objects.create(playlist=playlist, song=song)
        return Response({'message': 'Song added to playlist successfully.'}, status=status.HTTP_201_CREATED)

class RemoveSongFromPlaylistView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, playlist_id, song_id):
        playlist = get_object_or_404(Playlist, pk=playlist_id, user=request.user)
        song = get_object_or_404(Song, pk=song_id)

        playlist_song = get_object_or_404(PlaylistSong, playlist=playlist, song=song)
        playlist_song.delete()

        return Response({'message': 'Song removed from playlist successfully.'}, status=status.HTTP_204_NO_CONTENT)

# ------------------------- END REST API FUNCTIONS ------------------------- #