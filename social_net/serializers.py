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

class UserProfileSerializer(serializers.ModelSerializer):
    is_request_user = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserProfile
        fields = '__all__'


class BlogSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    authors = UserSerializer(many=True)
    # subscribers = UserSerializer(many=True)
    subscriberList = serializers.IntegerField(read_only=True)
    isSubscribed = serializers.BooleanField(read_only=True)
    isInBookmark = serializers.BooleanField(read_only=True)
    views = serializers.IntegerField(read_only=True)

    class Meta:
        model = Blog
        fields = ('id', 'isSubscribed', 'authors', 'title', 'subscriberList', 'slug', 'description', 'created_at', 'updated_at', 'count_of_posts', 'isInBookmark', 'isSubscribed',
                  'count_of_commentaries', 'owner', 'avatar', 'avatar_small', 'email', 'phone_number', 'site_link', 'vk_link', 'dzen_link', 'pinned_post', 'views', 'banner')


class CreateBlogSerializer(serializers.ModelSerializer):

    class Meta:
        model = Blog
        fields = ('title', 'slug', 'description', 'avatar', 'avatar_small',)


class UpdateBlogSerializer(serializers.ModelSerializer):
    owner = serializers.CharField(source='owner.username', read_only=True)
    authors = UserSerializer(many=True)

    class Meta:
        model = Blog
        fields = ('title', 'slug', 'avatar', 'avatar_small', 'description', 'owner', 'count_of_posts', 'count_of_commentaries', 'authors')
        read_only_fields = ('slug', 'created_at', 'updated_at', 'count_of_posts', 'owner', 'count_of_commentaries')


# class PostSerializer(serializers.ModelSerializer):
#     blog = BlogSerializer()
#     author = serializers.CharField()
#     tags = TagSerializer(many=True)
#     liked_users = UserSerializer(many=True)
#     isLiked = serializers.BooleanField(read_only=True)
#
#
#     class Meta:
#         model = Post
#         depth = 1
#         fields = ('id', 'slug', 'post_id', 'isLiked', 'title', 'author', 'body', 'is_published', 'created_at', 'likes', 'views', 'post_id', 'blog', 'tags', 'liked_users')
#         read_only_fields = ('slug', 'created_at', 'updated_at', 'count_of_posts', 'count_of_commentaries')

class PostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer()
    author = UserSerializer()
    isLiked = serializers.BooleanField(read_only=True)
    likedUsersCount = serializers.IntegerField(read_only=True)
    commentCount = serializers.IntegerField(read_only=True)
    subscribers = serializers.IntegerField(read_only=True)
    isSubscribed = serializers.BooleanField(read_only=True)
    isInBookmark = serializers.BooleanField(read_only=True)
    comments = serializers.IntegerField(read_only=True)
    liked_users = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ('id', 'title', 'author', 'body', 'is_published', 'created_at', 'likes', 'views', 'post_id', 'blog',
                  'tags', 'liked_users', 'pinned_comment', 'isLiked', 'likedUsersCount', 'commentCount', 'subscribers',
                  'isSubscribed', 'isInBookmark', 'comments')
        read_only_fields = ('slug', 'created_at', 'updated_at', 'count_of_posts', 'count_of_commentaries')

    def get_liked_users(self, obj):
        users = obj.liked_users.all()[:2]
        return UserSerializer(users, many=True).data


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
    reply_to = serializers.IntegerField(required=False, default=None)

    class Meta:
        model = Commentary
        fields = ('body', 'author', 'created_at', 'reply_to', 'comment_id')
        read_only_fields = ('author', 'created_at')


class PostCommentaryListSerializer(serializers.ModelSerializer):
    author = UserSerializer()
    count_of_replies = serializers.SerializerMethodField()
    # reply_to = serializers.SerializerMethodField()
    isLikedByPostAuthor = serializers.BooleanField()
    has_author_reply = serializers.BooleanField()

    class Meta:
        model = Commentary
        fields = ('comment_id', 'body', 'author', 'created_at', 'likes', 'dislikes', 'is_edited', 'reply_to', 'count_of_replies',
                  'isLikedByPostAuthor',
                  'has_author_reply'
        )

    def get_count_of_replies(self, obj):
        replies = obj.replies.count()
        return replies

    # def get_reply_to(self, obj):
    #     return obj.reply_to


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
