from django.urls import path
from viewsets import (
    CommentaryPage,
    PostCommentListView,
    PinCommentViewSet,
    SetCommentLikeByAuthorView,
    SetCommentLikeView,
    PostCommentNotificationView,
)

create_commentary = CommentaryPage.as_view({"post": "create"})
commentary = CommentaryPage.as_view(
    {"get": "retrieve", "delete": "destroy", "put": "update"}
)
post_comment_list = PostCommentListView.as_view({"get": "list"})

set_or_remove_comment_like = SetCommentLikeView.as_view({"post": "set_or_remove_like"})
set_or_remove_comment_dislike = SetCommentLikeView.as_view(
    {"post": "set_or_remove_dislike"}
)
set_or_remove_like_by_author = SetCommentLikeByAuthorView.as_view(
    {"post": "set_or_remove_like_by_author"}
)

pin_comment = PinCommentViewSet.as_view({"post": "pin_comment"})
unpin_comment = PinCommentViewSet.as_view({"post": "unpin_comment"})

post_comment_list_reply = PostCommentNotificationView.as_view({"get": "list"})

urlpatterns = [
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/pin/",
        pin_comment,
        name="pin_comment",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/list/",
        post_comment_list,
        name="post_comment_list",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/like_by_author/",
        set_or_remove_like_by_author,
        name="set_or_remove_like_by_author",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/",
        commentary,
        name="commentary",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/create/",
        create_commentary,
        name="create_commentary",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/like/",
        set_or_remove_comment_like,
        name="add_like",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/dislike/",
        set_or_remove_comment_dislike,
        name="add_dislike",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/list/reply/",
        post_comment_list_reply,
        name="post_comment_list_reply",
    ),
]
