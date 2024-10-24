from django.db import models
from users.models import User
from mutagen.mp3 import MP3
from datetime import timedelta
from django.core.exceptions import ValidationError 
import os

# Create your models here.
class Album(models.Model):
    album_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    report_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

class Song(models.Model):
    song_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    album = models.ForeignKey(Album, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=30)
    duration = models.DurationField(editable=False, null=True)
    mp3_file = models.FileField(upload_to='songs/', null=True)
    cover_image_file = models.FileField(upload_to='cover_art/', null=True, blank=True)
    report_count = models.PositiveIntegerField(default=0)
    liked_by = models.ManyToManyField(User, related_name='liked_songs', blank=True)

    reported_by = models.ManyToManyField(User, related_name='reported_songs', blank=True)


    def clean(self):
        if not self.mp3_file.name.endswith('.mp3'):
            raise ValidationError('Only .mp3 files are allowed.')
        
        if not self.cover_image_file.name.endswith(('.jpg', '.jpeg')):
            raise ValidationError('Only JPEG files are allowed.')

    def save(self, *args, **kwargs):
        # If a new file is uploaded or the song is newly created, calculate duration
        if self.mp3_file:
            audio = MP3(self.mp3_file)
            self.duration = timedelta(seconds=audio.info.length)  # length in seconds
        super(Song, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Delete the mp3 file from storage
        if self.mp3_file and os.path.isfile(self.mp3_file.path):
            os.remove(self.mp3_file.path)

        if self.cover_image_file and os.path.isfile(self.cover_image_file.path):
            os.remove(self.cover_image_file.path)

        # Call the parent class's delete method to delete the Song instance
        super(Song, self).delete(*args, **kwargs)

    def __str__(self):
        return self.title

class Playlist(models.Model):
    playlist_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.TextField(null=True, blank=True)
    report_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name

class PlaylistSong(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE)
    song = models.ForeignKey(Song, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('playlist', 'song')

    def __str__(self):
        return f'{self.playlist.name} - {self.song.title}'