from serializers import CreateCommentarySerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, permissions, viewsets
from django.shortcuts import get_object_or_404
import re
from django.db.models import (
    Q,
    When,
    Value,
    BooleanField,
    Exists,
    OuterRef,
)
from django.http import Http404
from rest_framework.parsers import MultiPartParser, FormParser

from authentication.models import UserProfile
from social_net.models import Blog, Post

from .models import Commentary
from notifications.models import Notification
from serializers import PostCommentaryListSerializer, PostCommentarySerializer


class ListSetPagination(PageNumberPagination):
    page_size = 5


class CommentaryPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        isAdmin = (
            request.user and request.user.is_authenticated and request.user.is_admin
        )
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == "POST":
            IsPostAccessibleForComments = Post.objects.filter(
                post_id=view.kwargs["post_id"], blog__slug=view.kwargs["slug"]
            )
            return bool(
                IsPostAccessibleForComments
                and request.user.id
                and request.user.is_authenticated
            )
        else:
            isBlogOwnerOrBlogAuthorOrAuthorOfComment = Commentary.objects.filter(
                Q(comment_id=view.kwargs["comment_id"])
                & Q(post__post_id=view.kwargs["post_id"])
                & Q(post__blog__slug=view.kwargs["slug"])
                & (
                    Q(post__blog__owner=request.user.id)
                    | Q(post__blog__authors__username__contains=request.user)
                    | Q(author=request.user.id)
                )
            )
            return bool(
                (isBlogOwnerOrBlogAuthorOrAuthorOfComment or isAdmin)
                and IsAuthenticated
            )

    def has_object_permission(self, request, view, obj):
        isAdmin = IsAuthenticated and request.user.is_admin
        isBlogOwner = IsAuthenticated and obj.post.blog.owner == request.user
        isBlogAuthor = IsAuthenticated and obj.post.blog.authors.filter(
            username__contains=request.user
        )
        isUserCommentAuthor = IsAuthenticated and obj.author == request.user
        if request.method in permissions.SAFE_METHODS:
            if obj.post.is_published:
                return True
            if not ((isBlogAuthor or isBlogOwner or isAdmin) and IsAuthenticated):
                raise Http404
        if request.method == "DELETE":
            return bool(isUserCommentAuthor or isAdmin or isBlogOwner)
        if request.method == "PUT":
            return bool(isUserCommentAuthor or isAdmin)


class PinCommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def pin_comment(self, request, slug, post_id, comment_id):
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        user = get_object_or_404(UserProfile, username=request.user.username)
        comment = get_object_or_404(Commentary, comment_id=comment_id, post=post)
        if comment.reply_to is None and comment.is_pinned == False:
            pinned_comment = Commentary.objects.filter(
                post=post, is_pinned=True, reply_to=None
            )
            if pinned_comment:
                pinned_comment.is_pinned = False
                pinned_comment.save(
                    update_fields=(
                        "is_pinned",
                        "pinned_by_user",
                    )
                )
            comment.is_pinned = True
            comment.pinned_by_user = user
            comment.save(
                update_fields=(
                    "is_pinned",
                    "pinned_by_user",
                )
            )
            return Response({"status: success"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status: unsuccessful"}, status=status.HTTP_400_BAD_REQUEST
            )

    def unpin_comment(self, request, slug, post_id, comment_id):
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        comment = get_object_or_404(Commentary, comment_id=comment_id, post=post)
        if comment.reply_to is None and comment.is_pinned == True:
            comment.is_pinned = False
            comment.pinned_by_user = None
            comment.save(
                update_fields=(
                    "is_pinned",
                    "pinned_by_user",
                )
            )
            return Response({"status: success"}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"status: unsuccessful"}, status=status.HTTP_400_BAD_REQUEST
            )


class PostCommentListView(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = PostCommentaryListSerializer
    permission_classes = [AllowAny]
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            post__blog__slug=self.kwargs["slug"], post__post_id=self.kwargs["post_id"]
        )
        blog = get_object_or_404(Blog, slug=self.kwargs["slug"])
        post = get_object_or_404(Post, post_id=self.kwargs["post_id"], blog=blog)

        parent_id = self.request.query_params.get("parent_id", None)
        sort_by = self.request.query_params.get("sort_by", None)

        if sort_by:
            if sort_by == "newest":
                queryset = queryset.order_by("-is_pinned", "-created_at")
            if sort_by == "oldest":
                queryset = queryset.order_by("-is_pinned", "created_at")

        if parent_id:
            model = Commentary.objects.get(
                comment_id=parent_id, post=post, post__blog=blog
            )
            queryset = queryset.filter(reply_to=model)
        else:
            queryset = queryset.filter(reply_to=None)

        if request.user.is_authenticated:
            queryset = queryset.annotate(
                isLiked=Exists(
                    Commentary.objects.filter(
                        liked_users=request.user, id=OuterRef("pk")
                    )
                ),
                isDisliked=Exists(
                    Commentary.objects.filter(
                        disliked_users=request.user, id=OuterRef("pk")
                    )
                ),
            )
        else:
            queryset = queryset.annotate(
                isLiked=Value(False, output_field=BooleanField()),
                isDisliked=Value(False, output_field=BooleanField()),
            )

        paginate_queryset = self.paginate_queryset(queryset)
        serializer = self.serializer_class(paginate_queryset, many=True)
        response = self.get_paginated_response(serializer.data)
        return Response(data=response.data, status=status.HTTP_200_OK)


