from django.urls import path
from .viewsets import BlogList, BlogPage, PostList, MyPosts, BlogPosts, PostPage, CommentaryPage, BlogSubscribe, BookmarksListView, \
    SubscriptionListViewSet, LikeViewSet, InvitationView, InviteReactView, InviteListView, LeaveBlogView, KickUserView, PinPostViewSet, \
    IsBlogOwner, IsSlugAvailable, InviteGetUsers, UserProfileView, ChangeUserProfileView, PostSearchView, PostCommentListView,\
    BlogPublicationsView, BookmarkView, PinCommentViewSet, LikedUserList, ChangeAvatarView, DeleteAvatarView, BlogEditorPostsView, BlogsWhereUserIsOwner, \
    BlogsWhereUserIsAuthor, BlogInvitationListView, BlogComments, LikedPostListView, SubscriptionListView, SubscriptionMiniList, BlogAuthorList, SetCommentLikeView

blog_list = BlogList.as_view({'get': 'list'})
blog_page = BlogPage.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'})
blog_create = BlogPage.as_view({'post': 'create'})
blog_posts = BlogPosts.as_view({'get': 'list'})
blog_comments = BlogComments.as_view({'get': 'list'})
# blog_authors = BlogAuthors.as_view({'get': 'list'})

profile = UserProfileView.as_view({'get': 'retrieve'})
change_profile = ChangeUserProfileView.as_view({'post': 'update'})

blog_sub = BlogSubscribe.as_view({'post': 'subscribe'})
blog_unsub = BlogSubscribe.as_view({'post': 'unsubscribe'})
user_subscriptions = SubscriptionListViewSet.as_view({'get': 'list'})

add_like = LikeViewSet.as_view({'post': 'add_like'})
remove_like = LikeViewSet.as_view({'post': 'remove_like'})

post_list = PostList.as_view({'get': 'list'})
my_posts = MyPosts.as_view({'get': 'list'})
post_page = PostPage.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'})
post_create = PostPage.as_view({'post': 'create'})

create_commentary = CommentaryPage.as_view({'post': 'create'})
commentary = CommentaryPage.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': 'update'})
post_comment_list = PostCommentListView.as_view({'get': 'list'})
pin_post = PinPostViewSet.as_view({'post': 'pin_post'})
pin_comment = PinCommentViewSet.as_view({'post': 'pin_comment'})

invite = InvitationView.as_view({'post': 'send_invite'})
invite_list = InviteListView.as_view({'get': 'list'})
invite_accept = InviteReactView.as_view({'post': 'accept_invite'})
invite_reject = InviteReactView.as_view({'post': 'reject_invite'})
invite_get_users = InviteGetUsers.as_view({'get': 'list'})

leave_blog = LeaveBlogView.as_view({'post': 'leave_blog'})
kick_user = KickUserView.as_view({'post': 'kick_user'})

is_blog_owner = IsBlogOwner.as_view({'get': 'is_blog_owner'})
is_slug_available = IsSlugAvailable.as_view({'get': 'is_slug_available'})

search = PostSearchView.as_view({'get': 'list'})

blog_publications = BlogPublicationsView.as_view({'get': 'list'})

add_bookmark = BookmarkView.as_view({'post': 'add_bookmark'})
remove_bookmark = BookmarkView.as_view({'post': 'remove_bookmark'})

liked_user_list = LikedUserList.as_view({'get': 'list'})

change_avatar = ChangeAvatarView.as_view({'put': 'update'})

delete_avatar = DeleteAvatarView.as_view({'delete': 'destroy'})

blog_editor_posts = BlogEditorPostsView.as_view({'get': 'list'})

username_blogs_owner = BlogsWhereUserIsOwner.as_view({'get': 'list'})
username_blogs_author = BlogsWhereUserIsAuthor.as_view({'get': 'list'})

blog_invitations = BlogInvitationListView.as_view({'get': 'list'})

liked_posts = LikedPostListView.as_view({'get': 'list'})
bookmarked_posts = BookmarksListView.as_view({'get': 'list'})
subscriptions = SubscriptionListView.as_view({'get': 'list'})
subscriptions_mini = SubscriptionMiniList.as_view({'get': 'list'})

blog_authors = BlogAuthorList.as_view({'get': 'list'})

