from django.urls import path
from .viewsets import LoginView, RegisterView, LogoutView, UserDataView, IsUsernameAvailable

register = RegisterView.as_view({'post': 'create'})
login = LoginView.as_view()
logout = LogoutView.as_view({'get': 'retrieve'})

is_username_available = IsUsernameAvailable.as_view({'get': 'is_username_available'})

user_data = UserDataView.as_view({'get': 'retrieve'})

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

    path('<str:username>/available/', is_username_available, name='is_username_available'),

    path('user_data/', user_data, name='user_data')
]
