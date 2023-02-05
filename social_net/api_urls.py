from django.urls import path, include
from .viewsets import CreateBlog, CreatePost

create_blog = CreateBlog.as_view({'post': 'create'})
create_post = CreatePost.as_view({'post': 'create'})

urlpatterns = [
    path('create_blog/', create_blog, name='create_blog'),
    path('create_post/', create_post, name='create_post')
]
