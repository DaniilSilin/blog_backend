from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, viewsets
from django.shortcuts import get_object_or_404

from authentication.models import UserProfile
from .models import Blog, Invite
from .serializers import (
    InviteUserSerializer,
    InviteListUserSerializer,
    InviteGetUsersSerializer,
)


class ListSetPagination(PageNumberPagination):
    page_size = 5


class InvitationCreateView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = InviteUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = get_object_or_404(UserProfile, pk=serializer.data["admin"])
        description = serializer.data["description"]
        addressee = get_object_or_404(
            UserProfile, username=serializer.data["addressee"]
        )
        blog = get_object_or_404(Blog, slug=serializer.data["blog"])

        invite = Invite(
            admin=admin, description=description, addressee=addressee, blog=blog
        )

        invite.save()
        serial = InviteUserSerializer(invite, many=False)
        return Response(serial.data, status=status.HTTP_200_OK)


class InviteListView(viewsets.ModelViewSet):
    queryset = Invite.objects.all()
    serializer_class = InviteListUserSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(addressee=request.user).order_by("status")
        paginated_result = self.paginate_queryset(queryset)
        if paginated_result is not None:
            serializer = self.serializer_class(paginated_result, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response({"status": "unsuccessful"}, status=status.HTTP_200_OK)


class InvitationView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def accept_invite(self, request, pk):
        invite = get_object_or_404(Invite, pk=pk)
        if invite.addressee == request.user and invite.status is None:
            invite.blog.authors.add(invite.addressee)
            invite.status = True
            invite.save()
            return Response({"status": "successful"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": "unsuccessful"}, status=status.HTTP_403_FORBIDDEN
            )

    def reject_invite(self, request, pk):
        invite = get_object_or_404(Invite, pk=pk)
        if invite.addressee == request.user and invite.status is None:
            invite.status = False
            invite.save()
            return Response({"status": "successful"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": "unsuccessful"}, status=status.HTTP_403_FORBIDDEN
            )


class InviteGetUsers(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = InviteGetUsersSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset

        query = self.request.query_params.get("query", None)

        blog = get_object_or_404(Blog, slug=self.kwargs["slug"])
        pending_invites = Invite.objects.filter(blog=blog, status=None).values_list(
            "addressee__username", flat=True
        )
        current_blog_authors = blog.authors.values_list("username", flat=True)
        blog_owner_username = UserProfile.objects.filter(
            username=blog.owner.username
        ).values_list("username", flat=True)

        excluded_usernames = (
            set(pending_invites) | set(current_blog_authors) | set(blog_owner_username)
        )
        print(excluded_usernames)

        queryset = queryset.exclude(username__in=excluded_usernames)
        if query:
            user_list = queryset.filter(username__icontains=query)[:5]
            if user_list:
                serializer = self.serializer_class(user_list, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"status": "unsuccessful"}, status=status.HTTP_404_NOT_FOUND
                )
        else:
            user_list = queryset.order_by("?")[:5]
            if user_list:
                serializer = self.serializer_class(user_list, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"status": "unsuccessful"}, status=status.HTTP_404_NOT_FOUND
                )


class BlogInvitationListView(viewsets.ModelViewSet):
    serializer_class = InviteListUserSerializer
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs["slug"])
        blog_invitations = blog.invites.all()
        paginated_result = self.paginate_queryset(blog_invitations)
        if paginated_result is not None:
            serializer = self.serializer_class(paginated_result, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status": "unsuccessful"}, status=status.HTTP_404_NOT_FOUND
            )
