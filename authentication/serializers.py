from rest_framework import serializers
from rest_framework.serializers import CharField, ModelSerializer
from django.core.validators import RegexValidator
from .validators import validate_first_name, validate_last_name
from .models import UserProfile
from social_net.models import Blog
from social_net.serializers import BlogSerializer


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = ("avatar_small", "title")


class RegisterSerializer(serializers.ModelSerializer):
    first_name = CharField(
        required=False, min_length=2, max_length=50, validators=[validate_first_name]
    )

    last_name = CharField(
        required=False, min_length=2, max_length=50, validators=[validate_last_name]
    )

    email = CharField(
        required=True,
    )

    username = CharField(
        required=True,
        min_length=3,
        max_length=150,
    )

    password = CharField(
        required=True,
        min_length=6,
        max_length=50,
    )

    token = CharField(
        required=True,
    )

    class Meta:
        model = UserProfile
        fields = ("first_name", "last_name", "email", "username", "password", "token")


class LoginSerializer(serializers.ModelSerializer):
    username = CharField(label="Username", write_only=True)

    password = CharField(
        label="Password", style={"input_type": "password"}, write_only=True
    )

    class Meta:
        model = UserProfile
        fields = ("username", "password")


class LogoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ("username", "password")


class UserSerializer(serializers.ModelSerializer):
    subscriptions = SubscriptionSerializer(many=True)

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
            "subscriptions",
        )


class UpdateUserProfileSerializer(serializers.ModelSerializer):
    avatar_small = serializers.ImageField(allow_null=True)
    banner_small = serializers.ImageField(allow_null=True)
    avatar = serializers.ImageField(allow_null=True)
    banner = serializers.ImageField(allow_null=True)
    subscriptionList = serializers.IntegerField()
    subscriptions = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = (
            "avatar",
            "avatar_small",
            "banner",
            "banner_small",
            "first_name",
            "last_name",
            "date_of_birth",
            "description",
            "email",
            "gender",
            "is_profile_private",
            "username",
            "last_activity",
            "subscriptionList",
            "subscriptions",
        )

    def get_subscriptions(self, obj):
        subscriptions = obj.subscriptions.all()[:5]
        return BlogSerializer(subscriptions, many=True).data


class SubscriptionList(serializers.ModelSerializer):
    subscriptions = BlogSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = ("subscriptions",)


class ChangeAvatarSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = (
            "avatar",
            "avatar_small",
            "username",
        )
