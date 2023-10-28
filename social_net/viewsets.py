from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404

from authentication.models import UserProfile
from .models import Blog, Post, Commentary, Tag
from .serializers import BlogSerializer, CreateBlogSerializer, PostSerializer, CreatePostSerializer, \
    CreateCommentarySerializer


class IsBlogOwnerOrAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user is True or request.user.is_admin
        else:
            return bool(Blog.objects.filter(slug=view.kwargs['slug'], owner=request.user) or request.user.is_admin)


class ListSetPagination(PageNumberPagination):
    page_size = 10


class BlogList(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    pagination_class = ListSetPagination
    permission_classes = (permissions.AllowAny,)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        query_dict = {}
        order_array = []

        search = self.request.query_params.get('search', None)
        order = self.request.query_params.get('order', None)
        before = self.request.query_params.get('before', None)
        after = self.request.query_params.get('after', None)

        if after:
            query_dict['updated_at__gt'] = after
        if before:
            query_dict['updated_at__lt'] = before

        if order:
            sort_array = order.split(',')

            if 'title_asc' in sort_array:
                target_index = sort_array.index("title_asc")
                sort_array[target_index] = "title"
            if 'title_desc' in sort_array:
                target_index = sort_array.index("title_desc")
                sort_array[target_index] = "-title"
            if 'date' in sort_array:
                target_index = sort_array.index("date")
                sort_array[target_index] = "updated_at"
            if '-date' in sort_array:
                target_index = sort_array.index("-date")
                sort_array[target_index] = "-updated_at"

        queryset = queryset.filter(**query_dict).order_by(*order_array).distinct()

        queryset = BlogSerializer(queryset, many=True)
        return Response(queryset.data, status=status.HTTP_200_OK)


class BlogPage(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    permission_classes = [IsBlogOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
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

    def create(self, request, *args, **kwargs):
        serializer = CreateBlogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        slug = serializer.data['slug']
        description = serializer.data['description']
        owner_pk = UserProfile.objects.get(username=request.user)
        authors = serializer.data['authors']

        blog = Blog(
            title=title,
            slug=slug,
            description=description,
            owner=owner_pk,
        )

        blog.save()
        blog.authors.set(authors)

        # serial = BlogSerializer(blog, many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def filter_queryset(self, queryset):
        return queryset.filter(slug=self.kwargs['slug'])


class PostList(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = (permissions.AllowAny,)

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        query_dict = {}
        order_array = []

        tags = self.request.query_params.get('tags', None)
        before = self.request.query_params.get('before', None)
        after = self.request.query_params.get('after', None)
        order = self.request.query_params.get('order', None)
        search = self.request.query_params.get('search', None)

        if after:
            query_dict['created_at__gt'] = after
        if before:
            query_dict['created_at__lt'] = before

        if search:
            query_dict = {**query_dict, 'title__contains': search, 'author__username__contains': search}

        if tags:
            order_query1 = tags.split(',')
            tag_list = []

            for tag in order_query1:
                if Tag.objects.filter(name=tag).exists():
                    tag_pk = Tag.objects.get(name=tag).pk
                    tag_list += [tag_pk]
                else:
                    return Response(status.HTTP_200_OK)

            query_dict = {**query_dict, 'tags__in': tag_list}

        if order:
            order_query_split = order.split(',')
            list_of_order = ['title_asc', 'title_desc', 'date', '-date']

            for order in order_query_split:
                if order in list_of_order:
                    if 'title_asc' in order_array:
                        order_array += ['title']
                    if 'title_desc' in order_array:
                        order_array += ['-title']
                    if 'date' in order_array:
                        order_array += ['created_at']
                    if '-date' in order_array:
                        order_array += ['-created_at']
                else:
                    return Response(status=status.HTTP_200_OK)

        queryset = queryset.filter(**query_dict).order_by(*order_array).distinct()

        serial = PostSerializer(queryset, many=True)
        return Response(serial.data, status=status.HTTP_200_OK)


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


class PostPage(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [IsBlogOwnerOrAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
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

    def create(self, request, *args, **kwargs):
        serializer = CreatePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        body = serializer.data['body']
        is_published = serializer.data['is_published']
        author = get_object_or_404(UserProfile, pk=serializer.data['author'])
        blog = get_object_or_404(Blog, pk=serializer.data['blog'])

        post = Post(
            title=title,
            body=body,
            is_published=is_published,
            author=author,
            blog=blog,
        )

        post.save()

        return Response('success', status=status.HTTP_200_OK)


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

