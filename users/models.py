import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static


def avatar_upload_path(instance, filename):
    return f'avatars/{uuid.uuid4().hex}.{filename.split(".")[-1]}'


class User(AbstractUser):
    avatar = models.ImageField(upload_to=avatar_upload_path, null=True, blank=True)

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return static('img/default_avatar.png')
