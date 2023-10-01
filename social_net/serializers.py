from rest_framework import serializers
from .models import Blog, Post, Commentary, UserProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username',)


class BlogSerializer(serializers.ModelSerializer):
    owner = serializers.CharField()
    authors = UserSerializer(many=True)

    class Meta:
        model = Blog
        fields = ('pk', 'title', 'slug', 'description', 'created_at', 'updated_at', 'owner', 'authors')


class CreateBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ('title', 'slug', 'description', 'authors')


class PostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer()
    author = serializers.CharField()

    class Meta:
        model = Post
        fields = ('title', 'author', 'body', 'is_published', 'likes', 'views', 'blog')


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'author', 'body', 'is_published', 'blog')


class CreateCommentarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentary
        fields = ('author', 'body', 'post')
