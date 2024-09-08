from django.http import HttpResponseRedirect
from rest_framework.response import Response
from rest_framework import status, viewsets, permissions
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import redirect

from .models import UserProfile
from .serializers import LoginSerializer, RegisterSerializer, LogoutSerializer


from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication


class LoginView(APIView):
    authentication_classes = [TokenAuthentication]

    def post(self, request):
        print('awdawdawd')
        # Your authentication logic here
        user = authenticate(username=request.data['username'], password=request.data['password'])

        if user:
            print(Token)
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key})
        else:
            return Response({'error': 'Invalid credentials'}, status=401)


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

