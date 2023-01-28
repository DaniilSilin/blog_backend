from django.urls import path, include
from .viewsets import PostsList

all_posts = PostsList.as_view({'GET': 'list'})

urlpatterns = [
    path('posts/', all_posts, name='all_posts')
]
