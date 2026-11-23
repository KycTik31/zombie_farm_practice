from django.contrib.auth.models import AbstractUser
from django.db import models
from django.templatetags.static import static


class User(AbstractUser):
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return static('img/default_avatar.png')
