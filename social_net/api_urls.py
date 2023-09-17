from django.urls import path
from .viewsets import AllBlogs, CreateBlog, BlogPage, DeleteBlog, BlogUpdate

all_blogs = AllBlogs.as_view({'get': 'list'})
create_blog = CreateBlog.as_view({'post': 'create'})
blog_page = BlogPage.as_view({'get': 'list'})
update_blog = BlogUpdate.as_view({'post': 'update'})
delete_blog = DeleteBlog.as_view({'delete': 'destroy'})

urlpatterns = [
    path('all_blogs/', all_blogs, name='all_blogs'),
    path('create_blog/', create_blog, name='create_blog'),
    path('<slug:title>/', blog_page, name='blog_page'),
    path('<slug:title>/update/', update_blog, name='blog_update'),
    path('<slug:title>/delete/', delete_blog, name='delete_blog'),
]
