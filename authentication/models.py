from django.db import models
from django.contrib.auth.models import AbstractUser


class UserProfile(AbstractUser):
    is_admin = models.BooleanField(default=True)

    def __str__(self):
        return self.username
