from django.urls import path
from .viewsets import LoginView, RegisterView, LogoutView, UserDataView

register = RegisterView.as_view({'post': 'create'})
login = LoginView.as_view()
logout = LogoutView.as_view({'get': 'retrieve'})

user_data = UserDataView.as_view({'get': 'retrieve'})

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),

    path('user_data/', user_data, name='user_data')
]
