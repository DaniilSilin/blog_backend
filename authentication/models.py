from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    subscriptions = models.ManyToManyField('social_net.Blog', related_name="subscribers", blank=True)
    bookmarks = models.ManyToManyField('social_net.Post', related_name='bookmarks', blank=True)
    is_admin = models.BooleanField(default=False)
    avatar = models.ImageField(default='icy.jpg', upload_to='users_avatars/original/')
    avatar_small = models.ImageField(default='icy.jpg', upload_to='users_avatars/small/')
    # description = models.TextField('Описание', blank=True)
    # gender = models.CharField()
    # date_of_birth = models.DateField()
    # is_profile_private = models.BooleanField(default=False)

    def __str__(self):
        return self.username
