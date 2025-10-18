from django.db import models
from authentication.models import UserProfile
from social_net.models import Post


class Commentary(models.Model):
    author = models.ForeignKey(
        UserProfile, related_name="commentaries", on_delete=models.CASCADE
    )
    body = models.TextField("Тело комментария")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    post = models.ForeignKey(Post, related_name="comment", on_delete=models.CASCADE)
    comment_id = models.PositiveIntegerField("ID комментария", null=True)
    likes = models.PositiveIntegerField("Лайки", default=0)
    liked_users = models.ManyToManyField(
        UserProfile, related_name="liked_commentaries", blank=True
    )
    dislikes = models.PositiveIntegerField("Дизлайки", default=0)
    disliked_users = models.ManyToManyField(
        UserProfile, related_name="disliked_commentaries", blank=True
    )
    reply_to = models.ForeignKey(
        "Commentary",
        on_delete=models.CASCADE,
        related_name="replies",
        blank=True,
        null=True,
    )
    is_edited = models.BooleanField(default=False)
    liked_by_author = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    pinned_by_user = models.ForeignKey(
        UserProfile,
        related_name="pinned_commentaries",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    def __str__(self):
        return str(self.comment_id)
