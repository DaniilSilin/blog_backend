from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    subscriptions = models.ManyToManyField(
        "social_net.Blog", related_name="subscribers", blank=True
    )
    bookmarks = models.ManyToManyField(
        "social_net.Post", related_name="bookmarks", blank=True
    )
    is_admin = models.BooleanField(default=False)
    gender = models.BooleanField("Пол", null=True)
    description = models.TextField("Описание", blank=True)
    date_of_birth = models.DateField("Дата рождения", null=True)
    is_profile_private = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)
    avatar = models.ImageField(
        upload_to="avatars/profile/original/", null=True, blank=True
    )
    avatar_small = models.ImageField(
        upload_to="avatars/profile/small/", null=True, blank=True
    )
    banner = models.ImageField(
        upload_to="banners/profile/original/", null=True, blank=True
    )
    banner_small = models.ImageField(
        upload_to="banners/profile/small/", null=True, blank=True
    )

    def __str__(self):
        return self.username
