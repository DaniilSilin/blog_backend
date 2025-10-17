from django.urls import path
from .viewsets import (
    BlogList,
    BlogPage,
    PostList,
    MyPosts,
    BlogPosts,
    PostPage,
    CommentaryPage,
    BlogSubscription,
    BookmarksListView,
    SubscriptionListViewSet,
    PostLikeDislikeViewSet,
    InvitationView,
    InvitationCreateView,
    InviteListView,
    LeaveBlogView,
    KickUserView,
    PinPostViewSet,
    IsBlogOwner,
    IsSlugAvailable,
    InviteGetUsers,
    UserProfileView,
    PostSearchView,
    PostCommentListView,
    BookmarkView,
    PinCommentViewSet,
    LikedUserList,
    ChangeAvatarView,
    DeleteAvatarView,
    BlogEditorPostsView,
    BlogsWhereUserIsOwner,
    BlogsWhereUserIsAuthor,
    BlogInvitationListView,
    BlogComments,
    LikedPostListView,
    SubscriptionListView,
    SubscriptionMiniList,
    BlogAuthorList,
    SetCommentLikeView,
    SetCommentLikeByAuthorView,
    BlogCommentsDeleteView,
    UserNotificationListView,
    PostCommentNotificationView,
    SetNotificationIsRead,
    HideNotificationView,
    BlogDeletePostsView,
    BlogPublicationsView,
)

blog_list = BlogList.as_view({"get": "list"})
blog_page = BlogPage.as_view(
    {"post": "create", "put": "update", "get": "retrieve", "delete": "destroy"}
)
blog_create = BlogPage.as_view({"post": "create"})
blog_posts = BlogPosts.as_view({"get": "list"})
blog_comments = BlogComments.as_view({"get": "list"})
# blog_authors = BlogAuthors.as_view({'get': 'list'})

profile = UserProfileView.as_view(
    {"get": "retrieve", "put": "update", "delete": "destroy"}
)

blog_subscription = BlogSubscription.as_view({"post": "toggle_subscription"})

user_subscriptions = SubscriptionListViewSet.as_view({"get": "list"})

post_list = PostList.as_view({"get": "list"})
my_posts = MyPosts.as_view({"get": "list"})
post_page = PostPage.as_view({"put": "update", "get": "retrieve", "delete": "destroy"})
post_create = PostPage.as_view({"post": "create"})

create_commentary = CommentaryPage.as_view({"post": "create"})
commentary = CommentaryPage.as_view(
    {"get": "retrieve", "delete": "destroy", "put": "update"}
)
post_comment_list = PostCommentListView.as_view({"get": "list"})
post_comment_list_reply = PostCommentNotificationView.as_view({"get": "list"})

pin_post = PinPostViewSet.as_view({"post": "pin_post"})
unpin_post = PinPostViewSet.as_view({"post": "unpin_post"})
pin_comment = PinCommentViewSet.as_view({"post": "pin_comment"})
unpin_comment = PinCommentViewSet.as_view({"post": "unpin_comment"})

invite_create = InvitationCreateView.as_view({"post": "create"})
invite_list = InviteListView.as_view({"get": "list"})
invite_accept = InvitationView.as_view({"post": "accept_invite"})
invite_reject = InvitationView.as_view({"post": "reject_invite"})
invite_get_users = InviteGetUsers.as_view({"get": "list"})

leave_blog = LeaveBlogView.as_view({"post": "leave_blog"})
kick_user = KickUserView.as_view({"post": "kick_user"})

is_blog_owner = IsBlogOwner.as_view({"get": "is_blog_owner"})
is_slug_available = IsSlugAvailable.as_view({"get": "is_slug_available"})

search = PostSearchView.as_view({"get": "list"})

blog_publications = BlogPublicationsView.as_view({"get": "list"})

liked_user_list = LikedUserList.as_view({"get": "list"})

change_avatar = ChangeAvatarView.as_view({"put": "update"})
delete_avatar = DeleteAvatarView.as_view({"delete": "destroy"})

blog_editor_posts = BlogEditorPostsView.as_view({"get": "list"})

username_blogs_owner = BlogsWhereUserIsOwner.as_view({"get": "list"})
username_blogs_author = BlogsWhereUserIsAuthor.as_view({"get": "list"})

blog_invitations = BlogInvitationListView.as_view({"get": "list"})

liked_posts = LikedPostListView.as_view({"get": "list"})
bookmarked_posts = BookmarksListView.as_view({"get": "list"})
subscriptions = SubscriptionListView.as_view({"get": "list"})
subscriptions_mini = SubscriptionMiniList.as_view({"get": "list"})

blog_authors = BlogAuthorList.as_view({"get": "list"})

set_or_remove_like = PostLikeDislikeViewSet.as_view({"post": "set_or_remove_like"})
set_or_remove_dislike = PostLikeDislikeViewSet.as_view(
    {"post": "set_or_remove_dislike"}
)

