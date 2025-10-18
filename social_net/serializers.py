from rest_framework import serializers
from rest_framework.serializers import (
    CharField,
    URLField,
    ImageField,
    SlugField,
    BooleanField,
    ListField,
)

from .models import (
    Blog,
    Post,
    UserProfile,
    Tag,
    PostImage,
)
from comments.models import Commentary

from .validators import validate_avatar_small, validate_avatar


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("name",)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("id", "username", "avatar", "avatar_small")


class BlogMiniListSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    authors = UserSerializer(many=True)
    subscriberList = serializers.IntegerField(read_only=True)
    isSubscribed = serializers.BooleanField(read_only=True)
    views = serializers.IntegerField(read_only=True)
    isBlogAuthor = serializers.BooleanField(read_only=True)

    class Meta:
        model = Blog
        fields = (
            "id",
            "isSubscribed",
            "owner",
            "authors",
            "title",
            "subscriberList",
            "slug",
            "description",
            "created_at",
            "updated_at",
            "count_of_posts",
            "isSubscribed",
            "count_of_commentaries",
            "avatar",
            "avatar_small",
            "email",
            "phone_number",
            "site_link",
            "vk_link",
            "dzen_link",
            "views",
            "isBlogAuthor",
        )


class BlogSerializerPinned(serializers.ModelSerializer):
    owner = UserSerializer()
    authors = UserSerializer(many=True)
    subscriberList = serializers.IntegerField(read_only=True)
    isSubscribed = serializers.BooleanField(read_only=True)
    views = serializers.IntegerField(read_only=True)

    class Meta:
        model = Blog
        fields = (
            "id",
            "isSubscribed",
            "owner",
            "authors",
            "title",
            "subscriberList",
            "slug",
            "description",
            "created_at",
            "updated_at",
            "count_of_posts",
            "isSubscribed",
            "count_of_commentaries",
            "avatar",
            "avatar_small",
            "banner",
            "banner_small",
            "email",
            "phone_number",
            "site_link",
            "vk_link",
            "dzen_link",
            "pinned_post",
            "views",
        )


class BlogPinnedPostSerializer(serializers.ModelSerializer):
    blog = BlogSerializerPinned()
    author = UserSerializer()
    # isLiked = serializers.BooleanField(read_only=True)
    likedUsersCount = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    subscribers = serializers.IntegerField(read_only=True)
    isSubscribed = serializers.BooleanField(read_only=True)
    isBookmarked = serializers.BooleanField(read_only=True)
    comments = serializers.IntegerField(read_only=True)
    liked_users = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "body",
            "is_published",
            "created_at",
            "likes",
            "dislikes",
            "views",
            "post_id",
            "blog",
            "tags",
            "liked_users",
            "disliked_users",
            "likedUsersCount",
            "comment_count",
            "subscribers",
            "isSubscribed",
            "isBookmarked",
            "comments",
            "map",
        )
        read_only_fields = (
            "slug",
            "created_at",
            "updated_at",
            "count_of_posts",
            "count_of_commentaries",
        )

    def get_liked_users(self, obj):
        users = obj.liked_users.all()[:5]
        return UserSerializer(users, many=True).data


class BlogSerializer(serializers.ModelSerializer):
    owner = UserSerializer()
    authors = UserSerializer(many=True)
    subscriberList = serializers.IntegerField(read_only=True)
    isSubscribed = serializers.BooleanField(read_only=True)
    views = serializers.IntegerField(read_only=True)

    class Meta:
        model = Blog
        fields = (
            "id",
            "isSubscribed",
            "owner",
            "authors",
            "title",
            "subscriberList",
            "slug",
            "description",
            "created_at",
            "updated_at",
            "count_of_posts",
            "isSubscribed",
            "count_of_commentaries",
            "avatar",
            "avatar_small",
            "banner",
            "banner_small",
            "email",
            "phone_number",
            "site_link",
            "youtube_link",
            "vk_link",
            "telegram_link",
            "dzen_link",
            "views",
            "map",
        )


class CreateBlogSerializer(serializers.ModelSerializer):
    avatar = ImageField(required=False, validators=[validate_avatar])
    avatar_small = ImageField(required=False, validators=[validate_avatar_small])
    title = CharField(required=True, max_length=50)
    slug = SlugField(
        required=True,
        max_length=25,
    )
    description = CharField(required=False, max_length=300)

    class Meta:
        model = Blog
        fields = ("avatar", "avatar_small", "title", "slug", "description")


class UpdateBlogSerializer(serializers.ModelSerializer):
    avatar_small = ImageField(allow_null=True, validators=[validate_avatar_small])
    banner_small = ImageField(allow_null=True)
    avatar = ImageField(allow_null=True, validators=[validate_avatar])
    banner = ImageField(allow_null=True)
    title = CharField(required=True, max_length=50)
    description = CharField(required=False, max_length=300)
    phone_number = CharField(required=False, max_length=15)
    email = CharField(required=False)
    map = CharField(required=False)
    vk_link = URLField(required=False, min_length=21, max_length=48)
    telegram_link = URLField(required=False, min_length=19, max_length=46)
    youtube_link = URLField(required=False)
    dzen_link = URLField(required=False)
    site_link = URLField(required=False)

    class Meta:
        model = Blog
        fields = (
            "banner",
            "banner_small",
            "avatar",
            "avatar_small",
            "title",
            "slug",
            "description",
            "phone_number",
            "email",
            "map",
            "vk_link",
            "telegram_link",
            "youtube_link",
            "dzen_link",
            "site_link",
        )
        read_only_fields = (
            "slug",
            "created_at",
            "updated_at",
            "count_of_posts",
            "owner",
            "count_of_commentaries",
        )


class PostImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostImage
        fields = ("id", "image")  # Adjust fields as necessary


class PostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer()
    author = UserSerializer()
    isLiked = serializers.BooleanField(read_only=True)
    isDisliked = serializers.BooleanField(read_only=True)
    isSubscribed = serializers.BooleanField(read_only=True)
    isBookmarked = serializers.BooleanField(read_only=True)

    likedUsersCount = serializers.IntegerField(read_only=True)
    comment_count = serializers.IntegerField(read_only=True)
    subscribers = serializers.IntegerField(read_only=True)
    comments = serializers.IntegerField(read_only=True)
    liked_users = serializers.SerializerMethodField()
    images1 = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "id",
            "title",
            "author",
            "body",
            "is_published",
            "images1",
            "created_at",
            "likes",
            "dislikes",
            "views",
            "post_id",
            "blog",
            "tags",
            "liked_users",
            "disliked_users",
            "isLiked",
            "isDisliked",
            "likedUsersCount",
            "comment_count",
            "subscribers",
            "isSubscribed",
            "isBookmarked",
            "comments",
            "map",
            "author_is_hidden",
            "comments_allowed",
        )
        read_only_fields = (
            "slug",
            "created_at",
            "updated_at",
            "count_of_posts",
            "count_of_commentaries",
            "map",
        )

    def get_liked_users(self, obj):
        users = obj.liked_users.all()[:5]
        return UserSerializer(users, many=True).data

    def get_images1(self, obj):
        images = obj.images.all()
        return PostImageSerializer(images, many=True).data


class CreatePostSerializer(serializers.ModelSerializer):
    title = CharField(required=True, max_length=100)
    body = CharField(required=True)
    map_type = CharField(required=True)
    map = CharField(required=False)
    is_published = BooleanField(default=False)
    author_is_hidden = BooleanField(default=False)
    comments_allowed = BooleanField(default=True)
    images = ListField(child=ImageField())

    class Meta:
        model = Post
        fields = (
            "title",
            "body",
            "images",
            "map_type",
            "map",
            "tags",
            "is_published",
            "author_is_hidden",
            "comments_allowed",
        )


class UpdatePostSerializer(serializers.ModelSerializer):
    blog = BlogSerializer(read_only=True)
    author = serializers.CharField(source="author.username", read_only=True)

    class Meta:
        model = Post
        fields = (
            "title",
            "body",
            "author",
            "is_published",
            "created_at",
            "likes",
            "views",
            "post_id",
            "blog",
            "tags",
            "liked_users",
            "comments_allowed",
            "author_is_hidden",
        )
        read_only_fields = (
            "created_at",
            "author",
            "likes",
            "views",
            "liked_users",
            "blog",
            "post_id",
        )


# class UpdateCommentarySerializer(serializers.ModelSerializer):
#     reply_to = serializers.IntegerField(required=False, default=None)
#     body = CharField(required=True)
#
#     class Meta:
#         model = Commentary
#         fields = ('body', 'author', 'created_at', 'reply_to', 'comment_id')
#         read_only_fields = ('author', 'created_at')


class BlogCommentListSerializer(serializers.ModelSerializer):
    post = PostSerializer()
    author = UserSerializer()
    replies_count = serializers.SerializerMethodField()
    isLiked = serializers.BooleanField()
    isDisliked = serializers.BooleanField()

    class Meta:
        model = Commentary
        fields = (
            "comment_id",
            "body",
            "author",
            "created_at",
            "likes",
            "dislikes",
            "is_edited",
            "reply_to",
            "post",
            "isLiked",
            "isDisliked",
            "replies_count",
            "liked_by_author",
        )

    def get_replies_count(self, obj):
        replies = obj.replies.count()
        return replies


class IsBlogOwnerSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source="slug")
    id = serializers.CharField(source="pk")

    class Meta:
        model = Blog
        fields = ("id", "value")


class IsBlogAvailableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            "slug",
        ]


class BookmarkListSerializer(serializers.ModelSerializer):
    subscriptions = BlogSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ("subscriptions",)


class BookmarkSerializer(serializers.ModelSerializer):
    subscriptions = BlogSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ("subscriptions",)


class UserProfileSerializer(serializers.ModelSerializer):
    subscriptions = BlogSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = (
            "id",
            "last_login",
            "is_superuser",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "date_joined",
            "is_admin",
            "gender",
            "description",
            "date_of_birth",
            "is_profile_private",
            "last_activity",
            "avatar",
            "avatar_small",
            "banner",
            "banner_small",
        )


class SubscriptionListMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ["id", "title", "avatar_small", "slug"]


class BlogCommentListDeleteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Commentary
        fields = [""]


class PostIdSerializer(serializers.Serializer):
    post_id = serializers.IntegerField()


class BlogDeletePostListSerializer(serializers.Serializer):
    selectedPosts = serializers.ListField(child=PostIdSerializer(), allow_empty=False)

    class Meta:
        model = Post
        fields = ["selectedPosts"]


class InviteGetUsersSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source="username")

    class Meta:
        model = UserProfile
        fields = ("id", "value", "email", "avatar_small")