set_or_remove_comment_like = SetCommentLikeView.as_view({'post': 'set_or_remove_like'})
set_or_remove_comment_dislike = SetCommentLikeView.as_view({'post': 'set_or_remove_dislike'})

urlpatterns = [
    path('blog/list/', blog_list, name='blog_list'),
    path('blog/create/', blog_create, name='create_blog'),
    path('blog/<slug:slug>/', blog_page, name='blog_page'),
    path('blog/<slug:slug>/authors/', blog_authors, name='blog_authors'),

    # path('blog/${slug}/authors/', blog_authors, name='blog_authors'),
    path('profile/<slug:username>/', profile, name='profile'),
    path('profile/<slug:username>/change/', change_profile, name='change_profile'),
    path('profile/<slug:username>/change/avatar/', change_avatar, name='change_avatar'),
    path('profile/<slug:username>/avatar/delete/', delete_avatar, name='delete_avatar'),

    path('<slug:username>/subscriptions/', user_subscriptions, name='user_subscriptions'),

    path('blog/<slug:slug>/subscribe/', blog_sub, name='blog_subscribe'),
    path('blog/<slug:slug>/unsubscribe/', blog_unsub, name='blog_unsubscribe'),

    path('blog/<slug:slug>/post/<int:post_id>/like/add/', add_like, name='add_like'),
    path('blog/<slug:slug>/post/<int:post_id>/like/remove/', remove_like, name='unlike'),

    path('blog/<slug:slug>/posts/', blog_posts, name='blog_posts'),
    path('blog/<slug:slug>/invitations/', blog_invitations, name='blog_invitations'),
    path('post/list/', post_list, name='post_list'),
    path('posts/my/', my_posts, name='my_posts'),

    path('blog/<slug:slug>/post/create/', post_create, name='create_post'),
    path('blog/<slug:slug>/post/<int:post_id>/', post_page, name='post_page'),
    path('blog/<slug:slug>/post/<int:post_id>/pin_post/', pin_post, name='pin_post'),

    path('blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/like/add/', set_or_remove_comment_like, name='add_like'),
    path('blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/like/remove/', set_or_remove_comment_dislike, name='remove_like'),
    path('blog/<slug:slug>/post/<int:post_id>/comment/create/', create_commentary, name='create_commentary'),
    path('blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/', commentary, name='commentary'),
    path('blog/<slug:slug>/post/<int:post_id>/comment/list/', post_comment_list, name='post_comment_list'),
    path('blog/<slug:slug>/post/<int:post_id>/liked_user_list/', liked_user_list, name='liked_user_list'),
    path('blog/<slug:slug>/publications/', blog_publications, name='blog_publications'),

    path('invite/create/', invite, name='invite'),
    path('invite/list/', invite_list, name='invite_list'),
    path('invite/<int:pk>/accept/', invite_accept, name='accept_invite'),
    path('invite/<int:pk>/reject/', invite_reject, name='reject_invite'),
    path('invite/blog/<slug:slug>/get_users/', invite_get_users, name='invite_get_users'),

    path('blog_owner/list/', is_blog_owner, name='is_blog_owner'),
    path('blog/<slug:slug>/available/', is_slug_available, name='is_slug_available'),

    path('posts/search/<str:hashtag>/', search, name='search'),

    path('bookmark/blog/<slug:slug>/post/<int:post_id>/add/', add_bookmark, name='add_bookmark'),
    path('bookmark/blog/<slug:slug>/post/<int:post_id>/remove/', remove_bookmark, name='remove_bookmark'),

    path('blog/<slug:slug>/editor/posts/', blog_editor_posts, name='blog_editor_posts'),

    path('<slug:username>/blogs/owner/', username_blogs_owner, name='username_blogs_owner'),
    path('<slug:username>/blogs/author/', username_blogs_author, name='username_blogs_author'),

    path('blog/<slug:slug>/comments/', blog_comments, name='blog_comments'),

    path('liked_posts/', liked_posts, name='liked_posts'),
    path('subscriptions/', subscriptions, name='subscriptions'),
    path('bookmarked_posts/', bookmarked_posts, name='bookmarked_posts'),
    path('subscriptions/mini/', subscriptions_mini, name='subscriptions_mini'),

    path('blog/<slug:slug>/leave/', leave_blog, name='leave_blog'),
    path('blog/<slug:slug>/kick/<slug:username>/', kick_user, name='kick_user'),
]
