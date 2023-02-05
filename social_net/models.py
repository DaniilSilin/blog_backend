from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField('Никнейм', max_length=255)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.user


class Tags(models.Model):
    name = models.CharField('Имя', max_length=255)


class Blog(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    description = models.TextField('Тематика')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата последнего обновления', auto_now=True)
    owner = models.ForeignKey('auth.User', related_name='blogs', on_delete=models.CASCADE)
    authors = models.ManyToManyField(Profile)

    class Meta:
        ordering = ['-created_at', '-updated_at']

    def __str__(self):
        return self.title


class Post(models.Model):
    author = models.OneToOneField(Profile, on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=255)
    body = models.TextField('Тело поста')
    is_published = models.BooleanField('Опубликован ли', default=False)
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    likes = models.IntegerField('Счётчик оценок', default=0)
    views = models.IntegerField('Счётчик просмотров', default=0)

    def __str__(self):
        return self.title


class Commentary(models.Model):
    author = models.ForeignKey('auth.User', related_name='commentaries', on_delete=models.CASCADE)
    body = models.TextField('Тело комментария')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.body
