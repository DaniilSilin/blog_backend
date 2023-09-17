from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from .models import Blog, UserProfile
from .serializers import AllBlogsSerializer, CreateBlogSerializer, DeleteBlogSerializer


class AllBlogsSetPagination(PageNumberPagination):
    page_size = 10


class AllBlogs(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = AllBlogsSerializer
    pagination_class = AllBlogsSetPagination


class BlogPage(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = CreateBlogSerializer

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
        owner = get_object_or_404(UserProfile, pk=serializer.data['owner'])
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


class DeleteBlog(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = DeleteBlogSerializer

    def destroy(self, request, *args, **kwargs):
        print(self.kwargs['title'])
        find_blog = self.kwargs['title']
        model = get_object_or_404(Blog, title=find_blog)
        model.delete()
        return Response('success', status=status.HTTP_200_OK)
