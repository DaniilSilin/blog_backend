from rest_framework import serializers
from .models import Blog


class AllBlogsSerializer(serializers.ModelSerializer):
    owner = serializers.CharField()

    class Meta:
        model = Blog
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'authors')


class CreateBlogSerializer(serializers.ModelSerializer):
    owner = serializers.CharField()

    class Meta:
        model = Blog
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'authors')

