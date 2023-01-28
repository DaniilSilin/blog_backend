from rest_framework import serializers
from .models import Post


class PostsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'body', 'is_published', 'created_at', 'likes', 'views', 'tags']
