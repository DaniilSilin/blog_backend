from django.contrib import admin
from .models import Invite


class AdminInvite(admin.ModelAdmin):
    model = Invite
    list_display = ("admin", "pk", "description", "addressee", "blog")


admin.site.register(Invite, AdminInvite)
