from django.urls import path
from .viewsets import (
    UserNotificationListView,
    SetNotificationIsRead,
    HideNotificationView,
)

notification_list = UserNotificationListView.as_view({"get": "list"})
read_notification = SetNotificationIsRead.as_view({"post": "read_notification"})
hide_notification = HideNotificationView.as_view({"post": "hide_notification"})

urlpatterns = [
    path(
        "profile/<slug:username>/notification/list/",
        notification_list,
        name="notification_list",
    ),
    path(
        "notification/<int:pk>/is_read/", read_notification, name="notification_is_read"
    ),
    path("notification/<int:pk>/hide/", hide_notification, name="hide_notification"),
]
