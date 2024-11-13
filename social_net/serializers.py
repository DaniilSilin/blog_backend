from rest_framework import serializers
from .models import Blog, Post, Commentary, UserProfile, Tag, Invite


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username',)

class UserProfileSerializer(serializers.ModelSerializer):
    is_request_user = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

class BlogSerializer(serializers.ModelSerializer):
    owner = serializers.CharField()
    authors = UserSerializer(many=True)

    class Meta:
        model = Blog
        fields = ('id', 'title', 'slug', 'description', 'created_at', 'updated_at', 'count_of_posts', 'count_of_commentaries', 'owner', 'authors', 'avatar')


class CreateBlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = ('title', 'slug', 'description', 'avatar')


class UpdateBlogSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    authors = UserSerializer(many=True)

    class Meta:
        model = Blog
        fields = ('title', 'slug', 'description', 'owner', 'count_of_posts', 'count_of_commentaries', 'authors')
        read_only_fields = ('slug', 'created_at', 'updated_at', 'count_of_posts', 'owner', 'count_of_commentaries')


class PostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer()
    author = serializers.CharField()
    tags = TagSerializer(many=True)
    liked_users = UserSerializer(many=True)
    isLiked = serializers.BooleanField(read_only=True)


    class Meta:
        model = Post
        depth = 1
        fields = ('id', 'slug', 'post_id', 'isLiked', 'title', 'author', 'body', 'is_published', 'created_at', 'likes', 'views', 'post_id', 'blog', 'tags', 'liked_users')
        read_only_fields = ('slug', 'created_at', 'updated_at', 'count_of_posts', 'count_of_commentaries')


class PostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer()
    author = serializers.CharField()
    liked_users = UserSerializer(many=True)
    isLiked = serializers.BooleanField(read_only=True)

    class Meta:
        model = Post
        depth = 1
        fields = ('id', 'title', 'author', 'body', 'isLiked', 'is_published', 'created_at', 'likes', 'views', 'post_id', 'blog', 'tags', 'liked_users')
        read_only_fields = ('slug', 'created_at', 'updated_at', 'count_of_posts', 'count_of_commentaries')


class CreatePostSerializer(serializers.ModelSerializer):
    # tags = TagSerializer(read_only=True)
    class Meta:
        model = Post
        fields = ('title', 'body', 'is_published', 'tags', 'images')


class UpdatePostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer(read_only=True)
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = ('title', 'body', 'author', 'is_published', 'created_at', 'likes', 'views', 'post_id', 'blog', 'tags', 'liked_users')
        read_only_fields = ('created_at', 'author', 'likes', 'views', 'liked_users', 'blog', 'post_id')


class CreateCommentarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentary
        fields = ('body', 'author', 'created_at')
        read_only_fields = ('author', 'created_at')


class CommentarySerializer(serializers.ModelSerializer):
    author = serializers.CharField()

    class Meta:
        model = Commentary
        fields = ('author', 'body', 'created_at')

class PostCommentaryListSerializer(serializers.ModelSerializer):
    author = UserProfileSerializer()

    class Meta:
        model = Commentary
        fields = '__all__'


class SubscriptionList(serializers.ModelSerializer):
    subscriptions = BlogSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ('subscriptions',)


class InviteUserSerializer(serializers.ModelSerializer):
    addressee = serializers.CharField()
    blog = serializers.CharField()
    class Meta:
        model = Invite
        fields = ['admin', 'description', 'addressee', 'blog']

class InviteListUserSerializer(serializers.ModelSerializer):
    blog = BlogSerializer()
    admin = serializers.CharField()
    addressee = serializers.CharField()
    class Meta:
        model = Invite
        fields = ['pk', 'admin', 'description', 'status', 'created_at', 'addressee', 'blog']

class IsBlogOwnerSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source='slug')
    id = serializers.CharField(source='pk')

    class Meta:
        model = Blog
        fields = ('id', 'value')

class IsBlogAvailableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['slug',]


class InviteGetUsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'email', 'avatar')
