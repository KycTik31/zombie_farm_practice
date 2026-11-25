from django import forms
from django.core.exceptions import ValidationError

from .models import Video
import filetype


class UploadVideoForm(forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'description', 'file', 'thumbnail')
        labels = {
            'title': 'Название видео',
            'description': 'Описание видео',
            'file': 'Файл',
            'thumbnail': 'Обложка',
        }
        widgets = {
            'file': forms.FileInput(attrs={'accept': '.mp4,.webm,video/mp4,video/webm'}),
            'thumbnail': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            return file

        kind = filetype.guess(file)

        if not kind or kind.mime not in ('video/mp4', 'video/webm'):
            raise ValidationError('Разрешены только .mp4 и .webm')

        return file
