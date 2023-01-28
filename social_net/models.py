from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField('Никнейм', max_length=255)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Blog(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    description = models.TextField('Тематика')
    created_at = models.DateTimeField('Дата создания')
    updated_at = models.DateTimeField('Дата последнего обновления')
    authors = models.ManyToManyField(Profile)

    def __str__(self):
        return self.title


class Post(models.Model):
    author = models.OneToOneField(Profile, on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=255)
    body = models.TextField('Тело поста')
    is_published = models.BooleanField('Опубликован ли')
    created_at = models.DateTimeField('Дата публикации')
    likes = models.IntegerField('Счётчик оценок')
    views = models.IntegerField('Счётчик просмотров')

    def __str__(self):
        return self.author


class Commentary(models.Model):
    body = models.TextField('Тело комментария')
    created_at = models.DateTimeField('Дата создания')

    def __str__(self):
        return self.body
