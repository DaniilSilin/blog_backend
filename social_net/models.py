from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.


class UserProfile(AbstractUser):
    nickname = models.CharField('Никнейм', max_length=255)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Tag(models.Model):
    name = models.CharField('Имя', max_length=255)

    def __str__(self):
        return self.name


class Blog(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField('Заголовок', max_length=255)
    description = models.TextField('Тематика')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата последнего обновления', auto_now=True)
    owner = models.ForeignKey(UserProfile, related_name='blogs', on_delete=models.CASCADE)
    authors = models.ManyToManyField(UserProfile)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Post(models.Model):
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=255)
    body = models.TextField('Тело поста')
    is_published = models.BooleanField('Опубликован ли', default=False)
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    likes = models.IntegerField('Счётчик оценок', default=0)
    views = models.IntegerField('Счётчик просмотров', default=0)
    tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Commentary(models.Model):
    id = models.IntegerField(primary_key=True)
    author = models.ForeignKey(UserProfile, related_name='commentaries', on_delete=models.CASCADE)
    body = models.TextField('Тело комментария')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.body
