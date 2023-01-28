from django.contrib import admin
from .models import Blog, Post, Profile
# Register your models here.


class AdminPosts(admin.ModelAdmin):
    model = Post
    list_display = ('author', 'title', 'body', 'is_published', 'created_at', 'likes', 'views')


class AdminBlog(admin.ModelAdmin):
    model = Blog
    list_display = ('title', 'description', 'created_at', 'updated_at')


class AdminProfile(admin.ModelAdmin):
    model = Profile
    list_display = ('user', 'username', 'is_admin')


admin.site.register(Post, AdminPosts)
admin.site.register(Blog, AdminBlog)
admin.site.register(Profile, AdminProfile)
