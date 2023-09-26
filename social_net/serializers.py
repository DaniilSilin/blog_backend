from rest_framework import serializers
from .models import Blog, Post


class BlogListSerializer(serializers.ModelSerializer):
    owner = serializers.CharField()

    class Meta:
        model = Blog
        fields = ('pk', 'title', 'slug', 'description', 'created_at', 'updated_at', 'owner', 'authors')


class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ('title', 'description', 'created_at', 'updated_at', 'owner', 'authors')


class PostListSerializer(serializers.ModelSerializer):
    author = serializers.CharField()

    class Meta:
        model = Post
        fields = ('title', 'author', 'body', 'is_published', 'likes', 'views', 'blog')


class CreatePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('title', 'author', 'body', 'is_published', 'likes', 'views', 'blog')
