from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .serializers import PostSerializer, BlogSerializer, AllPostsSerializer, AllBlogsSerializer
from .models import Post, Blog


class PostsPagination(PageNumberPagination):
    page_size = 2


class BlogsPagination(PageNumberPagination):
    page_size = 2


class AllPosts(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True)
    serializer_class = AllPostsSerializer
    pagination_class = PostsPagination


class AllBlogs(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = AllBlogsSerializer
    pagination_class = BlogsPagination


class CreatePost(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class CreateBlog(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer


class MyPosts(viewsets.ModelViewSet):
    queryset = Post.objects.filter()
    serializer_class = PostSerializer

    def filter_queryset(self, queryset):
        user = self.request.user.id
        return queryset.filter(author=user)


class UserPost(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def filter_queryset(self, queryset):
        return queryset.filter(id=self.kwargs['pk'])
