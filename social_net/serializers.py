from rest_framework import serializers
from .models import Blog, Post, Commentary


class CommentarySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Commentary
        fields = ['author', 'body', 'created_at']


class PostSerializer(serializers.HyperlinkedModelSerializer):
    # commentaries = CommentarySerializer(many=True)

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'body', 'is_published', 'created_at', 'likes', 'views']


class BlogSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # posts = PostSerializer(many=True)

    class Meta:
        model = Blog
        fields = ['id', 'title', 'description', 'created_at', 'updated_at', 'owner']

