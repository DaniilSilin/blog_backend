from django.http import JsonResponse
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from authentication.models import UserProfile
from .models import Blog, Post
from .serializers import BlogListSerializer, BlogSerializer, CreatePostSerializer, PostListSerializer


class IsBlogOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(Blog.objects.filter(slug=view.kwargs['slug'], owner=request.user) or request.user.is_admin)


class ListSetPagination(PageNumberPagination):
    page_size = 10


class BlogList(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogListSerializer
    pagination_class = ListSetPagination
    permission_classes = (permissions.AllowAny,)


class PostList(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    pagination_class = ListSetPagination
    permission_classes = (permissions.AllowAny,)


class MyPosts(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = Post.objects.filter(author=request.user)
        data = PostListSerializer(queryset, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class BlogPosts(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostListSerializer

    def list(self, request, *args, **kwargs):
        queryset = Post.objects.filter(blog__title=self.kwargs['title'])
        serial = PostListSerializer(queryset, many=True)
        return Response(serial.data, status=status.HTTP_200_OK)


class BlogPage(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsBlogOwnerOrAdmin]

    def destroy(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        blog.delete()
        return Response('success', status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        blog = Blog.objects.get(slug=self.kwargs['slug'])
        data = BlogSerializer(instance=blog, data=request.data)
        data.is_valid(raise_exception=True)
        data.save()
        return Response(data.data, status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        return queryset.filter(slug=self.kwargs['slug'])


class CreateBlog(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        description = serializer.data['description']
        owner = get_object_or_404(UserProfile, pk=serializer.data['owner'])
        authors = serializer.data['authors']

        blog = Blog(
            title=title,
            description=description,
            owner=owner,
        )

        blog.save()
        blog.authors.set(authors)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreatePost(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        body = serializer.data['body']
        is_published = serializer.data['is_published']
        likes = serializer.data['likes']
        views = serializer.data['views']
        author = get_object_or_404(UserProfile, pk=serializer.data['author'])
        blog = get_object_or_404(Blog, pk=serializer.data['blog'])

        post = Post(
            title=title,
            body=body,
            is_published=is_published,
            likes=likes,
            views=views,
            author=author,
            blog=blog,
        )

        post.save()

        return Response('success', status=status.HTTP_200_OK)

