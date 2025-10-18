from django.contrib import admin
from .models import Notification


class AdminNotifications(admin.ModelAdmin):
    model = Notification
    list_display = ("addressee", "author", "created_at", "is_read")


admin.site.register(Notification, AdminNotifications)
