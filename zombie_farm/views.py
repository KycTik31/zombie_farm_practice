from types import SimpleNamespace

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.templatetags.static import static
from django.contrib.auth import get_user_model
from django.utils import timezone

from .forms import UploadVideoForm
from .models import *

User = get_user_model()


def index(request):
    return render(request, 'index.html', {
        'videos': Video.objects.none(),
    })


def subs(request):
    return render(request, 'subs.html', {
        'channels': [],
        'videos': Video.objects.none(),
    })


@login_required
def upload(request):
    if request.method == 'POST':
        form = UploadVideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.author = request.user
            video.save()
            return redirect('watch', pk=video.pk)
    else:
        form = UploadVideoForm()
    return render(request, 'upload.html', {
        'form': form,
    })


def watch(request, pk):
    fake_author = SimpleNamespace(
        pk=1,
        username='admin',
        avatar_url=static('img/default_avatar.png'),
    )
    fake_video = SimpleNamespace(
        pk=pk,
        title=f'Тестовое видео #{pk}',
        thumbnail=None,
        author=fake_author,
        views={'count': 123},
        likes={'count': 42},
        created_at=timezone.now(),
        description='Заглушка описания для проверки внешнего вида страницы.',
    )
    return render(request, 'watch.html', {
        'video': fake_video,
        'comments': Comment.objects.none(),
        'other_videos': Video.objects.none(),
        'is_liked': False,
        'is_sub': False,
    })


def stream(request):
    return HttpResponse(status=204)


def like(request, pk):
    return redirect('watch', pk=pk)


def comment(request, pk):
    return redirect('watch', pk=pk)


def delete_video(request, pk):
    return redirect('index')


def channel(request, username):
    fake_channel = SimpleNamespace(
        pk=1,
        username=username,
        avatar_url=static('img/default_avatar.png'),
        subscribers={'count': 10},
    )
    return render(request, 'channel.html', {
        'channel': fake_channel,
        'videos': Video.objects.none(),
        'is_sub': False,
    })


def subscribe(request, pk):
    return redirect(request.META.get('HTTP_REFERER') or 'index')
