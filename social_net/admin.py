from django.contrib import admin
from .models import (
    Blog,
    Post,
    UserProfile,
    Tag,
    PostImage,
)


class AdminPosts(admin.ModelAdmin):
    model = Post
    list_display = (
        "author",
        "title",
        "body",
        "is_published",
        "created_at",
        "likes",
        "views",
        "post_id",
    )


class AdminBlog(admin.ModelAdmin):
    model = Blog
    list_display = ("title", "slug", "description", "created_at", "updated_at")


class AdminTags(admin.ModelAdmin):
    model = Tag
    list_display = ("name",)


class AdminPostImages(admin.ModelAdmin):
    model = PostImage
    list_display = ("id", "image")


admin.site.register(Post, AdminPosts)
admin.site.register(Blog, AdminBlog)
admin.site.register(Tag, AdminTags)
admin.site.register(PostImage, AdminPostImages)
