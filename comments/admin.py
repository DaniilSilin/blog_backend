from django.contrib import admin
from .models import Commentary


class AdminCommentary(admin.ModelAdmin):
    model = Commentary
    list_display = (
        "author",
        "created_at",
        "body",
        "comment_id",
        "reply_to",
        "reply_to_id",
        "post",
    )


admin.site.register(Commentary, AdminCommentary)
