from django.contrib import admin
from .models import Blog, Post, UserProfile, Commentary, Tag, Invite


class AdminPosts(admin.ModelAdmin):
    model = Post
    list_display = ('author', 'title', 'body', 'is_published', 'created_at', 'likes', 'views', 'post_id')


class AdminBlog(admin.ModelAdmin):
    model = Blog
    list_display = ('title', 'slug', 'description', 'created_at', 'updated_at')


class AdminCommentary(admin.ModelAdmin):
    model = Commentary
    list_display = ('author', 'created_at', 'body', 'comment_id', 'post')


class AdminInvite(admin.ModelAdmin):
    model = Invite
    list_display = ('admin', 'pk', 'description', 'addressee', 'blog')


class AdminTags(admin.ModelAdmin):
    model = Tag
    list_display = ('name',)


admin.site.register(Post, AdminPosts)
admin.site.register(Blog, AdminBlog)
admin.site.register(Commentary, AdminCommentary)
admin.site.register(Tag, AdminTags)
admin.site.register(Invite, AdminInvite)
