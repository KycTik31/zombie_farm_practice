import mimetypes
import os
import re

from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, StreamingHttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_POST
from django.urls import reverse
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


@login_required
def subs(request):
    channels_ids = Subscription.objects.filter(subscriber_id=request.user.id).values_list('channel_id', flat=True)
    channels = User.objects.filter(id__in=channels_ids)
    videos = Video.objects.select_related('author').filter(
        author_id__in=channels_ids
    ).order_by('-created_at')
    return render(request, 'subs.html', {
        'channels': channels,
        'videos': videos,
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


@login_required
@require_POST
def like(request, pk):
    video = get_object_or_404(Video, pk=pk)
    obj, created = Like.objects.get_or_create(user=request.user, video=video)
    if not created:
        obj.delete()
    return JsonResponse({
        'liked': created,
        'count': video.likes.count(),
    })


@login_required
@require_POST
def comment(request, pk):
    video = get_object_or_404(Video, pk=pk)
    text = request.POST.get('text', '').strip()
    if not text:
        return JsonResponse({'error': 'Пустой комментарий'}, status=400)
    c = Comment.objects.create(author=request.user, video=video, text=text)
    return JsonResponse({
        'author': c.author.first_name,
        'avatar_url': c.author.avatar_url,
        'channel_url': reverse('channel', args=[c.author.username]),
        'is_author': c.author_id == video.author_id,
        'text': c.text,
        'created_at': timezone.localtime(c.created_at).strftime('%d.%m.%Y %H:%M'),
        'count': video.comments.count(),
    })


@login_required
@require_POST
def subscribe(request, pk):
    channel_user = get_object_or_404(User, pk=pk)
    is_sub = False
    if channel_user != request.user:
        obj, created = Subscription.objects.get_or_create(subscriber=request.user, channel=channel_user)
        if created:
            is_sub = True
        else:
            obj.delete()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'is_sub': is_sub})
    return redirect('channel', username=channel_user.username)


@login_required
@require_POST
def delete_video(request, pk):
    video = get_object_or_404(Video, pk=pk, author=request.user)
    if video.file:
        video.file.delete(save=False)
    if video.thumbnail:
        video.thumbnail.delete(save=False)
    video.delete()
    return redirect('channel', username=request.user.username)


def channel(request, username):
    channel_user = get_object_or_404(User, username=username)
    videos = Video.objects.filter(author=channel_user).order_by('-created_at')
    is_sub = False
    if request.user.is_authenticated:
        is_sub = Subscription.objects.filter(subscriber=request.user, channel=channel_user).exists()
    return render(request, 'channel.html', {
        'channel': channel_user,
        'videos': videos,
        'is_sub': is_sub,
    })
