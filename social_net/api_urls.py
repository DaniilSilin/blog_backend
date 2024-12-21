from django.urls import path
from .viewsets import BlogList, BlogPage, PostList, MyPosts, BlogPosts, PostPage, CommentaryPage, BlogSubscribe, \
    SubscriptionListViewSet, LikeViewSet, InvitationView, InviteReactView, InviteListView, LeaveBlogView, KickUserView, \
    IsBlogOwner, IsSlugAvailable, InviteGetUsers, Subscriptions, UserProfileView, ChangeUserProfileView, PostSearchView, BlogCommentsView, BlogPublicationsView, PostCommentReplyList

blog_list = BlogList.as_view({'get': 'list'})
blog_page = BlogPage.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'})
blog_create = BlogPage.as_view({'post': 'create'})
blog_posts = BlogPosts.as_view({'get': 'list'})
# blog_authors = BlogAuthors.as_view({'get': 'list'})

profile = UserProfileView.as_view({'get': 'retrieve'})
change_profile = ChangeUserProfileView.as_view({'post': 'update'})

blog_sub = BlogSubscribe.as_view({'post': 'subscribe'})
blog_unsub = BlogSubscribe.as_view({'post': 'unsubscribe'})
user_subscriptions = SubscriptionListViewSet.as_view({'get': 'list'})
subscriptions = Subscriptions.as_view({'get': 'list'})

add_like = LikeViewSet.as_view({'post': 'add_like'})
remove_like = LikeViewSet.as_view({'post': 'remove_like'})

post_list = PostList.as_view({'get': 'list'})
my_posts = MyPosts.as_view({'get': 'list'})
post_page = PostPage.as_view({'put': 'update', 'get': 'retrieve', 'delete': 'destroy'})
post_create = PostPage.as_view({'post': 'create'})

create_commentary = CommentaryPage.as_view({'post': 'create'})
commentary = CommentaryPage.as_view({'get': 'retrieve', 'delete': 'destroy', 'put': 'update'})
blog_comments = BlogCommentsView.as_view({'get': 'list'})

invite = InvitationView.as_view({'post': 'send_invite'})
invite_list = InviteListView.as_view({'get': 'list'})
invite_accept = InviteReactView.as_view({'post': 'accept_invite'})
invite_reject = InviteReactView.as_view({'post': 'reject_invite'})
invite_get_users = InviteGetUsers.as_view({'get': 'get_users'})

leave_blog = LeaveBlogView.as_view({'post': 'leave_blog'})
kick_user = KickUserView.as_view({'post': 'kick_user'})

is_blog_owner = IsBlogOwner.as_view({'get': 'is_blog_owner'})
is_slug_available = IsSlugAvailable.as_view({'get': 'is_slug_available'})

search = PostSearchView.as_view({'get': 'list'})

blog_publications = BlogPublicationsView.as_view({'get': 'list'})
post_comment_reply_list = PostCommentReplyList.as_view({'get': 'list'})

urlpatterns = [
    path('blog/list/', blog_list, name='blog_list'),
    path('blog/create/', blog_create, name='create_blog'),
    path('blog/<slug:slug>/', blog_page, name='blog_page'),

    # path('blog/${slug}/authors/', blog_authors, name='blog_authors'),
    path('profile/<slug:username>/', profile, name='profile'),
    path('profile/<slug:username>/change/', change_profile, name='change_profile'),
    path('<slug:username>/subscriptions/', user_subscriptions, name='user_subscriptions'),

    path('subscriptions/', subscriptions, name='subscriptions'),
    path('blog/<slug:slug>/subscribe/', blog_sub, name='blog_subscribe'),
    path('blog/<slug:slug>/unsubscribe/', blog_unsub, name='blog_unsubscribe'),

    path('blog/<slug:slug>/post/<int:post_id>/like/add/', add_like, name='add_like'),
    path('blog/<slug:slug>/post/<int:post_id>/like/remove/', remove_like, name='unlike'),

    path('blog/<slug:slug>/posts/', blog_posts, name='blog_posts'),
    path('post/list/', post_list, name='post_list'),
    path('posts/my/', my_posts, name='my_posts'),

    path('blog/<slug:slug>/post/create/', post_create, name='create_post'),
    path('blog/<slug:slug>/post/<int:post_id>/', post_page, name='post_page'),

    path('blog/<slug:slug>/post/<int:post_id>/comment/create/', create_commentary, name='create_commentary'),
    path('blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/', commentary, name='commentary'),
    path('blog/<slug:slug>/post/<int:post_id>/comments/', blog_comments, name='blog_comments'),
    path('blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/replies/', post_comment_reply_list, name='post_comment_reply_list'),
    path('blog/<slug:slug>/publications/', blog_publications, name='blog_publications'),

    path('invite/create/', invite, name='invite'),
    path('invite/list/', invite_list, name='invite_list'),
    path('invite/<int:pk>/accept/', invite_accept, name='accept_invite'),
    path('invite/<int:pk>/reject/', invite_reject, name='reject_invite'),
    path('invite/get_users/<slug:username>/', invite_get_users, name='invite_get_users'),

    path('blog/<slug:slug>/leave/', leave_blog, name='leave_blog'),
    path('blog/<slug:slug>/kick/<slug:username>/', kick_user, name='kick_user'),

    path('blog_owner/list/', is_blog_owner, name='is_blog_owner'),
    path('blog/<slug:slug>/available/', is_slug_available, name='is_slug_available'),

    path('posts/search/', search, name='search'),
]
