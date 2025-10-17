from rest_framework import serializers
from social_net.serializers import BlogSerializer, UserSerializer

from .models import (
    UserProfile,
    Invite,
)


class InviteUserSerializer(serializers.ModelSerializer):
    addressee = serializers.CharField()
    blog = serializers.CharField()

    class Meta:
        model = Invite
        fields = ["admin", "description", "addressee", "blog"]


class InviteListUserSerializer(serializers.ModelSerializer):
    blog = BlogSerializer()
    admin = UserSerializer()
    addressee = UserSerializer()

    class Meta:
        model = Invite
        fields = [
            "pk",
            "admin",
            "description",
            "status",
            "created_at",
            "addressee",
            "blog",
        ]


class InviteGetUsersSerializer(serializers.ModelSerializer):
    value = serializers.CharField(source="username")

    class Meta:
        model = UserProfile
        fields = ("id", "value", "email", "avatar_small")
