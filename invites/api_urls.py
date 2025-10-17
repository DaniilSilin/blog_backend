from django.urls import path

from .viewsets import (
    InviteGetUsers,
    InvitationView,
    InviteListView,
    InvitationCreateView,
    BlogInvitationListView,
)

invite_create = InvitationCreateView.as_view({"post": "create"})
invite_list = InviteListView.as_view({"get": "list"})
invite_accept = InvitationView.as_view({"post": "accept_invite"})
invite_reject = InvitationView.as_view({"post": "reject_invite"})
invite_get_users = InviteGetUsers.as_view({"get": "list"})

blog_invitations = BlogInvitationListView.as_view({"get": "list"})

urlpatterns = [
    path("invite/create/", invite_create, name="invite_create"),
    path("invite/list/", invite_list, name="invite_list"),
    path("invite/<int:pk>/accept/", invite_accept, name="accept_invite"),
    path("invite/<int:pk>/reject/", invite_reject, name="reject_invite"),
    path(
        "invite/blog/<slug:slug>/get_users/", invite_get_users, name="invite_get_users"
    ),
    path("blog/<slug:slug>/invitations/", blog_invitations, name="blog_invitations"),
]
