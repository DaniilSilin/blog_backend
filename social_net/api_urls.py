from django.urls import path, include
from .viewsets import CreateBlog, CreatePost, AllPosts, AllBlogs, MyPosts, UserPost

create_blog = CreateBlog.as_view({'post': 'create'})
create_post = CreatePost.as_view({'post': 'create'})
all_posts = AllPosts.as_view({'get': 'list'})
all_blogs = AllBlogs.as_view({'get': 'list'})
my_posts = MyPosts.as_view({'get': 'list'})
user_post = UserPost.as_view({'get': 'retrieve'})


urlpatterns = [
    path('create_blog/', create_blog, name='create_blog'),
    path('create_post/', create_post, name='create_post'),
    path('all_posts/', all_posts, name='all_posts'),
    path('all_blogs/', all_blogs, name='all_blogs'),
    path('my_posts/', my_posts, name='my_posts'),
    path('<int:pk>/', user_post, name='user_post'),
    # path('')
]
