import datetime
from django.db import models
from authentication.models import UserProfile


class Blog(models.Model):
    avatar = models.ImageField(
        upload_to="blog/avatars/original/", null=True, blank=True
    )
    avatar_small = models.ImageField(
        upload_to="blog/avatars/small/", null=True, blank=True
    )
    banner = models.ImageField(
        upload_to="blog/banners/original/", null=True, blank=True
    )
    banner_small = models.ImageField(
        upload_to="blog/banners/small/", null=True, blank=True
    )
    title = models.CharField("Заголовок", max_length=255)
    email = models.CharField("Email", max_length=255, blank=True)
    phone_number = models.CharField("Номер телефона", max_length=255, blank=True)
    description = models.TextField("Тематика", null=True, blank=True)
    slug = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата последнего обновления", auto_now_add=True)
    owner = models.ForeignKey(
        UserProfile, related_name="blogs", on_delete=models.CASCADE
    )
    map = models.TextField("Ссылка на карту")
    count_of_posts = models.PositiveIntegerField("Кол-во постов блога", default=0)
    count_of_commentaries = models.PositiveIntegerField(
        "Кол-во комментариев блога", default=0
    )
    authors = models.ManyToManyField(UserProfile, related_name="blog_list", blank=True)
    vk_link = models.CharField("Ссылка на ВК", max_length=255, blank=True)
    telegram_link = models.CharField("Ссылка на Telegram", max_length=255, blank=True)
    youtube_link = models.CharField("Ссылка на YouTube", max_length=255, blank=True)
    dzen_link = models.CharField("Ссылка на Дзен", max_length=255, blank=True)
    site_link = models.CharField("Cсылка на свой сайт", max_length=255, blank=True)

    def __str__(self):
        return self.slug


class Tag(models.Model):
    name = models.CharField("Имя", unique=True, max_length=255, blank=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    MAP_TYPES = [
        ("interactive", "Интерактивная"),
        ("static", "Статическая"),
        ("null", "Не выбрано"),
    ]

    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField("Заголовок", max_length=255)
    post_id = models.PositiveIntegerField("ID поста", null=True)
    body = models.TextField("Тело поста")
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    likes = models.IntegerField("Счётчик оценок", default=0)
    liked_users = models.ManyToManyField(
        "authentication.UserProfile", related_name="alex", blank=True
    )
    dislikes = models.IntegerField("Счётчик дизлайков", default=0)
    disliked_users = models.ManyToManyField(
        "authentication.UserProfile", related_name="disliked", blank=True
    )
    views = models.IntegerField("Счётчик просмотров", default=0)
    blog = models.ForeignKey(
        Blog, to_field="slug", related_name="posts", on_delete=models.CASCADE
    )
    tags = models.TextField("Тэги", null=True)
    map_type = models.CharField(
        "Тип карты", max_length=50, choices=MAP_TYPES, default="null"
    )
    map = models.TextField("Ссылка на карту", blank=True)
    is_pinned = models.BooleanField("Закреплён ли", default=False)
    is_published = models.BooleanField("Опубликован ли", default=False)
    author_is_hidden = models.BooleanField("Автор скрыт", default=False)
    comments_allowed = models.BooleanField("Разрешены ли комментарии", default=True)

    def __str__(self):
        return str(self.title)

    def save(self, *args, **kwargs):
        if self.is_published:
            if self.created_at is None:
                self.created_at = datetime.datetime.now()
                self.blog.updated_at = self.created_at
                self.blog.save()
        super(Post, self).save(*args, **kwargs)


class PostImage(models.Model):
    post = models.ForeignKey(Post, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="post_images/", null=True, blank=True)

    def __str__(self):
        return str(self.image)
