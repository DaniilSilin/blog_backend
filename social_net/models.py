import datetime
from django.db import models
from authentication.models import UserProfile


class Blog(models.Model):
    title = models.CharField('Заголовок', max_length=255)
    description = models.TextField('Тематика')
    slug = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата последнего обновления', auto_now_add=True)
    owner = models.ForeignKey(UserProfile, related_name='blogs', on_delete=models.CASCADE)
    count_of_posts = models.PositiveIntegerField('Кол-во постов блога', default=0)
    count_of_commentaries = models.PositiveIntegerField('Кол-во комментариев блога', default=0)
    authors = models.ManyToManyField(UserProfile, related_name='blog_list', blank=True)

    def __str__(self):
        return self.slug


class Tag(models.Model):
    name = models.CharField('Имя', unique=True, max_length=255, blank=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField('Заголовок', max_length=255)
    post_id = models.PositiveIntegerField('ID поста', null=True)
    body = models.TextField('Тело поста')
    is_published = models.BooleanField('Опубликован ли', default=False)
    created_at = models.DateTimeField('Дата публикации', null=True, blank=True)
    likes = models.IntegerField('Счётчик оценок', default=0)
    liked_users = models.ManyToManyField('authentication.UserProfile', related_name='alex', blank=True)
    views = models.IntegerField('Счётчик просмотров', default=0)
    blog = models.ForeignKey(Blog, to_field='slug', related_name='posts', on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.is_published:
            if self.created_at is None:
                self.created_at = datetime.datetime.now()
        else:
            self.created_at = None

        last_created_post = Post.objects.filter(is_published=True, blog__slug=self.blog.slug).latest("post_id")
        if last_created_post.created_at > self.blog.updated_at:
            self.blog.updated_at = last_created_post.created_at
            self.blog.save()
        super(Post, self).save(*args, **kwargs)


class Commentary(models.Model):
    author = models.ForeignKey(UserProfile, related_name='commentaries', on_delete=models.CASCADE)
    body = models.TextField('Тело комментария')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment_id = models.PositiveIntegerField('ID комментария', null=True)

    def __str__(self):
        return self.body
