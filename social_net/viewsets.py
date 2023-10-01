from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from authentication.models import UserProfile
from .models import Blog, Post, Commentary
from .serializers import BlogSerializer, CreateBlogSerializer, PostSerializer, CreatePostSerializer, CreateCommentarySerializer


class IsBlogOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(Blog.objects.filter(slug=view.kwargs['slug'], owner=request.user) or request.user.is_admin)


class ListSetPagination(PageNumberPagination):
    page_size = 10


class BlogList(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    pagination_class = ListSetPagination
    permission_classes = (permissions.AllowAny,)


class PostList(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = (permissions.AllowAny,)


class MyPosts(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [IsBlogOwnerOrAdmin]

    def list(self, request, *args, **kwargs):
        queryset = Post.objects.filter(author=request.user)
        data = PostSerializer(queryset, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class BlogPosts(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def list(self, request, *args, **kwargs):
        queryset = Post.objects.filter(blog__slug=self.kwargs['slug'])
        serial = PostSerializer(queryset, many=True)
        return Response(serial.data, status=status.HTTP_200_OK)


class BlogPage(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    permission_classes = [IsBlogOwnerOrAdmin]

    def get_serializer_class(self):
        if self.action == 'update':
            return CreateBlogSerializer
        return BlogSerializer

    def destroy(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        blog.delete()
        return Response(status=status.HTTP_200_OK)

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
    serializer_class = CreateBlogSerializer
    permission_classes = [IsBlogOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        slug = serializer.data['slug']
        description = serializer.data['description']
        # Подумать над реализацией нижней строки, сделать, чтобы пользователь подставлялся автоматом при создании блога
        owner = UserProfile.objects.get(username=request.user)
        authors = serializer.data['authors']

        blog = Blog(
            title=title,
            description=description,
            owner=owner,
            slug=slug,
        )

        blog.save()
        blog.authors.set(authors)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreatePost(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = CreatePostSerializer
    permission_classes = [IsBlogOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        body = serializer.data['body']
        is_published = serializer.data['is_published']
        author = get_object_or_404(UserProfile, pk=serializer.data['author'])
        blog = get_object_or_404(Blog, pk=serializer.data['blog'])

        blog_id = Post.objects.filter(blog=serializer.data['blog']).count()
        id_of_current_post = blog_id + 1

        post = Post(
            title=title,
            body=body,
            is_published=is_published,
            author=author,
            blog=blog,
            post_id=id_of_current_post
        )

        post.save()
        return Response(status=status.HTTP_200_OK)


class PostPage(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsBlogOwnerOrAdmin]

    def get_serializer_class(self):
        if self.action == 'update':
            return CreatePostSerializer
        return PostSerializer

    def filter_queryset(self, queryset):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = Post.objects.get(post_id=self.kwargs['id'], blog=blog)
        post.views = post.views + 1
        post.save(update_fields=("views",))
        return queryset.filter(post_id=self.kwargs['id'], blog=blog)

    def destroy(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['id'], blog=blog)
        post.delete()
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        blog = Blog.objects.get(slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['id'], blog=blog)
        data = CreatePostSerializer(instance=post, data=request.data)
        data.is_valid(raise_exception=True)
        data.save()
        return Response(data.data, status=status.HTTP_200_OK)


class CreateCommentary(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = CreateCommentarySerializer
    permission_classes = [IsBlogOwnerOrAdmin]

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        body = serializer.data['body']
        author = request.user
        post = get_object_or_404(Post, pk=serializer.data['post'])

        comm = Commentary(
            body=body,
            author=author,
            post=post
        )

        comm.save()
        return Response(status=status.HTTP_201_CREATED)
