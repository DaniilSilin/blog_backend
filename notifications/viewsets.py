from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404
from rest_framework.pagination import PageNumberPagination

from .models import Notification
from .serializers import (
    UserNotificationsSerializer,
)


class ListSetPagination(PageNumberPagination):
    page_size = 5


class UserNotificationListView(viewsets.ModelViewSet):
    queryset = Notification.objects.filter(is_hidden=False)
    permission_classes = [IsAuthenticated]
    serializer_class = UserNotificationsSerializer
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(addressee=request.user)

        paginate_queryset = self.paginate_queryset(queryset)
        if paginate_queryset:
            serializer = self.serializer_class(paginate_queryset, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(data=result.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": "unsuccessful"}, status=status.HTTP_404_NOT_FOUND
            )


class SetNotificationIsRead(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def read_notification(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=("is_read",))
            return Response({"status": "successful"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": "unsuccessful"}, status=status.HTTP_404_NOT_FOUND
            )


class HideNotificationView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def hide_notification(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        if not notification.is_hidden:
            notification.is_hidden = True
            notification.save(update_fields=("is_hidden",))
            return Response({"status": "successful"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": "unsuccessful"}, status=status.HTTP_404_NOT_FOUND
            )
