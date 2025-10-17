from django.db import models
from authentication.models import UserProfile
from social_net.models import Blog


class Invite(models.Model):
    admin = models.ForeignKey(
        UserProfile, related_name="user_profile", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    replied_at = models.DateTimeField("Дата ответа", null=True, blank=True)
    description = models.TextField("Описание")
    addressee = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    status = models.BooleanField("Статус приглашения", null=True)
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name="invites")

    def __str__(self):
        return str(self.admin)
