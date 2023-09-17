from django.urls import path
from .viewsets import LoginView, RegisterView, LogoutView

register = RegisterView.as_view({'post': 'create'})
login = LoginView.as_view({'post': 'retrieve'})
logout = LogoutView.as_view({'get': 'retrieve'})

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout')
]
