from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from rest_framework.test import APITestCase
from rest_framework import status
from unittest.mock import patch, mock_open, Mock
from .models import Song, Playlist, PlaylistSong
from .forms import SongForm, PlaylistForm
from .external_api import upload_mp3_to_assemblyai, get_transcription
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class PlaylistViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password', email='test@example.com')
        self.user.is_verified = True 
        self.user.save()
        self.client.login(username='testuser', password='password')
        with open("music/mp3/test.mp3", "rb") as mp3_file:
            self.mock_mp3_file = SimpleUploadedFile("music/mp3/test.mp3", mp3_file.read(), content_type="audio/mpeg")


    def test_view_playlists(self):
        Playlist.objects.create(user=self.user, name="My Playlist")
        response = self.client.get(reverse('view_playlists', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Playlist")

    def test_create_playlist(self):
        response = self.client.post(reverse('create_playlist'), {'name': 'New Playlist', 'description': 'Test Description'})
        self.assertEqual(response.status_code, 302)  # Redirect after creation
        self.assertEqual(Playlist.objects.count(), 1)
        playlist = Playlist.objects.first()
        self.assertEqual(playlist.name, 'New Playlist')

    def test_delete_playlist(self):
        playlist = Playlist.objects.create(user=self.user, name="Playlist to Delete")
        self.client.login(username='testuser', password='password')
        response = self.client.post(reverse('delete_playlist', args=[playlist.playlist_id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Playlist.objects.filter(pk=playlist.playlist_id).count(), 0)

    @patch("mutagen.mp3.MP3")
    def test_upload_song(self, mock_mp3):
        response = self.client.post(reverse('upload_song'), {
            'title': 'Test Song',
            'mp3_file': self.mock_mp3_file
        })

        self.assertEqual(response.status_code, 302) 

        song = Song.objects.filter(title="Test Song", user=self.user).first()
        self.assertIsNotNone(song)
        self.assertTrue(song.mp3_file.name.endswith(".mp3"))


    def test_view_playlist_songs(self):
        song = Song.objects.create(user=self.user, title="Test Song", mp3_file=self.mock_mp3_file)
        playlist = Playlist.objects.create(user=self.user, name="Test Playlist")
        PlaylistSong.objects.create(playlist=playlist, song=song)
        response = self.client.get(reverse('view_playlist_songs', args=[self.user.username, playlist.playlist_id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Song")

    def test_add_to_playlist(self):
        playlist = Playlist.objects.create(user=self.user, name="Add Song Playlist")
        song = Song.objects.create(user=self.user, title="Song to Add")
        
        response = self.client.post(reverse('add_to_playlist'), {
            'playlist': playlist.playlist_id,
            'song_id': song.song_id
        })
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(PlaylistSong.objects.filter(playlist=playlist, song=song).exists())

    def test_delete_song_from_playlist(self):
        playlist = Playlist.objects.create(user=self.user, name="Delete Song Playlist")
        song = Song.objects.create(user=self.user, title="Song to Delete")
        playlist_song = PlaylistSong.objects.create(playlist=playlist, song=song)
        
        response = self.client.post(reverse('delete_song_from_playlist', args=[playlist.playlist_id, song.song_id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(PlaylistSong.objects.filter(playlist=playlist, song=song).exists())

    def test_report_song(self):
        song = Song.objects.create(user=self.user, title="Song to Report")
        response = self.client.post(reverse('report_song', args=[song.song_id]))
        self.assertEqual(response.status_code, 302)
        song.refresh_from_db()
        self.assertEqual(song.report_count, 1)

    def test_liked_songs(self):
        song = Song.objects.create(user=self.user, title="Liked Song")
        response = self.client.get(reverse('liked_songs', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)

        response = self.client.get(reverse('liked_songs', args=[self.user.username]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Liked Song")

    def test_add_to_liked_songs(self):
        song = Song.objects.create(user=self.user, title="Likeable Song")
        response = self.client.post(reverse('add_to_liked_songs', args=[song.song_id]))
        self.assertEqual(response.status_code, 302)
        song.refresh_from_db()
        self.assertIn(self.user, song.liked_by.all())

    def test_remove_liked_song(self):
        song = Song.objects.create(user=self.user, title="Unlikable Song")
        song.liked_by.add(self.user)
        response = self.client.post(reverse('remove_liked_song', args=[song.song_id]))
        self.assertEqual(response.status_code, 302)
        song.refresh_from_db()
        self.assertNotIn(self.user, song.liked_by.all())


class SongModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='password', email='test@example.com')
        self.song = Song.objects.create(user=self.user, title="Reportable Song")

    def test_song_clean_invalid_file_type(self):
        song = Song(user=self.user, title="Test Song", mp3_file="song.txt")
        with self.assertRaises(ValidationError):
            song.clean()

class PlaylistSongModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser', password='password', email='test@example.com')
        self.playlist = Playlist.objects.create(user=self.user, name="Test Playlist")
        self.song = Song.objects.create(user=self.user, title="Test Song")

    def test_unique_song_in_playlist(self):
        song = Song.objects.create(user=self.user, title="Unique Song", mp3_file=None)
        playlist = Playlist.objects.create(user=self.user, name="Test Playlist")
        PlaylistSong.objects.create(playlist=playlist, song=song)
        
        self.assertFalse(song.mp3_file)

class SongFormTests(TestCase):
    def test_song_form_invalid_file_type(self):
        form_data = {'title': 'Test Song'}
        file_data = {'mp3_file': SimpleUploadedFile('song.txt', b'file_content')}
        form = SongForm(data=form_data, files=file_data)
        self.assertFalse(form.is_valid())

    def test_song_form_valid_file_type(self):
        form_data = {'title': 'Test Song'}
        file_data = {'mp3_file': SimpleUploadedFile('song.mp3', b'file_content')}
        form = SongForm(data=form_data, files=file_data)
        self.assertTrue(form.is_valid())

    def test_song_form_missing_title(self):
        file_data = {'mp3_file': SimpleUploadedFile('song.mp3', b'file_content')}
        form = SongForm(data={}, files=file_data)
        self.assertFalse(form.is_valid())  


class PlaylistFormTests(TestCase):
    def test_playlist_form_valid(self):
        form_data = {'name': 'My Playlist', 'description': 'A test playlist'}
        form = PlaylistForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_playlist_form_missing_name(self):
        form_data = {'description': 'A test playlist'}
        form = PlaylistForm(data=form_data)
        self.assertFalse(form.is_valid()) 

    def test_playlist_form_empty_description(self):
        form_data = {'name': 'My Playlist', 'description': ''}
        form = PlaylistForm(data=form_data)
        self.assertTrue(form.is_valid()) 

    def test_playlist_form_max_length_name(self):
        form_data = {'name': 'A' * 101, 'description': 'A test playlist'}
        form = PlaylistForm(data=form_data)
        self.assertFalse(form.is_valid())


class AssemblyAITests(TestCase):
    @patch('requests.post')
    def test_upload_mp3_to_assemblyai(self, mock_post):
        mock_response = {'upload_url': 'https://api.assemblyai.com/v2/upload/12345'}
        mock_post.return_value.json.return_value = mock_response
        with patch("builtins.open", mock_open(read_data="data")) as mock_file:
            upload_url = upload_mp3_to_assemblyai("fake_path.mp3")
        self.assertEqual(upload_url, mock_response['upload_url'])

    @patch('requests.post')
    @patch('requests.get')
    def test_get_transcription_completed(self, mock_get, mock_post):
        mock_post.return_value.json.return_value = {'id': 'transcript_id_123'}
        mock_get.return_value.json.side_effect = [{'status': 'processing'}, {'status': 'completed', 'text': 'Transcription result'}]
        transcription_text = get_transcription("https://api.assemblyai.com/v2/upload/12345")
        self.assertEqual(transcription_text, 'Transcription result')



class PlaylistAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.client.force_authenticate(user=self.user)

    def test_create_playlist(self):
        url = reverse("playlist-list-create")
        response = self.client.post(url, {"name": "New Playlist"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], "New Playlist")

    def test_view_user_playlists(self):
        Playlist.objects.create(user=self.user, name="My Playlist")
        url = reverse("playlist-detail", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "My Playlist")

    def test_update_playlist(self):
        playlist = Playlist.objects.create(user=self.user, name="Initial Name")
        url = reverse("update-playlist", kwargs={"playlist_id": playlist.playlist_id})
        response = self.client.patch(url, {"name": "Updated Name"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        playlist.refresh_from_db()
        self.assertEqual(playlist.name, "Updated Name")

    def test_remove_playlist(self):
        playlist = Playlist.objects.create(user=self.user, name="Playlist to Remove")
        url = reverse("remove-playlist", kwargs={"playlist_id": playlist.playlist_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Playlist.objects.filter(pk=playlist.playlist_id).exists())


class PlaylistSongAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.client.force_authenticate(user=self.user)
        self.playlist = Playlist.objects.create(user=self.user, name="Test Playlist")
        self.song = Song.objects.create(user=self.user, title="Test Song")

    def test_add_song_to_playlist(self):
        url = reverse("add-song-to-playlist", kwargs={"playlist_id": self.playlist.playlist_id, "song_id": self.song.song_id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(PlaylistSong.objects.filter(playlist=self.playlist, song=self.song).exists())

    def test_remove_song_from_playlist(self):
        PlaylistSong.objects.create(playlist=self.playlist, song=self.song)
        url = reverse("remove-song-from-playlist", kwargs={"playlist_id": self.playlist.playlist_id, "song_id": self.song.song_id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(PlaylistSong.objects.filter(playlist=self.playlist, song=self.song).exists())


class ViewPlaylistSongsAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.client.force_authenticate(user=self.user)
        self.playlist = Playlist.objects.create(user=self.user, name="Test Playlist")
        self.song = Song.objects.create(user=self.user, title="Test Song")
        PlaylistSong.objects.create(playlist=self.playlist, song=self.song)

    def test_view_playlist_songs(self):
        url = reverse("view-playlist-songs", kwargs={"playlist_id": self.playlist.playlist_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Test Song")


class ViewPlaylistSongsTemplateTests(TestCase):
    @patch("mutagen.mp3.MP3")  
    def setUp(self, mock_mp3):
        mock_mp3.return_value.info.length = 60.0 

        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.user.is_verified = True 
        self.user.save()
        self.client.login(username='testuser', password='password')        
        
        self.playlist = Playlist.objects.create(user=self.user, name="Test Playlist", description="A test playlist description")
        with open("music/mp3/test.mp3", "rb") as mp3_file:
            self.mock_mp3_file = SimpleUploadedFile("music/mp3/test.mp3", mp3_file.read(), content_type="audio/mpeg")

        self.song = Song.objects.create(user=self.user, title="Test Song", mp3_file=self.mock_mp3_file)
        PlaylistSong.objects.create(playlist=self.playlist, song=self.song)

    def test_view_playlist_songs_template_with_song(self):
        url = reverse("view_playlist_songs", kwargs={"username": self.user.username, "playlist_id": self.playlist.playlist_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.playlist.name)
        self.assertContains(response, self.playlist.description)
        self.assertContains(response, self.song.title)

        self.assertTemplateUsed(response, 'music/in_playlist.html')
        self.assertTemplateUsed(response, 'base.html') 

    def test_view_playlist_songs_template_empty_playlist(self):
        PlaylistSong.objects.all().delete()
        
        url = reverse("view_playlist_songs", kwargs={"username": self.user.username, "playlist_id": self.playlist.playlist_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No songs in this playlist yet.")

        self.assertTemplateUsed(response, 'music/in_playlist.html')
        self.assertTemplateUsed(response, 'base.html')

class LikedSongsTemplateTests(TestCase):
    @patch("mutagen.mp3.MP3")  
    def setUp(self, mock_mp3):
        mock_mp3.return_value.info.length = 60.0

        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.user.is_verified = True 
        self.user.save()
        self.client.login(username="testuser", password="password")

        with open("music/mp3/test.mp3", "rb") as mp3_file:
            self.mock_mp3_file = SimpleUploadedFile("music/mp3/test.mp3", mp3_file.read(), content_type="audio/mpeg")
        
        self.song = Song.objects.create(user=self.user, title="Test Song", mp3_file=self.mock_mp3_file)
        self.song.liked_by.add(self.user)

    def test_liked_songs_template_with_liked_song(self):
        url = reverse("liked_songs", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Liked Songs")
        self.assertContains(response, "Test Song")
        self.assertContains(response, "Clear Search")

        self.assertTemplateUsed(response, "music/liked_songs.html")
        self.assertTemplateUsed(response, "base.html")

class UploadSongTemplateTests(TestCase):
    @patch("mutagen.mp3.MP3")
    def setUp(self, mock_mp3):
        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.user.is_verified = True
        self.user.save()
        self.client.login(username="testuser", password="password")

    def test_upload_song_template_rendering(self):
        response = self.client.get(reverse("upload_song"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'music/upload_song.html')
        self.assertContains(response, "Upload a New Song")
        self.assertContains(response, "Single Name")
        self.assertContains(response, "Upload MP3 Audio")
        self.assertContains(response, "Choose Single Cover")
        self.assertContains(response, "Upload")

class LibraryTemplateTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="password", email="test@example.com")
        self.user.is_verified = True 
        self.user.save()
        self.client.login(username="testuser", password="password")
        self.playlist = Playlist.objects.create(user=self.user, name="Test Playlist", description="A test playlist description")
        with open("music/mp3/test.mp3", "rb") as mp3_file:
            mp3_data = SimpleUploadedFile("music/mp3/test.mp3", mp3_file.read(), content_type="audio/mpeg")
            self.song = Song.objects.create(user=self.user, title="Test Song", mp3_file=mp3_data)
            PlaylistSong.objects.create(playlist=self.playlist, song=self.song)

    def test_library_template_with_playlists(self):
        self.assertTrue(self.client.login(username="testuser", password="password"))
        url = reverse("view_playlists", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your Library")
        self.assertContains(response, "Test Playlist")
        self.assertContains(response, "View Songs")
        self.assertTemplateUsed(response, "music/view_playlists.html")
        self.assertTemplateUsed(response, "base.html")

    def test_library_template_no_playlists(self):
        self.assertTrue(self.client.login(username="testuser", password="password"))
        Playlist.objects.all().delete()
        
        url = reverse("view_playlists", kwargs={"username": self.user.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No current playlists available.")