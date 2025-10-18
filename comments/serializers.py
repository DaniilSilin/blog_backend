from models import Commentary
from rest_framework import serializers
from rest_framework.serializers import (
    CharField,
    BooleanField,
    IntegerField,
    SerializerMethodField,
)

from social_net.serializers import UserSerializer


class CreateCommentarySerializer(serializers.ModelSerializer):
    reply_to = IntegerField(required=False, default=None)
    body = CharField(required=True)

    class Meta:
        model = Commentary
        fields = ("body", "author", "created_at", "reply_to", "comment_id")
        read_only_fields = ("author", "created_at")


class PostCommentaryListSerializer(serializers.ModelSerializer):
    reply_to = SerializerMethodField()
    replies_count = SerializerMethodField()
    author = UserSerializer()
    isLiked = BooleanField()
    isDisliked = BooleanField()
    pinned_by_user = UserSerializer()

    class Meta:
        model = Commentary
        fields = (
            "id",
            "comment_id",
            "body",
            "author",
            "created_at",
            "likes",
            "dislikes",
            "is_edited",
            "reply_to",
            "replies_count",
            "liked_by_author",
            "isLiked",
            "isDisliked",
            "is_pinned",
            "pinned_by_user",
        )

    def get_replies_count(self, obj):
        replies = obj.replies.count()
        return replies

    def get_reply_to(self, obj):
        if obj.reply_to is not None:
            return obj.reply_to.comment_id


class UpdateCommentarySerializer(serializers.ModelSerializer):
    author = UserSerializer()
    replies_count = SerializerMethodField()
    isLiked = BooleanField()
    isDisliked = BooleanField()
    reply_to = SerializerMethodField()
    pinned_by_user = UserSerializer()

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
            "replies_count",
            "liked_by_author",
            "isLiked",
            "isDisliked",
            "is_pinned",
            "pinned_by_user",
        )

    def get_replies_count(self, obj):
        replies = obj.replies.count()
        return replies

    def get_reply_to(self, obj):
        if obj.reply_to is not None:
            return obj.reply_to.comment_id


class PostCommentarySerializer(serializers.ModelSerializer):
    author = UserSerializer()
    replies_count = SerializerMethodField()
    isLiked = BooleanField(default=False)
    isDisliked = BooleanField(default=False)
    reply_to = SerializerMethodField()

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
            "replies_count",
            "liked_by_author",
            "isLiked",
            "isDisliked",
        )

    def get_replies_count(self, obj):
        replies = obj.replies.count()
        return replies

    def get_reply_to(self, obj):
        if obj.reply_to is not None:
            return obj.reply_to.comment_id
