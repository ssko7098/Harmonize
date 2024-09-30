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

        # Custom validation method for the file field
        def clean_file(self):
            file = self.cleaned_data.get('mp3_file')

            if not file.name.endswith('.mp3'):
                raise forms.ValidationError('The file must be in MP3 format.')

            return file