from django.urls import path
from .viewsets import AllBlogs, CreateBlog, BlogPage

all_blogs = AllBlogs.as_view({'get': 'list'})
create_blog = CreateBlog.as_view({'post': 'create'})
blog_page = BlogPage.as_view({'post': 'update', 'get': 'list', 'delete': 'destroy'})

urlpatterns = [
    path('blog/list/', all_blogs, name='blog_list'),
    path('blog/create/', create_blog, name='create_blog'),
    path('blog/<slug:title>/', blog_page, name='blog_page'),
]
