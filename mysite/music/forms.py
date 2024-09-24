from django import forms
from .models import Song


class SongForm(forms.ModelForm):
    class Meta:
        model = Song
        fields = ['title', 'mp3_file']

        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'mp3_file': forms.FileInput(attrs={'class': 'form-control-file'}),
        }