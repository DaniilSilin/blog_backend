from rest_framework import serializers
from .models import UserProfile
from social_net.models import Blog


class LoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        label="Username",
        write_only=True
    )

    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
        write_only=True
    )

    class Meta:
        model = UserProfile
        fields = ('username', 'password')


class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        label="Username",
    )

    password = serializers.CharField(
        label="Password",
        style={'input_type': 'password'},
    )

    class Meta:
        model = UserProfile
        fields = ('email', 'username', 'password')


class LogoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('username', 'password')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
