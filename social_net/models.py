from django.db import models
from authentication.models import UserProfile


class Blog(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    description = models.TextField('Тематика')
    slug = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата последнего обновления', auto_now=True)
    owner = models.ForeignKey(UserProfile, related_name='blogs', on_delete=models.CASCADE)
    authors = models.ManyToManyField(UserProfile)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Post(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=255)
    post_id = models.PositiveIntegerField('ID поста', null=True)
    body = models.TextField('Тело поста')
    is_published = models.BooleanField('Опубликован ли', default=False)
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    likes = models.IntegerField('Счётчик оценок', default=0)
    views = models.IntegerField('Счётчик просмотров', default=0)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)
    # tags = models.ManyToManyField(Tag, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Tag(models.Model):
    name = models.CharField('Имя', max_length=255)

    def __str__(self):
        return self.name


class Commentary(models.Model):
    author = models.ForeignKey(UserProfile, related_name='commentaries', on_delete=models.CASCADE)
    body = models.TextField('Тело комментария')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.body
