from rest_framework.response import Response
from rest_framework import status, permissions, viewsets
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q

from authentication.models import UserProfile
from .models import Blog, Post, Commentary, Tag
from .serializers import BlogSerializer, CreateBlogSerializer, UpdateBlogSerializer, PostSerializer, \
    CreatePostSerializer, CreateCommentarySerializer, CommentarySerializer, SubscriptionList


class BlogPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return bool(request.user and request.user.is_authenticated)
        else:
            return bool(Blog.objects.filter(slug=view.kwargs['slug'], owner=request.user.id).exists() or (request.user and request.user.is_staff))


class PostPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return bool(request.user and request.user.is_authenticated)
        else:
            return bool(Post.objects.filter(Q(post_id=view.kwargs['post_id']) & (Q(blog__authors__username__contains=request.user) | Q(blog__owner=request.user.id))) or (request.user and request.user.is_staff))


class CommentaryPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return bool(request.user and request.user.is_authenticated)
        else:
            return bool(Commentary.objects.filter(comment_id=view.kwargs['comment_id'], author=request.user.id) or (request.user and request.user.is_staff))


class ListSetPagination(PageNumberPagination):
    page_size = 10


class BlogList(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by('-updated_at')
    serializer_class = BlogSerializer
    pagination_class = ListSetPagination
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        query_dict = {}
        sort_array = []

        search = self.request.query_params.get('search', None)
        order = self.request.query_params.get('order', None)
        before = self.request.query_params.get('before', None)
        after = self.request.query_params.get('after', None)

        if search:
            query_dict = {'title__contains': search, 'authors__username__contains': search}

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

        queryset = queryset.filter(**query_dict).order_by(*sort_array).distinct()

        queryset = BlogSerializer(queryset, many=True)
        return Response(queryset.data, status=status.HTTP_200_OK)


class BlogPage(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    permission_classes = [BlogPermissions]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateBlogSerializer
        if self.request.method == 'PUT':
            return UpdateBlogSerializer
        return BlogSerializer

    def destroy(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        blog.delete()
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        serializer = CreateBlogSerializer(instance=blog, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        instance_serializer = BlogSerializer(serializer)
        return Response(instance_serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = CreateBlogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        slug = serializer.data['slug']
        description = serializer.data['description']
        owner = get_object_or_404(UserProfile, username=request.user)
        authors = serializer.data['authors']

        blog = Blog(
            title=title,
            slug=slug,
            description=description,
            owner=owner,
        )

        blog.save()
        blog.authors.set(authors)

        serial = BlogSerializer(blog)
        return Response(serial.data, status=status.HTTP_201_CREATED)

    def filter_queryset(self, queryset):
        return queryset.filter(slug=self.kwargs['slug'])


class PostList(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True).order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [permissions.AllowAny]

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
            list_of_order = ['title_asc', 'title_desc', 'date', '-date', 'likes', '-likes']

            for order_query in order_query_split:
                if order_query in list_of_order:
                    if 'title_asc' in order_query_split:
                        order_array += ['title']
                    if 'title_desc' in order_query_split:
                        order_array += ['-title']
                    if 'date' in order_query_split:
                        order_array += ['created_at']
                    if '-date' in order_query_split:
                        order_array += ['-created_at']
                    if 'likes' in order_query_split:
                        order_array += ['likes']
                    if '-likes' in order_query_split:
                        order_array += ['-likes']
                else:
                    return Response(status=status.HTTP_200_OK)

        queryset = queryset.filter(**query_dict).order_by(*order_array).distinct()

        serial = PostSerializer(queryset, many=True)
        return Response(serial.data, status=status.HTTP_200_OK)


class MyPosts(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True).order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(author=request.user)
        data = PostSerializer(queryset, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class BlogPosts(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True)
    serializer_class = PostSerializer
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(blog__slug=self.kwargs['slug'])
        serial = PostSerializer(queryset, many=True)
        return Response(serial.data, status=status.HTTP_200_OK)


class PostPage(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [PostPermissions]

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return CreatePostSerializer
        return PostSerializer

    def filter_queryset(self, queryset):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        post.views += 1
        post.save(update_fields=("views",))
        return self.queryset.filter(post_id=self.kwargs['post_id'], blog=blog)

    def destroy(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        post.delete()
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        serializer = CreatePostSerializer(instance=post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serial = PostSerializer(serializer, many=False)
        return Response(serial.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = CreatePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        body = serializer.data['body']
        is_published = serializer.data['is_published']
        author = get_object_or_404(UserProfile, pk=serializer.data['author'])
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])

        blog.count_of_posts += 1
        blog.save(update_fields=("count_of_posts",))
        post_id = blog.count_of_posts

        post = Post(
            title=title,
            body=body,
            is_published=is_published,
            author=author,
            blog=blog,
            post_id=post_id
        )

        post.save()

        serial = PostSerializer(post)
        return Response(serial.data, status=status.HTTP_201_CREATED)


class CommentaryPage(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    permission_classes = [CommentaryPermissions]

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return CreateCommentarySerializer
        return CommentarySerializer

    def create(self, request, *args, **kwargs):
        serializer = CreateCommentarySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        body = serializer.data['body']
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'])
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])

        blog.count_of_commentaries += 1
        blog.save(update_fields=("count_of_commentaries",))
        comment_id = blog.count_of_commentaries

        comm = Commentary(
            body=body,
            author=request.user,
            post=post,
            comment_id=comment_id,
        )

        comm.save()
        serial = CommentarySerializer(comm, many=False)
        return Response(serial.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        comment = get_object_or_404(Commentary, comment_id=self.kwargs['comment_id'], post=post)
        serializer = CreateCommentarySerializer(instance=comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        comment = get_object_or_404(Commentary, comment_id=self.kwargs['comment_id'], post=post)
        comment.delete()
        return Response(status=status.HTTP_200_OK)

    def filter_queryset(self, queryset):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        return self.queryset.filter(comment_id=self.kwargs['comment_id'], post=post)


class BlogSubscribe(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = SubscriptionList
    permission_classes = [permissions.IsAuthenticated]

    def subscribe(self, request, slug):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        user = get_object_or_404(UserProfile, username=request.user)
        user.subscriptions.add(blog)
        return Response('added', status=status.HTTP_200_OK)

    def unsubscribe(self, request, slug):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        user = get_object_or_404(UserProfile, username=request.user)
        user.subscriptions.remove(blog)
        return Response('removed', status=status.HTTP_200_OK)


class SubscriptionList2(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = SubscriptionList
    pagination_class = ListSetPagination
    permission_classes = [permissions.AllowAny]

    def filter_queryset(self, queryset):
        return self.queryset.filter(username=self.kwargs['username'])


class AddLike(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = SubscriptionList
    permission_classes = [permissions.IsAuthenticated]

    def set_like(self, request, slug, post_id):
        user = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        if not post.liked_users.contains(user):
            post.liked_users.add(user)
            post.likes += 1
            post.save(update_fields=("likes",))
            return Response('added', status=status.HTTP_200_OK)
        else:
            return Response('not added', status=status.HTTP_200_OK)

    def remove_like(self, request, slug, post_id):
        user = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        if post.liked_users.contains(user):
            post.liked_users.remove(user)
            post.likes -= 1
            post.save(update_fields=("likes",))
            return Response('removed', status=status.HTTP_200_OK)
        else:
            return Response('already removed', status=status.HTTP_200_OK)
