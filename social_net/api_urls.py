from django.urls import path
from .viewsets import BlogList, BlogPage, PostList, MyPosts, BlogPosts, PostPage, CreateCommentary

blog_list = BlogList.as_view({'get': 'list'})
blog_page = BlogPage.as_view({'put': 'update', 'get': 'list', 'delete': 'destroy'})
blog_create = BlogPage.as_view({'post': 'create'})
blog_posts = BlogPosts.as_view({'get': 'list'})

post_list = PostList.as_view({'get': 'list'})
my_posts = MyPosts.as_view({'get': 'list'})
post_page = PostPage.as_view({'put': 'update', 'get': 'list', 'delete': 'destroy', 'post': 'create'})
post_create = PostPage.as_view({'post': 'create'})

create_commentary = CreateCommentary.as_view({'post': 'create'})

urlpatterns = [
    path('blog/list/', blog_list, name='blog_list'),
    path('blog/create/', blog_create, name='create_blog'),
    path('blog/<slug:slug>/', blog_page, name='blog_page'),

    path('blog/<slug:slug>/posts/', blog_posts, name='blog_posts'),
    path('post/list/', post_list, name='post_list'),
    path('posts/my/', my_posts, name='my_posts'),

    path('blog/<slug:slug>/post/create/', post_create, name='create_post'),
    path('blog/<slug:slug>/post/<int:id>/', post_page, name='post_page'),

    path('blog/<slug:slug>/post/<int:id>/comment/<int:comment_id>/', create_commentary, name='create_commentary'),
]
