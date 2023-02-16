from rest_framework import serializers
from .models import Blog, Post, Commentary


class CommentarySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Commentary
        fields = ['author', 'body', 'created_at']


class PostSerializer(serializers.ModelSerializer):
    # commentaries = CommentarySerializer(many=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'blog', 'title', 'body', 'is_published', 'created_at', 'likes', 'views', 'tags']


class BlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'authors')


class AllPostsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('id', 'title', 'body', 'is_published', 'created_at', 'likes', 'views', 'tags')


class AllBlogsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'authors')
