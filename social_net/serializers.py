from rest_framework import serializers
from .models import Blog, Post, Commentary, UserProfile, Tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username',)


class BlogSerializer(serializers.ModelSerializer):
    owner = serializers.CharField()
    authors = UserSerializer(many=True)

    class Meta:
        model = Blog
        fields = ('title', 'slug', 'description', 'created_at', 'updated_at', 'owner', 'authors')


class CreateBlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = ('title', 'slug', 'description', 'authors')


class UpdateBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ('title', 'description', 'authors',)


class PostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer()
    author = serializers.CharField()
    tags = TagSerializer(many=True)
    liked_users = UserSerializer(many=True)

    class Meta:
        model = Post
        fields = ('title', 'author', 'body', 'is_published', 'created_at', 'likes', 'views', 'post_id', 'blog', 'tags', 'liked_users')


class CreatePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('title', 'author', 'body', 'is_published', 'tags')


class CreateCommentarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentary
        fields = ('body',)


class CommentarySerializer(serializers.ModelSerializer):
    author = serializers.CharField()

    class Meta:
        model = Commentary
        fields = ('author', 'body', 'created_at')


class SubscriptionList(serializers.ModelSerializer):
    subscriptions = BlogSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ('subscriptions',)
