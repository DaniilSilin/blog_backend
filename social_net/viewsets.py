from django.core.files.storage import FileSystemStorage
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, permissions, viewsets
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Case, When, Value, BooleanField, IntegerField, Sum
from django.http import Http404
from rest_framework.parsers import MultiPartParser, FormParser

from authentication.models import UserProfile
from .models import Blog, Post, Commentary, Tag, Invite
from .serializers import (BlogSerializer, CreateBlogSerializer, UpdateBlogSerializer, PostSerializer, \
                          CreatePostSerializer, CreateCommentarySerializer, SubscriptionList,
                          UpdatePostSerializer, UserProfileSerializer,
                          InviteUserSerializer, InviteListUserSerializer, IsBlogOwnerSerializer,
                          IsBlogAvailableSerializer, InviteGetUsersSerializer, PostCommentaryListSerializer)

class BlogPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            return request.user and request.user.is_authenticated
        else:
            isBlogExistsAndIsUserOwner = Blog.objects.filter(slug=view.kwargs['slug'], owner=request.user.id)
            isAdmin = (request.user and request.user.is_authenticated and request.user.is_admin)
            return bool(isBlogExistsAndIsUserOwner or isAdmin)


class PostPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        isAdmin = (request.user and request.user.is_authenticated and request.user.is_admin)
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            isBlogOwnerOrOneOfAuthors = Blog.objects.filter(Q(slug=view.kwargs['slug']) & (Q(owner=request.user.id) | Q(authors__username__contains=request.user)))
            return bool((isBlogOwnerOrOneOfAuthors or isAdmin) and IsAuthenticated)
        else:
            isPostOwnerOrOneOfAuthors = Post.objects.filter(Q(post_id=view.kwargs['post_id']) & Q(blog__slug=view.kwargs['slug']) & (Q(blog__authors__username__contains=request.user) | Q(blog__owner=request.user.id)))
            return bool((isPostOwnerOrOneOfAuthors or isAdmin) and IsAuthenticated)

    def has_object_permission(self, request, view, obj):
        isAdmin = (request.user and request.user.is_authenticated and request.user.is_admin)
        isBlogOwner = obj.blog.owner == request.user
        isBlogAuthor = obj.blog.authors.filter(username__contains=request.user)
        if request.method in permissions.SAFE_METHODS:
            if bool(obj.is_published):
                return True
            if not (isBlogOwner or isBlogAuthor or isAdmin) and IsAuthenticated:
                raise Http404
        return True


class CommentaryPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        isAdmin = (request.user and request.user.is_authenticated and request.user.is_admin)
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.method == 'POST':
            IsPostAccessibleForComments = Post.objects.filter(post_id=view.kwargs['post_id'], blog__slug=view.kwargs['slug'])
            return bool(IsPostAccessibleForComments and request.user.id and request.user.is_authenticated)
        else:
            isBlogOwnerOrBlogAuthorOrAuthorOfComment = Commentary.objects.filter(Q(comment_id=view.kwargs['comment_id']) & Q(post__post_id=view.kwargs['post_id']) & Q(post__blog__slug=view.kwargs['slug']) & (Q(post__blog__owner=request.user.id) | Q(post__blog__authors__username__contains=request.user) | Q(author=request.user.id)))
            return bool((isBlogOwnerOrBlogAuthorOrAuthorOfComment or isAdmin) and IsAuthenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            isAdmin = (request.user and request.user.is_authenticated and request.user.is_admin)
            IsBlogAuthor = obj.post.blog.authors.filter(username__contains=request.user)
            IsBlogOwner = obj.post.blog.owner == request.user
            if obj.post.is_published:
                return True
            if not ((IsBlogAuthor or IsBlogOwner or isAdmin) and IsAuthenticated):
                raise Http404
        return True

class ListSetPagination(PageNumberPagination):
    page_size = 5

class BlogList(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by('-updated_at')
    serializer_class = BlogSerializer
    pagination_class = ListSetPagination
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        query_dict = {}
        order_array = []

        search = self.request.query_params.get('search', None)
        order = self.request.query_params.get('order', None)
        before = self.request.query_params.get('before', None)
        after = self.request.query_params.get('after', None)

        if search:
            queryset = queryset.filter(Q(title__icontains=search) | Q(description__icontains=search))

        if after:
            query_dict['updated_at__gt'] = after
        if before:
            query_dict['updated_at__lt'] = before

        if order:
            order_array_split = order.split(',')
            list_of_order = ['title_asc', 'title_desc', 'date', '-date']

            for order_query in order_array_split:
                if order_query in list_of_order:
                    if 'title_asc' in order_array_split:
                        order_array += ['title']
                    if 'title_desc' in order_array_split:
                        order_array += ["-title"]
                    if 'date' in order_array_split:
                        order_array += ["updated_at"]
                    if '-date' in order_array_split:
                        order_array += ["-updated_at"]
                else:
                    return Response(status=status.HTTP_200_OK)

        queryset = queryset.filter(**query_dict)
        if len(order_array):
            queryset = queryset.order_by(*order_array)

        paginatedResult = self.paginate_queryset(queryset.distinct())
        queryset = BlogSerializer(paginatedResult, many=True)
        return Response(queryset.data, status=status.HTTP_200_OK)


class BlogPage(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    permission_classes = [BlogPermissions]
    parser_class = (MultiPartParser, FormParser)

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
        blog.authors.clear()
        serializer = UpdateBlogSerializer(instance=blog, data=request.data, partial=True)
        print(serializer)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # instance_serializer = BlogSerializer(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = CreateBlogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        slug = serializer.data['slug']
        description = serializer.data['description']
        avatar = request.FILES.get('avatar', None)
        owner = get_object_or_404(UserProfile, username=request.user)

        blog = Blog(
            title=title,
            slug=slug,
            description=description,
            owner=owner,
            avatar=avatar
        )

        blog.save()
        return Response({ 'status': 'success' }, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        try:
            blog = self.queryset.get(slug=self.kwargs['slug'])
            blog.isSubscribed = blog.subscribers.filter(username=request.user.username).exists()
            blog.subscriberList = blog.subscribers.count()


            serial = BlogSerializer(blog)
            return Response(serial.data)
        except Blog.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class PostList(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True).order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [PostPermissions]

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
            queryset = queryset.filter(Q(title__icontains=search) | Q(author__username__icontains=search))

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

        queryset = queryset.filter(**query_dict)
        if len(order_array):
            queryset = queryset.order_by(*order_array).distinct()
        result = queryset.annotate(
            isLiked=Case(
                When(liked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )
        paginatedResult = self.paginate_queryset(result)
        serial = PostSerializer(paginatedResult, many=True)
        return Response(serial.data, status=status.HTTP_200_OK)


class MyPosts(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(author=request.user)
        # paginatedResult = self.paginate_queryset(queryset)
        serializer = PostSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BlogPosts(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True).order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset

        sorting = self.request.query_params.get('sorting', None)
        if sorting:
            if sorting == 'newest':
                queryset = queryset.order_by('-created_at')
            if sorting == 'oldest':
                queryset = queryset.order_by('created_at')

        queryset = queryset.filter(blog__slug=self.kwargs['slug']).distinct().annotate(
            commentCount=Count('comment'),
            likedUsersCount=Count('liked_users'),
            isLiked=Case(
                When(liked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
        paginatedResult = self.paginate_queryset(queryset)
        if paginatedResult is not None:
            serializer = PostSerializer(paginatedResult, many=True)
            result = self.get_paginated_response(serializer.data)
        return Response(result.data, status=status.HTTP_200_OK)


class PostPage(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    permission_classes = [PostPermissions]
    parser_class = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return CreatePostSerializer
        return PostSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
            post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)

            post.isSubscribed = blog.subscribers.filter(username=request.user.username).exists()
            post.isLiked = request.user in post.liked_users.all()
            post.commentCount = post.comment.count()
            post.subscribers = post.blog.subscribers.count()

            serial = PostSerializer(post)
            post.views += 1
            post.save(update_fields=("views",))
            return Response(serial.data)
        except Post.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        post.delete()
        return Response(status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        request.data._mutable = True
        request.data['is_published'] = request.data.get('is_published', 'false')
        post.tags.clear()
        request.data._mutable = False
        serializer = UpdatePostSerializer(instance=post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serial = PostSerializer(serializer, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = CreatePostSerializer(data=request.data)
        print(serializer)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        body = serializer.data['body']
        is_published = serializer.data['is_published']
        author = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        tags = serializer.data['tags']
        blog.count_of_posts += 1
        blog.save(update_fields=("count_of_posts",))
        post_id = blog.count_of_posts

        fs = FileSystemStorage()
        images = request.FILES.get('images')
        image = request.FILES.get('images')
        print(images)
        # for image in images:
        post = Post(
            images=images,
            title=title,
            body=body,
            is_published=is_published,
            author=author,
            blog=blog,
            post_id=post_id,
            tags=tags,
        )

        # post = Post(
        #     title=title,
        #     body=body,
        #     is_published=is_published,
        #     author=author,
        #     blog=blog,
        #     post_id=post_id,
        #     tags=tags,
        #     images=images
        # )

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
        reply_to=serializer.data['reply_to_1'] or None
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        comment = get_object_or_404(Commentary, comment_id=reply_to, post__post_id=self.kwargs['post_id'], post__blog=blog)
        blog.count_of_commentaries += 1
        blog.save(update_fields=("count_of_commentaries",))
        comment_id = blog.count_of_commentaries

        comm = Commentary(
            body=body,
            author=request.user,
            post=post,
            comment_id=comment_id,
            reply_to=comment
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

    def retrieve(self, request, *args, **kwargs):
        try:
            blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
            post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
            serial = CommentarySerializer(self.queryset.get(comment_id=self.kwargs['comment_id'], post=post))
            return Response(serial.data)
        except Commentary.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)


class BlogSubscribe(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = SubscriptionList
    permission_classes = [permissions.IsAuthenticated]

    def subscribe(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)
        user = get_object_or_404(UserProfile, username=request.user)
        user.subscriptions.add(blog)
        return Response({ 'status': 'success' }, status=status.HTTP_200_OK)

    def unsubscribe(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)
        user = get_object_or_404(UserProfile, username=request.user)
        user.subscriptions.remove(blog)
        return Response({ 'status': 'success' }, status=status.HTTP_200_OK)


class SubscriptionListViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = SubscriptionList
    # pagination_class = ListSetPagination
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=self.kwargs['username'])
        queryset = self.queryset.filter(username=user)
        if user:
            result = SubscriptionList(queryset, many=True)
            return Response(result.data, status=status.HTTP_200_OK)

class LikeViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = SubscriptionList
    permission_classes = [permissions.IsAuthenticated]

    def add_like(self, request, slug, post_id):
        user = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        if not post.liked_users.contains(user):
            post.liked_users.add(user)
            post.likes += 1
            post.save(update_fields=("likes",))
            return Response({'status': 'success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_200_OK)

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


class InvitationView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = InviteUserSerializer

    def send_invite(self, request):
        serializer = InviteUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        admin = get_object_or_404(UserProfile, pk=serializer.data['admin'])
        description = serializer.data['description']
        addressee = get_object_or_404(UserProfile, username=serializer.data['addressee'])
        blog = get_object_or_404(Blog, slug=serializer.data['blog'])

        invite = Invite(
            admin=admin,
            description=description,
            addressee=addressee,
            blog=blog
        )

        invite.save()
        serial = InviteUserSerializer(invite, many=False)
        return Response(serial.data, status=status.HTTP_200_OK)


class InviteListView(viewsets.ModelViewSet):
    queryset = Invite.objects.all()
    serializer_class = InviteListUserSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(addressee=request.user)
        result = InviteListUserSerializer(queryset, many=True)
        return Response(result.data, status=status.HTTP_200_OK)


class InviteReactView(viewsets.ModelViewSet):
    queryset = Invite.objects.all()
    serializer_class = InviteUserSerializer
    permission_classes = [IsAuthenticated]

    def accept_invite(self, request, pk):
        invite = get_object_or_404(Invite, pk=self.kwargs['pk'])
        if invite.addressee == request.user and invite.status is None:
            invite.blog.authors.add(invite.addressee)
            invite.status = True
            invite.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

    def reject_invite(self, request):
        invite = get_object_or_404(Invite, pk=self.kwargs['pk'])
        if invite.addressee == request.user and invite.status is None:
            invite.status = False
            invite.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

class LeaveBlogView(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated]

    def leave_blog(self, request):
        blog = get_object_or_404(Blog, blog=self.kwargs['slug'])
        if blog.authors.filter(username=request.user.username).exists():
            blog.authors.remove(user=request.user)
            return Response(status.HTTP_200_OK)
        else:
            return Response(status.HTTP_403_FORBIDDEN)

class KickUserView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [IsAuthenticated]

    def kick_user(self, slug, username):
        blog = get_object_or_404(Blog, slug=slug)
        user = get_object_or_404(UserProfile, username=username)
        blog.authors.remove(user)
        return Response({ "status": "success" }, status=status.HTTP_200_OK)

class IsBlogOwner(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = IsBlogOwnerSerializer
    permission_classes = [IsAuthenticated]

    def is_blog_owner(self, request):
        queryset = self.queryset.filter(owner=request.user)
        result = IsBlogOwnerSerializer(queryset, many=True)
        return Response(result.data, status=status.HTTP_200_OK)

class IsSlugAvailable(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = IsBlogAvailableSerializer

    def is_slug_available(self, request, slug):
        blog = self.queryset.filter(slug=slug).exists()
        if blog:
            return Response('Slug недоступен', status=status.HTTP_200_OK)
        else:
            return Response('Slug доступен', status=status.HTTP_200_OK)


class InviteGetUsers(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = InviteGetUsersSerializer
    pagination_class = ListSetPagination

    def get_users(self, request, username):
        user_list = self.queryset.filter(username__contains=username)
        if user_list:
            paginatedResult = self.paginate_queryset(user_list.distinct())
            serializer = InviteGetUsersSerializer(paginatedResult, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        # elif username == '':
        #     paginatedResult = self.paginate_queryset(self.queryset.order_by('?'))
        #     serializer = InviteGetUsersSerializer(paginatedResult, many=True)
        #     return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            paginatedResult = self.paginate_queryset(self.queryset.order_by('?'))
            serializer = InviteGetUsersSerializer(paginatedResult, context={"request": request}, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class Subscriptions(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = SubscriptionList
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter()
        blog = queryset.filter(username=request.user.username)
        serializer = SubscriptionList(blog, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserProfileView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        user_exists = self.queryset.filter(username=self.kwargs['username']).exists()
        if user_exists:
            queryset = self.queryset.filter(username=self.kwargs['username'])
            alex = queryset.annotate(
                is_request_user=Case(When(username=request.user.username, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                )
            )
            serializer = UserProfileSerializer(alex, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({ "status": "unsuccessful" }, status=status.HTTP_404_NOT_FOUND)

class ChangeUserProfileView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

    def update(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=self.kwargs['username'])
        avatar = request.FILES.get('image', None)
        serializer = UserProfileSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

class PostSearchView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [PostPermissions]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        hashtag = self.request.query_params.get('hashtag', None)

        if hashtag:
            queryset = self.queryset.filter(tags__icontains=hashtag)

        paginatedResult = self.paginate_queryset(queryset.distinct())
        queryset = PostSerializer(paginatedResult, many=True)
        return Response(queryset.data, status=status.HTTP_200_OK)

class BlogCommentsView(viewsets.ModelViewSet):
    queryset = Commentary.objects.filter(reply_to=None)
    serializer_class = PostCommentaryListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset

        sortBy = self.request.query_params.get('sortBy', None)
        if sortBy:
            if sortBy == 'newest':
                queryset = queryset.filter().order_by('-created_at')
            if sortBy == 'oldest':
                queryset = queryset.filter().order_by('created_at')

        queryset = queryset.filter(post__blog__slug=self.kwargs['slug'], post__post_id=self.kwargs['post_id'])
        paginatedResult = self.paginate_queryset(queryset)
        if paginatedResult is not None:
            serializer = PostCommentaryListSerializer(paginatedResult, many=True)
            result = self.get_paginated_response(serializer.data)
        return Response(result.data, status=status.HTTP_200_OK)


class PostCommentReplyList(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = PostCommentaryListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, blog=blog, blog__slug=self.kwargs['slug'])
        print(blog)
        print(post)
        comment = get_object_or_404(Commentary, comment_id=self.kwargs['comment_id'], post=post, post__blog=blog)
        alex = self.queryset.filter(comment_id=comment.comment_id).order_by('-created_at')
        print(alex)
        serializer = PostCommentaryListSerializer(alex, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BlogPublicationsView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        state = self.request.query_params.get('state', None)

        if state == 'published':
            queryset = queryset.filter(published=True)
            paginatedResult = self.paginate_queryset(queryset.distinct())
            serializer = PostSerializer(paginatedResult, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if state == 'pending':
            queryset = queryset.filter(published=False)
            paginatedResult = self.paginate_queryset(queryset.distinct())
            serializer = PostSerializer(paginatedResult, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
