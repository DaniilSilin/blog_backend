from django.urls import path
from .viewsets import BlogList, BlogPage, PostList, MyPosts, BlogPosts, PostPage, CommentaryPage, BlogSubscribe, SubscriptionList2, AddLike

blog_list = BlogList.as_view({'get': 'list'})
blog_page = BlogPage.as_view({'put': 'update', 'get': 'list', 'delete': 'destroy'})
blog_create = BlogPage.as_view({'post': 'create'})
blog_posts = BlogPosts.as_view({'get': 'list'})

blog_sub = BlogSubscribe.as_view({'post': 'subscribe'})
blog_unsub = BlogSubscribe.as_view({'post': 'unsubscribe'})
user_subscriptions = SubscriptionList2.as_view({'get': 'list'})

set_like = AddLike.as_view({'post': 'set_like'})
remove_like = AddLike.as_view({'post': 'remove_like'})

post_list = PostList.as_view({'get': 'list'})
my_posts = MyPosts.as_view({'get': 'list'})
post_page = PostPage.as_view({'put': 'update', 'get': 'list', 'delete': 'destroy'})
post_create = PostPage.as_view({'post': 'create'})

create_commentary = CommentaryPage.as_view({'post': 'create'})
commentary = CommentaryPage.as_view({'get': 'list', 'delete': 'destroy', 'put': 'update'})

urlpatterns = [
    path('blog/list/', blog_list, name='blog_list'),
    path('blog/create/', blog_create, name='create_blog'),
    path('blog/<slug:slug>/', blog_page, name='blog_page'),

    path('<slug:username>/subscriptions/', user_subscriptions, name='user_subscriptions'),
    path('blog/<slug:slug>/subscribe/', blog_sub, name='blog_subscribe'),
    path('blog/<slug:slug>/unsubscribe/', blog_unsub, name='blog_unsubscribe'),

    path('blog/<slug:slug>/post/<int:post_id>/like/set/', set_like, name='add_like'),
    path('blog/<slug:slug>/post/<int:post_id>/like/remove/', remove_like, name='unlike'),

    path('blog/<slug:slug>/posts/', blog_posts, name='blog_posts'),
    path('post/list/', post_list, name='post_list'),
    path('posts/my/', my_posts, name='my_posts'),

    path('blog/<slug:slug>/post/create/', post_create, name='create_post'),
    path('blog/<slug:slug>/post/<int:post_id>/', post_page, name='post_page'),

    path('blog/<slug:slug>/post/<int:post_id>/comment/create/', create_commentary, name='create_commentary'),
    path('blog/<slug:slug>/post/<int:post_id>/comment/<int:comment_id>/', commentary, name='commentary')
]
