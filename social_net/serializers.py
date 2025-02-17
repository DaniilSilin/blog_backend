from rest_framework import serializers
from .models import Blog, Post, Commentary, UserProfile, Tag, Invite

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'username', 'avatar', 'avatar_small')

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post  # Замените на вашу фактическую модель
        fields = '__all__'

class BlogMiniListSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    authors = UserSerializer(many=True)
    # subscribers = UserSerializer(many=True)
    subscriberList = serializers.IntegerField(read_only=True)
    isSubscribed = serializers.BooleanField(read_only=True)
    views = serializers.IntegerField(read_only=True)
    isBlogAuthor = serializers.BooleanField(read_only=True)
    # pinned_post = PostSerializer()

    class Meta:
        model = Blog
        fields = ('id', 'isSubscribed', 'owner', 'authors', 'title', 'subscriberList', 'slug', 'description', 'created_at', 'updated_at', 'count_of_posts', 'isSubscribed',
                  'count_of_commentaries', 'avatar', 'avatar_small', 'email', 'phone_number', 'site_link', 'vk_link', 'dzen_link', 'views', 'isBlogAuthor')


class BlogSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    authors = UserSerializer(many=True)
    # subscribers = UserSerializer(many=True)
    subscriberList = serializers.IntegerField(read_only=True)
    isSubscribed = serializers.BooleanField(read_only=True)
    views = serializers.IntegerField(read_only=True)
    # pinned_post = PostSerializer()

    class Meta:
        model = Blog
        fields = ('id', 'isSubscribed', 'owner', 'authors', 'title', 'subscriberList', 'slug', 'description', 'created_at', 'updated_at', 'count_of_posts', 'isSubscribed',
                  'count_of_commentaries', 'avatar', 'avatar_small', 'banner', 'banner_small', 'email', 'phone_number', 'site_link', 'vk_link', 'dzen_link', 'pinned_post', 'views')


class CreateBlogSerializer(serializers.ModelSerializer):
    avatar = serializers.ImageField(required=False)
    avatar_small = serializers.ImageField(required=False)

    class Meta:
        model = Blog
        fields = ('title', 'slug', 'description', 'avatar', 'avatar_small',)

class UpdateBlogSerializer(serializers.ModelSerializer):
    authors = UserSerializer(many=True)

    class Meta:
        model = Blog
        fields = ('title', 'slug', 'avatar', 'avatar_small', 'avatar', 'banner', 'banner_small', 'description', 'owner', 'count_of_posts', 'count_of_commentaries', 'authors')
        read_only_fields = ('slug', 'created_at', 'updated_at', 'count_of_posts', 'owner', 'count_of_commentaries')


class PostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer()
    author = UserSerializer()
    isLiked = serializers.BooleanField(read_only=True)
    likedUsersCount = serializers.IntegerField(read_only=True)
    commentCount = serializers.IntegerField(read_only=True)
    subscribers = serializers.IntegerField(read_only=True)
    isSubscribed = serializers.BooleanField(read_only=True)
    isBookmarked = serializers.BooleanField(read_only=True)
    comments = serializers.IntegerField(read_only=True)
    liked_users = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'author', 'body', 'is_published', 'created_at', 'likes', 'dislikes', 'views', 'post_id', 'blog',
                  'tags', 'liked_users', 'disliked_users', 'pinned_comment', 'isLiked', 'likedUsersCount', 'commentCount', 'subscribers',
                  'isSubscribed', 'isBookmarked', 'comments', 'map')
        read_only_fields = ('slug', 'created_at', 'updated_at', 'count_of_posts', 'count_of_commentaries')

    def get_liked_users(self, obj):
        users = obj.liked_users.all()[:2]
        return UserSerializer(users, many=True).data


class CreatePostSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ('title', 'body', 'map', 'is_published', 'tags')


class UpdatePostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer(read_only=True)
    author = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Post
        fields = ('title', 'body', 'author', 'is_published', 'created_at', 'likes', 'views', 'post_id', 'blog', 'tags', 'liked_users')
        read_only_fields = ('created_at', 'author', 'likes', 'views', 'liked_users', 'blog', 'post_id')


class CreateCommentarySerializer(serializers.ModelSerializer):
    reply_to = serializers.IntegerField(required=False, default=None)

    class Meta:
        model = Commentary
        fields = ('body', 'author', 'created_at', 'reply_to', 'comment_id')
        read_only_fields = ('author', 'created_at')


class BlogCommentListSerializer(serializers.ModelSerializer):
    post = PostSerializer()
    author = UserSerializer()

    class Meta:
        model = Commentary
        fields = ('comment_id', 'body', 'author', 'created_at', 'likes', 'dislikes', 'is_edited', 'reply_to', 'post')


class PostCommentaryListSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    count_of_replies = serializers.SerializerMethodField()
    isLiked= serializers.BooleanField()
    isDisliked = serializers.BooleanField()
    # reply_to = serializers.SerializerMethodField()

    class Meta:
        model = Commentary
        fields = ('comment_id', 'body', 'author', 'created_at', 'likes', 'dislikes', 'is_edited', 'reply_to', 'count_of_replies', 'liked_by_author', 'isLiked', 'isDisliked')

    def get_count_of_replies(self, obj):
        replies = obj.replies.count()
        return replies


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
    value = serializers.CharField(source='username')


    class Meta:
        model = UserProfile
        fields = ('id', 'value', 'email', 'avatar_small')


class BookmarkListSerializer(serializers.ModelSerializer):
    subscriptions = BlogSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ('subscriptions',)


class BookmarkSerializer(serializers.ModelSerializer):
    subscriptions = BlogSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ('subscriptions',)


class ChangeAvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ('avatar', 'avatar_small', 'username',)


class UserProfileSerializer(serializers.ModelSerializer):
    is_request_user = serializers.BooleanField(read_only=True)
    subscriptions = BlogSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = '__all__'

class SubscriptionListMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ['id', 'title', 'avatar_small', 'slug']