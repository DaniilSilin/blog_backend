import os

from django.contrib.sites import requests
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets, permissions
from django.contrib.auth import logout, authenticate
from django.shortcuts import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser

import requests

import sys
import json

from .models import UserProfile
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    LogoutSerializer,
    UserSerializer,
    UpdateUserProfileSerializer,
    SubscriptionList,
    ChangeAvatarSerializer,
)


from dotenv import dotenv_values, load_dotenv

load_dotenv()
config = dotenv_values(".env")


from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication


class LoginView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):

        # Your authentication logic here
        user = authenticate(
            username=request.data["username"], password=request.data["password"]
        )

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key})
        else:
            return Response({"error": "Invalid credentials"}, status=401)


class RegisterView(viewsets.ModelViewSet):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        first_name = serializer.data["first_name"]
        last_name = serializer.data["last_name"]
        email = serializer.data["email"]
        username = serializer.data["username"]
        password = serializer.data["password"]
        token = serializer.data["token"]

        if self.check_captcha(token):
            user = UserProfile(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username,
                is_admin=False,
            )
            user.set_password(password)
            user.save()
            return Response({"status": "successful"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": "unsuccessful"}, status=status.HTTP_400_BAD_REQUEST
            )

    def check_captcha(self, token):
        SMARTCAPTCHA_SERVER_KEY = os.getenv("SMARTCAPTCHA_SERVER_KEY")
        resp = requests.post(
            "https://smartcaptcha.yandexcloud.net/validate",
            data={
                "secret": SMARTCAPTCHA_SERVER_KEY,
                "token": token,
            },
            timeout=1,
        )
        server_output = resp.content.decode()
        if resp.status_code != 200:
            print(
                f"Allow access due to an error: code={resp.status_code}; message={server_output}",
                file=sys.stderr,
            )
            return True
        return json.loads(server_output)["status"] == "ok"


class LogoutView(viewsets.ModelViewSet):
    serializer_class = LogoutSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_200_OK)


class UserDataView(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)


class IsUsernameAvailable(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [AllowAny]

    def is_username_available(self, request, username):
        username_exists = self.queryset.filter(username=username).exists()
        if username_exists:
            return Response({"available": False}, status=status.HTTP_200_OK)
        else:
            return Response({"available": True}, status=status.HTTP_200_OK)


class IsEmailAvailable(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [AllowAny]

    def is_email_available(self, request, email):
        email_exists = self.queryset.filter(email=email).exists()
        if email_exists:
            return Response(
                {"available": False, "message": "Email already exists."},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"available": True, "message": "Email is available."},
                status=status.HTTP_200_OK,
            )


class UserProfileView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UpdateUserProfileSerializer
        if self.request.method == "PUT":
            return UpdateUserProfileSerializer
        return UpdateUserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.queryset.get(username=self.kwargs["username"])
            user.subscriptionList = user.subscriptions.count()
            serial = UpdateUserProfileSerializer(user)
            return Response(serial.data)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=self.kwargs["username"])
        serializer = UpdateUserProfileSerializer(
            instance=user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "successful"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=self.kwargs["username"])
        user.delete()
        return Response({"status: successful"}, status=status.HTTP_200_OK)


class SubscriptionListViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = SubscriptionList
    # pagination_class = ListSetPagination
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=self.kwargs["username"])
        queryset = self.queryset.filter(username=user)
        if user:
            result = SubscriptionList(queryset, many=True)
            return Response(result.data, status=status.HTTP_200_OK)


class DeleteAvatarView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()

    # def destroy(self, request, *args, **kwargs):
    #     user = get_object_or_404(UserProfile, username=self.kwargs['username'])


class ChangeAvatarView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ChangeAvatarSerializer
    parser_class = (MultiPartParser, FormParser)

    def update(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=self.kwargs["username"])
        serializer = ChangeAvatarSerializer(
            instance=user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status": "success"}, status=status.HTTP_200_OK)
