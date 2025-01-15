import datetime
from django.db import models
from authentication.models import UserProfile


class Blog(models.Model):
    avatar = models.ImageField(default='icy.jpg', upload_to='blog_avatars/')
    avatar_small = models.ImageField(default='icy_small.png', upload_to='blog_avatars_small/')
    title = models.CharField('Заголовок', max_length=255)
    email = models.CharField('Email', max_length=255, blank=True)
    phone_number = models.CharField('Номер телефона', max_length=255, blank=True)
    site_link = models.CharField('Cсылка на свой сайт', max_length=255, blank=True)
    description = models.TextField('Тематика')
    pinned_post = models.ForeignKey('Post', related_name='pinned_blogs', blank=True, null=True, on_delete=models.CASCADE)
    slug = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата последнего обновления', auto_now_add=True)
    owner = models.ForeignKey(UserProfile, related_name='blogs', on_delete=models.CASCADE)
    count_of_posts = models.PositiveIntegerField('Кол-во постов блога', default=0)
    count_of_commentaries = models.PositiveIntegerField('Кол-во комментариев блога', default=0)
    authors = models.ManyToManyField(UserProfile, related_name='blog_list', blank=True)
    vk_link = models.CharField('Ссылка на ВК', max_length=255, blank=True)
    dzen_link = models.CharField('Ссылка на Дзен', max_length=255, blank=True)
    ok_link = models.CharField('Ссылка на ОК', max_length=255, blank=True)
    youtube_link = models.CharField('Ссылка на YouTube', max_length=255, blank=True)
    telegram_link = models.CharField('Ссылка на Telegram', max_length=255, blank=True)
    banner = models.ImageField(default='banner.jpg', upload_to='blog_banners/')
    # user_map = models.TextField()

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
    created_at = models.DateTimeField('Дата публикации', auto_now_add=True)
    likes = models.IntegerField('Счётчик оценок', default=0)
    liked_users = models.ManyToManyField('authentication.UserProfile', related_name='alex', blank=True)
    views = models.IntegerField('Счётчик просмотров', default=0)
    blog = models.ForeignKey(Blog, to_field='slug', related_name='posts', on_delete=models.CASCADE)
    tags = models.TextField('Тэги', null=True)
    images = models.ImageField(default='ax.jpg', upload_to='post_images/')
    pinned_comment = models.ForeignKey('Commentary', related_name='pinned_comment', blank=True, null=True, on_delete=models.CASCADE)
    comments_allowed = models.BooleanField('Разрешены ли комментарии', default=True)

    def __str__(self):
        return f"images{self.id}"

    def save(self, *args, **kwargs):
        if self.is_published:
            if self.created_at is None:
                self.created_at = datetime.datetime.now()
                self.blog.updated_at = self.created_at
                self.blog.save()
        super(Post, self).save(*args, **kwargs)


class Commentary(models.Model):
    author = models.ForeignKey(UserProfile, related_name='commentaries', on_delete=models.CASCADE)
    body = models.TextField('Тело комментария')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    post = models.ForeignKey(Post, related_name='comment', on_delete=models.CASCADE)
    comment_id = models.PositiveIntegerField('ID комментария', null=True)
    likes = models.PositiveIntegerField('Лайки', default=0)
    liked_users = models.ManyToManyField(UserProfile, related_name='liked_commentaries', blank=True)
    dislikes = models.PositiveIntegerField('Дизлайки', default=0)
    disliked_users = models.ManyToManyField(UserProfile, related_name='disliked_commentaries', blank=True)
    reply_to = models.ForeignKey('Commentary', on_delete=models.CASCADE, related_name='replies', blank=True, null=True)
    is_edited = models.BooleanField(default=False)
    liked_by_author = models.BooleanField(default=False)

    def __str__(self):
        return str(self.comment_id)


class Invite(models.Model):
    admin = models.ForeignKey(UserProfile, related_name='user_profile', on_delete=models.CASCADE)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    description = models.TextField('Описание')
    addressee = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    status = models.BooleanField('Статус приглашения', null=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.admin)
