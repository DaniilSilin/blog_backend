from django.db import models
from authentication.models import UserProfile
from social_net.models import Post
from comments.models import Commentary


class Notification(models.Model):
    addressee = models.ForeignKey(
        UserProfile, related_name="addressee", on_delete=models.CASCADE
    )
    parent_comment = models.ForeignKey(
        Commentary, on_delete=models.CASCADE, related_name="parent_comment"
    )
    replied_comment = models.ForeignKey(
        Commentary, on_delete=models.CASCADE, related_name="replied_comment"
    )
    post = models.ForeignKey(
        Post, related_name="notifications", on_delete=models.CASCADE
    )
    text = models.TextField("Текст уведомления")
    author = models.ForeignKey(
        UserProfile, related_name="authors", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    is_read = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return str(self.addressee)
