from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect

from .models import UserProfile
from .serializers import LoginSerializer, RegisterSerializer, LogoutSerializer


class LoginView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = LoginSerializer
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response('Success', status=status.HTTP_200_OK)
        else:
            return Response('UnSuccess', status=status.HTTP_400_BAD_REQUEST)


class RegisterView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        username = serializer.data['username']
        password = serializer.data['password']

        user = UserProfile(
            email=email,
            username=username,
            is_admin=False
        )
        user.set_password(password)
        user.save()

        return redirect('/login/')


class LogoutView(viewsets.ModelViewSet):
    serializer_class = LogoutSerializer
    permission_classes = (permissions.AllowAny,)

    def retrieve(self, request, *args, **kwargs):
        logout(request)
        return HttpResponseRedirect('/login/')

