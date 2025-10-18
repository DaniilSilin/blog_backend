from django.urls import path
from .viewsets import (
    LoginView,
    RegisterView,
    LogoutView,
    UserDataView,
    IsUsernameAvailable,
    IsEmailAvailable,
    UserProfileView,
    SubscriptionListViewSet,
    ChangeAvatarView,
    DeleteAvatarView,
)

register = RegisterView.as_view({"post": "create"})
login = LoginView.as_view()
logout = LogoutView.as_view({"get": "retrieve"})

is_username_available = IsUsernameAvailable.as_view({"get": "is_username_available"})
is_email_available = IsEmailAvailable.as_view({"get": "is_email_available"})

user_data = UserDataView.as_view({"get": "retrieve"})

profile = UserProfileView.as_view(
    {"get": "retrieve", "put": "update", "delete": "destroy"}
)

user_subscriptions = SubscriptionListViewSet.as_view({"get": "list"})


change_avatar = ChangeAvatarView.as_view({"put": "update"})
delete_avatar = DeleteAvatarView.as_view({"delete": "destroy"})

urlpatterns = [
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path(
        "<str:username>/available/", is_username_available, name="is_username_available"
    ),
    path("<str:email>/available/", is_email_available, name="is_email_available"),
    path("user_data/", user_data, name="user_data"),
    path("profile/<slug:username>/", profile, name="profile"),
    path(
        "<slug:username>/subscriptions/", user_subscriptions, name="user_subscriptions"
    ),
    path("profile/<slug:username>/change/avatar/", change_avatar, name="change_avatar"),
    path("profile/<slug:username>/avatar/delete/", delete_avatar, name="delete_avatar"),
]
