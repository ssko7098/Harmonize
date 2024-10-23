from rest_framework import serializers
from .models import Playlist, PlaylistSong, Song

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['song_id', 'title', 'duration', 'mp3_file', 'cover_image_file']


class PlaylistSerializer(serializers.ModelSerializer):
    songs = serializers.SerializerMethodField()

    class Meta:
        model = Playlist
        fields = ['playlist_id', 'name', 'description', 'report_count', 'songs']
        read_only_fields = ['playlist_id', 'report_count', 'user']

    def get_songs(self, playlist):
        playlist_songs = PlaylistSong.objects.filter(playlist=playlist)
        songs = [ps.song for ps in playlist_songs]  # Get the Song instances
        return SongSerializer(songs, many=True).data
    