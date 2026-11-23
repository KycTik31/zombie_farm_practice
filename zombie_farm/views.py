import mimetypes
import os
import re
from types import SimpleNamespace

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse, StreamingHttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.templatetags.static import static
from django.contrib.auth import get_user_model
from django.utils import timezone

from .forms import UploadVideoForm
from .models import *

User = get_user_model()


def index(request):
    videos = Video.objects.order_by('-created_at')
    if query := request.GET.get('q', '').strip():
        videos = videos.filter(title__icontains=query)
    return render(request, 'index.html', {
        'videos': videos,
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
    video = get_object_or_404(Video, pk=pk)
    comments = video.comments.select_related('author').order_by('-created_at')
    other_videos = Video.objects.select_related('author').exclude(pk=pk).order_by('-created_at')[:6]
    is_liked = False
    is_sub = False
    if request.user.is_authenticated:
        View.objects.get_or_create(user=request.user, video=video)
        is_liked = Like.objects.filter(user=request.user, video=video.id).exists()
        is_sub = Subscription.objects.filter(subscriber_id=request.user.id, channel_id=video.author.id).exists()
    return render(request, 'watch.html', {
        'video': video,
        'comments': comments,
        'other_videos': other_videos,
        'is_liked': is_liked,
        'is_sub': is_sub,
    })


def file_iterator(path, offset=0, length=None):
    with open(path, 'rb') as f:
        f.seek(offset)
        remaining = length
        while True:
            read_size = 1048576 if remaining is None else min(1048576, remaining)
            if read_size <= 0:
                break
            data = f.read(read_size)
            if not data:
                break
            if remaining is not None:
                remaining -= len(data)
            yield data


def stream(request, pk):
    video = get_object_or_404(Video, pk=pk)
    path = video.file.path
    file_size = os.path.getsize(path)
    content_type, _ = mimetypes.guess_type(path)
    content_type = content_type or 'video/mp4'

    range_header = request.headers.get('Range', '').strip()
    match = re.compile(r'bytes=(\d+)-(\d*)').match(range_header)

    if match:
        start = int(match.group(1))
        end = int(match.group(2)) if match.group(2) else min(start + 1048576 - 1, file_size - 1)
        end = min(end, file_size - 1)

        if start >= file_size:
            resp = HttpResponse(status=416)
            resp['Content-Range'] = f'bytes */{file_size}'
            return resp

        length = end - start + 1
        resp = StreamingHttpResponse(file_iterator(path, start, length), status=206, content_type=content_type)
        resp['Content-Range'] = f'bytes {start}-{end}/{file_size}'
        resp['Content-Length'] = str(length)
    else:
        resp = StreamingHttpResponse(file_iterator(path), status=200, content_type=content_type)
        resp['Content-Length'] = str(file_size)

    resp['Accept-Ranges'] = 'bytes'
    return resp


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
