from django.urls import path

from .consumers import UserConsumer

ws_urlpatterns = [
    path('ws/some-url/', UserConsumer.as_asgi())
]