add_or_remove_bookmark = BookmarkView.as_view({"post": "add_or_remove_bookmark"})
set_or_remove_comment_like = SetCommentLikeView.as_view({"post": "set_or_remove_like"})
set_or_remove_comment_dislike = SetCommentLikeView.as_view(
    {"post": "set_or_remove_dislike"}
)
set_or_remove_like_by_author = SetCommentLikeByAuthorView.as_view(
    {"post": "set_or_remove_like_by_author"}
)

notification_list = UserNotificationListView.as_view({"get": "list"})
read_notification = SetNotificationIsRead.as_view({"post": "read_notification"})
hide_notification = HideNotificationView.as_view({"post": "hide_notification"})

blog_delete_posts = BlogDeletePostsView.as_view({"delete": "delete_posts"})
blog_delete_comments = BlogCommentsDeleteView.as_view({"delete": "delete_comments"})

urlpatterns = [
    path("blog/list/", blog_list, name="blog_list"),
    path("blog/create/", blog_page, name="create_blog"),
    path("blog/<slug:slug>/", blog_page, name="blog_page"),
    path("blog/<slug:slug>/subscription/", blog_subscription, name="blog_subscription"),
    path("blog/<slug:slug>/authors/", blog_authors, name="blog_authors"),
    path("blog/<slug:slug>/posts/delete/", blog_delete_posts, name="blog_delete_posts"),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/like_by_author/",
        set_or_remove_like_by_author,
        name="set_or_remove_like_by_author",
    ),
    # path('blog/${slug}/authors/', blog_authors, name='blog_authors'),
    path("profile/<slug:username>/", profile, name="profile"),
    path("profile/<slug:username>/change/avatar/", change_avatar, name="change_avatar"),
    path("profile/<slug:username>/avatar/delete/", delete_avatar, name="delete_avatar"),
    path(
        "profile/<slug:username>/notification/list/",
        notification_list,
        name="notification_list",
    ),
    path(
        "<slug:username>/subscriptions/", user_subscriptions, name="user_subscriptions"
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/like/",
        set_or_remove_like,
        name="set_or_remove_like",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/dislike/",
        set_or_remove_dislike,
        name="set_or_remove_dislike",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/bookmark/",
        add_or_remove_bookmark,
        name="add_or_remove_bookmark",
    ),
    path("blog/<slug:slug>/posts/", blog_posts, name="blog_posts"),
    path("blog/<slug:slug>/invitations/", blog_invitations, name="blog_invitations"),
    path("post/list/", post_list, name="post_list"),
    path("posts/my/", my_posts, name="my_posts"),
    path("blog/<slug:slug>/post/create/", post_create, name="create_post"),
    path("blog/<slug:slug>/post/<int:post_id>/", post_page, name="post_page"),
    path("blog/<slug:slug>/post/<int:post_id>/pin_post/", pin_post, name="pin_post"),
    path(
        "blog/<slug:slug>/post/<int:post_id>/unpin_post/", unpin_post, name="unpin_post"
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
        "blog/<slug:slug>/post/<int:post_id>/comment/create/",
        create_commentary,
        name="create_commentary",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/",
        commentary,
        name="commentary",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/list/",
        post_comment_list,
        name="post_comment_list",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/list/reply/",
        post_comment_list_reply,
        name="post_comment_list_reply",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/pin/",
        pin_comment,
        name="pin_comment",
    ),
    path(
        "blog/<slug:slug>/post/<int:post_id>/liked_user_list/",
        liked_user_list,
        name="liked_user_list",
    ),
    path("blog/<slug:slug>/publications/", blog_publications, name="blog_publications"),
    path("invite/create/", invite_create, name="invite_create"),
    path("invite/list/", invite_list, name="invite_list"),
    path("invite/<int:pk>/accept/", invite_accept, name="accept_invite"),
    path("invite/<int:pk>/reject/", invite_reject, name="reject_invite"),
    path(
        "invite/blog/<slug:slug>/get_users/", invite_get_users, name="invite_get_users"
    ),
    path("blog_owner/list/", is_blog_owner, name="is_blog_owner"),
    path("blog/<slug:slug>/available/", is_slug_available, name="is_slug_available"),
    path("posts/search/<str:hashtag>/", search, name="search"),
    path("blog/<slug:slug>/editor/posts/", blog_editor_posts, name="blog_editor_posts"),
    path(
        "<slug:username>/blogs/owner/",
        username_blogs_owner,
        name="username_blogs_owner",
    ),
    path(
        "<slug:username>/blogs/author/",
        username_blogs_author,
        name="username_blogs_author",
    ),
    path("blog/<slug:slug>/comments/", blog_comments, name="blog_comments"),
    path("liked_posts/", liked_posts, name="liked_posts"),
    path("subscriptions/", subscriptions, name="subscriptions"),
    path("bookmarked_posts/", bookmarked_posts, name="bookmarked_posts"),
    path("subscriptions/mini/", subscriptions_mini, name="subscriptions_mini"),
    path("blog/<slug:slug>/leave/", leave_blog, name="leave_blog"),
    path("blog/<slug:slug>/kick/<slug:username>/", kick_user, name="kick_user"),
    path(
        "notification/<int:pk>/is_read/", read_notification, name="notification_is_read"
    ),
    path("notification/<int:pk>/hide/", hide_notification, name="hide_notification"),
]
