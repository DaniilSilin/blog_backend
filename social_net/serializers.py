from rest_framework import serializers
from .models import Blog


class AllBlogsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'authors')


class CreateBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'authors')


class DeleteBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ('id', 'title', 'description', 'created_at', 'updated_at', 'owner', 'authors')
