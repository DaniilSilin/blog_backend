from django.contrib import admin
from .models import UserProfile


class AdminProfile(admin.ModelAdmin):
    model = UserProfile
    list_display = ("username", "is_admin")


admin.site.register(UserProfile, AdminProfile)
