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
        fields = ('title', 'slug', 'description', 'created_at', 'updated_at', 'count_of_posts', 'count_of_commentaries', 'owner', 'authors')


class CreateBlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = ('title', 'slug', 'description', 'authors')


class UpdateBlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = ('title', 'slug', 'description', 'created_at', 'count_of_posts', 'count_of_commentaries', 'updated_at', 'authors')
        read_only_fields = ('slug', 'created_at', 'updated_at', 'count_of_posts', 'count_of_commentaries')


class PostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer()
    author = serializers.CharField()
    tags = TagSerializer(many=True)
    liked_users = UserSerializer(many=True)

    class Meta:
        model = Post
        depth = 1
        fields = ('title', 'author', 'body', 'is_published', 'created_at', 'likes', 'views', 'post_id', 'blog', 'tags', 'liked_users')
        read_only_fields = ('slug', 'created_at', 'updated_at', 'count_of_posts', 'count_of_commentaries')


class CreatePostSerializer(serializers.ModelSerializer):
    # tags = TagSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ('title', 'body', 'is_published', 'tags')


class UpdatePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('title', 'body', 'is_published', 'created_at', 'likes', 'views', 'tags', 'liked_users')
        read_only_fields = ('created_at', 'likes', 'views', 'liked_users')


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
