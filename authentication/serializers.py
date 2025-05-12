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
        fields = ('avatar_small', 'title')


class RegisterSerializer(serializers.ModelSerializer):
    first_name = CharField(
        required=False,
        min_length=2,
        max_length=50,
        validators=[validate_first_name]
    )

    last_name = CharField(
        required=False,
        min_length=2,
        max_length=50,
        validators=[validate_last_name]
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

    class Meta:
        model = UserProfile
        fields = ('first_name', 'last_name', 'email', 'username', 'password')


class LoginSerializer(serializers.ModelSerializer):
    username = CharField(
        label="Username",
        write_only=True
    )

    password = CharField(
        label="Password",
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = UserProfile
        fields = ('username', 'password')


class LogoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'password')

class UserSerializer(serializers.ModelSerializer):
    subscriptions = SubscriptionSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = '__all__'
