from rest_framework import serializers
from social_net.serializers import UserSerializer, PostSerializer
from .models import Notification


class UserNotificationsSerializer(serializers.ModelSerializer):
    addressee = UserSerializer()
    author = UserSerializer()
    post = PostSerializer()

    class Meta:
        model = Notification
        fields = ["id", "addressee", "text", "author", "created_at", "is_read", "post"]
