from django import forms
from .models import Video


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