class CommentaryPage(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = CreateCommentarySerializer
    permission_classes = [CommentaryPermissions]

    # def get_serializer_class(self):
    #     if self.request.method == "POST" or self.request.method == "PUT":
    #         return CreateCommentarySerializer
    #     return CommentarySerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateCommentarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body = serializer.data["body"]
        reply_to = serializer.data["reply_to"]
        blog = get_object_or_404(Blog, slug=self.kwargs["slug"])
        post = get_object_or_404(Post, post_id=self.kwargs["post_id"], blog=blog)
        if reply_to:
            parent_comment = get_object_or_404(
                Commentary, comment_id=reply_to, post=post
            )
        blog.count_of_commentaries += 1
        blog.save(update_fields=("count_of_commentaries",))
        comment_id = blog.count_of_commentaries

        if reply_to:
            commentary = get_object_or_404(Commentary, comment_id=reply_to, post=post)
            comm = Commentary(
                body=body,
                author=request.user,
                post=post,
                comment_id=comment_id,
                reply_to=commentary,
            )
        else:
            comm = Commentary(
                body=body,
                author=request.user,
                post=post,
                comment_id=comment_id,
            )
        comm.save()

        addressee_regex = r"@\w+"
        addressees = re.findall(addressee_regex, body)
        new_addressees = " ".join(addressees).split("@")

        for addressee in new_addressees:
            message = f'Пользователь {addressee} оставил комментарий "{body}"'
            if UserProfile.objects.filter(username=addressee).exists():
                user = UserProfile.objects.get(username=addressee)
                notification = Notification(
                    parent_comment=parent_comment,
                    replied_comment=comm,
                    post=post,
                    text=message,
                    addressee=user,
                    author=request.user,
                    is_read=False,
                )
                notification.save()

        serial = PostCommentarySerializer(comm, many=False)
        return Response(serial.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs["slug"])
        post = get_object_or_404(Post, post_id=self.kwargs["post_id"], blog=blog)
        comment = get_object_or_404(
            Commentary, comment_id=self.kwargs["comment_id"], post=post
        )
        comment.is_edited = True
        serializer = CreateCommentarySerializer(
            instance=comment, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"status: successful"}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs["slug"])
        post = get_object_or_404(Post, post_id=self.kwargs["post_id"], blog=blog)
        comment = get_object_or_404(
            Commentary, comment_id=self.kwargs["comment_id"], post=post
        )
        comment.delete()
        return Response(status=status.HTTP_200_OK)


class SetCommentLikeByAuthorView(viewsets.ModelViewSet):
    permissions_classes = [IsAuthenticated]

    def set_or_remove_like_by_author(self, request, slug, post_id, comment_id):
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        comment = get_object_or_404(Commentary, comment_id=comment_id, post=post)
        if not comment.liked_by_author:
            comment.liked_by_author = True
            comment.save(update_fields=("liked_by_author",))
            return Response({"status": "successful"}, status=status.HTTP_200_OK)
        else:
            comment.liked_by_author = False
            comment.save(update_fields=("liked_by_author",))
            return Response({"status": "successful"}, status=status.HTTP_200_OK)


class SetCommentLikeView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def set_or_remove_like(self, request, slug, post_id, comment_id):
        user = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        comment = get_object_or_404(Commentary, comment_id=comment_id, post=post)
        if comment.disliked_users.contains(user):
            comment.disliked_users.remove(user)
            comment.dislikes -= 1
        if not comment.liked_users.contains(user):
            comment.liked_users.add(user)
            comment.likes += 1
        else:
            comment.liked_users.remove(user)
            comment.likes -= 1
        comment.save(update_fields=("likes", "dislikes"))
        return Response({"status": "successful"}, status=status.HTTP_200_OK)

    def set_or_remove_dislike(self, request, slug, post_id, comment_id):
        user = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        comment = get_object_or_404(Commentary, comment_id=comment_id, post=post)
        if comment.liked_users.contains(user):
            comment.liked_users.remove(user)
            comment.likes -= 1
        if not comment.disliked_users.contains(user):
            comment.disliked_users.add(user)
            comment.dislikes = +1
        else:
            comment.disliked_users.remove(user)
            comment.dislikes -= 1
        comment.save(update_fields=("likes", "dislikes"))
        return Response({"status": "successful"}, status=status.HTTP_200_OK)


class PostCommentNotificationView(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = PostCommentaryListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(
            post__blog__slug=self.kwargs["slug"], post__post_id=self.kwargs["post_id"]
        )

        parent_id = self.request.query_params.get("parent_id", None)

        blog = get_object_or_404(Blog, slug=self.kwargs["slug"])
        post = get_object_or_404(Post, post_id=self.kwargs["post_id"], blog=blog)

        if parent_id:
            parent_comment = Commentary.objects.get(
                comment_id=parent_id, post=post, post__blog=blog
            )
            queryset = queryset.filter(reply_to=parent_comment)
        else:
            queryset = queryset.filter(reply_to=None)

        queryset = queryset.annotate(
            isLiked=Exists(
                Commentary.objects.filter(liked_users=request.user, id=OuterRef("pk"))
            ),
            isDisliked=Exists(
                Commentary.objects.filter(
                    disliked_users=request.user, id=OuterRef("pk")
                )
            ),
        )

        paginate_queryset = self.paginate_queryset(queryset)
        serializer = self.serializer_class(paginate_queryset, many=True)
        response = self.get_paginated_response(serializer.data)
        return Response(data=response.data, status=status.HTTP_200_OK)
