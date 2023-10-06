from django.urls import path
from .viewsets import BlogList, CreateBlog, BlogPage, CreatePost, PostList, MyPosts, BlogPosts, PostPage, \
    CreateCommentary, SubscriptionList

blog_list = BlogList.as_view({'get': 'list'})
create_blog = CreateBlog.as_view({'post': 'create'})
blog_page = BlogPage.as_view({'post': 'update', 'get': 'list', 'delete': 'destroy'})
blog_posts = BlogPosts.as_view({'get': 'list'})

post_list = PostList.as_view({'get': 'list'})
my_posts = MyPosts.as_view({'get': 'list'})
create_post = CreatePost.as_view({'post': 'create'})
post_page = PostPage.as_view({'post': 'update', 'get': 'list', 'delete': 'destroy'})

create_commentary = CreateCommentary.as_view({'post': 'create'})

urlpatterns = [
    path('blog/list/', blog_list, name='blog_list'),
    path('blog/create/', create_blog, name='create_blog'),
    path('blog/<slug:slug>/', blog_page, name='blog_page'),

    path('blog/<slug:slug>/posts/', blog_posts, name='blog_posts'),
    path('post/list/', post_list, name='post_list'),
    path('posts/my/', my_posts, name='my_posts'),

    path('blog/<slug:slug>/post/create/', create_post, name='create_post'),
    path('blog/<slug:slug>/post/<int:id>/', post_page, name='post_page'),

    path('blog/<slug:slug>/post/<int:id>/comment/create/', create_commentary, name='create_commentary'),

]
