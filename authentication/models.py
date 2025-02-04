from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    subscriptions = models.ManyToManyField('social_net.Blog', related_name="subscribers", blank=True)
    bookmarks = models.ManyToManyField('social_net.Post', related_name='bookmarks', blank=True)
    is_admin = models.BooleanField(default=False)
    gender = models.BooleanField('Пол', null=True)
    description = models.TextField('Описание', blank=True)
    date_of_birth = models.DateField('Дата рождения', null=True)
    is_profile_private = models.BooleanField(default=False)
    last_activity = models.DateTimeField(auto_now=True)
    age = models.PositiveIntegerField('Возраст', null=True)
    avatar = models.ImageField(default='default/original/avatar.jpg', upload_to='avatars/profile/original/')
    avatar_small = models.ImageField(default='default/original/avatar.jpg', upload_to='avatars/profile/small/')
    banner = models.ImageField(default='default/original/banner.jpg', upload_to='banners/profile/original/')
    banner_small = models.ImageField(default='default/small/banner.jpg', upload_to='banners/profile/small/')


    def __str__(self):
        return self.username
