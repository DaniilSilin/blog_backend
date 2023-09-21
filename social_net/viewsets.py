from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from .models import Blog
from .serializers import AllBlogsSerializer, CreateBlogSerializer


class IsBlogOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(Blog.objects.filter(title=view.kwargs['title'], owner=request.user) or request.user.is_admin)


class AllBlogsSetPagination(PageNumberPagination):
    page_size = 10


class AllBlogs(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = AllBlogsSerializer
    pagination_class = AllBlogsSetPagination
    permission_classes = (permissions.AllowAny,)


class BlogPage(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = CreateBlogSerializer
    permission_classes = [IsBlogOwnerOrAdmin]

    def destroy(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, title=self.kwargs['title'])
        blog.delete()
        return Response('success', status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

    def filter_queryset(self, queryset):
        return queryset.filter(title=self.kwargs['title'])


class CreateBlog(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = CreateBlogSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        id = serializer.data['id']
        title = serializer.data['title']
        description = serializer.data['description']
        owner = serializer.data['owner']
        authors = serializer.data['authors']

        blog = Blog(
            id=id,
            title=title,
            description=description,
            owner=owner,
        )

        blog.save()
        blog.authors.set(authors)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

