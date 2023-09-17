from django.contrib import admin
from .models import Blog, Post, UserProfile, Commentary, Tag


class AdminPosts(admin.ModelAdmin):
    model = Post
    list_display = ('author', 'title', 'body', 'is_published', 'created_at', 'likes', 'views')


class AdminBlog(admin.ModelAdmin):
    model = Blog
    list_display = ('title', 'description', 'created_at', 'updated_at')


class AdminCommentary(admin.ModelAdmin):
    model = Commentary
    list_display = ('author', 'created_at', 'body')


class AdminTags(admin.ModelAdmin):
    model = Tag
    list_display = ('name',)


admin.site.register(Post, AdminPosts)
admin.site.register(Blog, AdminBlog)
admin.site.register(Commentary, AdminCommentary)
admin.site.register(Tag, AdminTags)
