from django.db.models.functions import Coalesce
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status, permissions, viewsets
from django.shortcuts import get_object_or_404
from django.db.models import Q, Count, Case, When, Value, BooleanField, Sum, Exists, OuterRef
from django.http import Http404
from rest_framework.parsers import MultiPartParser, FormParser
import re

from authentication.models import UserProfile
from .models import Blog, Post, Commentary, Invite, Notification, PostImage
from .serializers import (BlogSerializer, CreateBlogSerializer, UpdateBlogSerializer, PostSerializer, \
                          CreatePostSerializer, CreateCommentarySerializer, SubscriptionList,
                          UpdatePostSerializer, UserProfileSerializer, BlogCommentListSerializer,
                          InviteUserSerializer, InviteListUserSerializer, IsBlogOwnerSerializer,
                          IsBlogAvailableSerializer, InviteGetUsersSerializer, PostCommentaryListSerializer,
                          BookmarkListSerializer, BookmarkSerializer, UserSerializer, ChangeAvatarSerializer,
                          SubscriptionListMiniSerializer, BlogMiniListSerializer, BlogCommentListDeleteSerializer,
                          UpdateUserProfileSerializer, UserNotificationsSerializer, PostCommentarySerializer, BlogDeletePostsSerializer,
                          UpdateCommentarySerializer)


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
        isAdmin = (IsAuthenticated and request.user.is_admin)
        isBlogOwner = (IsAuthenticated and obj.post.blog.owner == request.user)
        isBlogAuthor = (IsAuthenticated and obj.post.blog.authors.filter(username__contains=request.user))
        isUserCommentAuthor = (IsAuthenticated and obj.author == request.user)
        if request.method in permissions.SAFE_METHODS:
            if obj.post.is_published:
                return True
            if not ((isBlogAuthor or isBlogOwner or isAdmin) and IsAuthenticated):
                raise Http404
        if request.method == "DELETE":
            return bool(isUserCommentAuthor or isAdmin or isBlogOwner)
        if request.method == "PUT":
            return bool(isUserCommentAuthor or isAdmin)


class ListSetPagination(PageNumberPagination):
    page_size = 5

class BlogListPagination(PageNumberPagination):
    page_size = 10

class ListSetPaginationSecond(PageNumberPagination):
    page_size = 2

class BlogList(viewsets.ModelViewSet):
    queryset = Blog.objects.all().order_by('-updated_at')
    serializer_class = BlogMiniListSerializer
    pagination_class = ListSetPagination
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        query_dict = {}

        search = self.request.query_params.get('search', None)
        sorting = self.request.query_params.get('sorting', None)
        before = self.request.query_params.get('before', None)
        after = self.request.query_params.get('after', None)

        if search:
            queryset = queryset.filter(title__icontains=search)

        if after:
            query_dict['updated_at__gt'] = after
        if before:
            query_dict['updated_at__lt'] = before

        if sorting:
            if sorting == 'date':
                queryset = queryset.order_by('updated_at')
            if sorting == '-date':
                queryset = queryset.order_by('-updated_at')
            if sorting == 'title_asc':
                queryset = queryset.order_by('title')
            if sorting == 'title_desc':
                queryset = queryset.order_by('-title')

        queryset = queryset.filter(**query_dict)

        if request.user.is_authenticated:
            queryset = queryset.annotate(
                subscriberList=Count('subscribers'),
                views=Coalesce(Sum('posts__views'), 0),
                isSubscribed=Case(
                    When(subscribers=request.user, then=Value(True)),
                      default=Value(False),
                      output_field=BooleanField(),
                ),
                # isBlogAuthor=Exists(is_author_subquery)
            )
        else:
            queryset = queryset.annotate(
                subscriberList=Count('subscribers'),
                views=Coalesce(Sum('posts__views'), 0),
                isSubscribed=Value(False, output_field=BooleanField()),
            )

        paginated_result = self.paginate_queryset(queryset)
        if paginated_result is not None:
            serializer = self.serializer_class(paginated_result, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


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

    def create(self, request, *args, **kwargs):
        serializer = CreateBlogSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(serializer.data)
        title = serializer.data['title']
        slug = serializer.data['slug']
        description = serializer.validated_data.get('description', '')
        avatar = request.FILES.get('avatar', None)
        avatar_small = request.FILES.get('avatar_small', None)
        owner = get_object_or_404(UserProfile, username=request.user)

        blog = Blog(
            title=title,
            slug=slug,
            description=description,
            owner=owner,
            avatar=avatar,
            avatar_small=avatar_small
        )

        blog.save()
        return Response({'status': 'successful'}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        try:
            blog = self.queryset.get(slug=self.kwargs['slug'])
            blog.isSubscribed = blog.subscribers.filter(username=request.user.username).exists()
            blog.subscriberList = blog.subscribers.count()
            blog.views = blog.posts.aggregate(views=Sum('views'))['views'] or 0
            serial = BlogSerializer(blog)
            return Response(serial.data)
        except Blog.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        serializer = UpdateBlogSerializer(instance=blog, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'successful'}, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        blog.delete()
        return Response({'status: successful'}, status=status.HTTP_200_OK)


class PostList(viewsets.ModelViewSet):
    queryset = Post.objects.filter(is_published=True).order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        query_dict = {}

        before = self.request.query_params.get('before', None)
        after = self.request.query_params.get('after', None)
        search = self.request.query_params.get('search', None)
        sort_by = self.request.query_params.get('sort_by', None)

        if after:
            query_dict['created_at__gte'] = after
        if before:
            query_dict['created_at__lte'] = before

        if search:
            queryset = queryset.filter(Q(title__icontains=search))

        if sort_by:
            if sort_by == 'date':
                queryset = queryset.order_by('-created_at')
            if sort_by == '-date':
                queryset = queryset.order_by('created_at')
            if sort_by == 'title_asc':
                queryset = queryset.order_by('title')
            if sort_by == 'title_desc':
                queryset = queryset.order_by('-title')

        queryset = queryset.filter(**query_dict)

        if request.user.is_authenticated:
            queryset = queryset.annotate(
                isLiked=Exists(
                    Post.objects.filter(liked_users=request.user, id=OuterRef('pk'))
                ),
                isDisliked=Exists(
                    Post.objects.filter(disliked_users=request.user, id=OuterRef('pk'))
                ),
                isBookmarked=Exists(
                    UserProfile.objects.filter(bookmarks=OuterRef('pk'), id=request.user.id)
                ),
                comments=Count('comment')
            )
        else:
            queryset = queryset.annotate(
                isLiked=Value(False, output_field=BooleanField()),
                isDisliked=Value(False, output_field=BooleanField()),
                isBookmarked=Value(False, output_field=BooleanField()),
                comments=Count('comment')
            )

        paginated_result = self.paginate_queryset(queryset)
        if paginated_result is not None:
            serializer = self.serializer_class(paginated_result, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class MyPosts(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(author=request.user)
        queryset = queryset.annotate(
            isLiked=Case(
                When(liked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            comments=Count('comment')
        )
        paginated_result = self.paginate_queryset(queryset)
        if paginated_result is not None:
            serializer = self.serializer_class(paginated_result, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class BlogPosts(viewsets.ModelViewSet):
    queryset = Post.objects.filter().order_by('-created_at')
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        # pinned_post = get_object_or_404(Post, blog__slug=self.kwargs['slug'])
        # queryset = queryset.exclude(id=pinned_post.id)

        sorting = self.request.query_params.get('sorting', None)
        search = self.request.query_params.get('search', None)
        if sorting:
            if sorting == 'newest':
                queryset = queryset.order_by('-created_at')
            if sorting == 'oldest':
                queryset = queryset.order_by('created_at')
            if sorting == 'title_asc':
                queryset = queryset.order_by('title')
            if sorting == 'title_desc':
                queryset = queryset.order_by('-title')

        if search:
            queryset = queryset.filter(title__icontains=search)

        queryset = queryset.filter(blog__slug=self.kwargs['slug']).distinct().annotate(
            commentCount=Count('comment'),
            likedUsersCount=Count('liked_users'),
            isLiked=Case(
                When(liked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            isDisliked=Case(
                When(disliked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            isBookmarked=Case(
                When(bookmarks=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )
        paginated_result = self.paginate_queryset(queryset)
        if paginated_result is not None:
            serializer = self.serializer_class(paginated_result, many=True)
            result = self.get_paginated_response(serializer.data)
        return Response(result.data, status=status.HTTP_200_OK)


class PostPage(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    parser_class = (MultiPartParser, FormParser)
    permission_classes = [PostPermissions]

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PUT':
            return CreatePostSerializer
        return PostSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
            post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
            post_images = post.images.all()

            post.isSubscribed = blog.subscribers.filter(username=request.user.username).exists()
            post.isLiked = request.user in post.liked_users.all()
            post.isDisliked = request.user in post.disliked_users.all()
            post.isBookmarked = request.user in post.bookmarks.all()

            post.commentCount = post.comment.count()
            post.subscribers = post.blog.subscribers.count()

            post.images1 = post_images

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
        return Response({ 'status: success' }, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        serializer = UpdatePostSerializer(instance=post, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serial = PostSerializer(serializer, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = CreatePostSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        title = serializer.data['title']
        body = serializer.data['body']
        is_published = serializer.data['is_published']
        author = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        tags = serializer.data['tags']
        map_type = serializer.data['map_type']
        map_1 = serializer.data['map']
        author_is_hidden = serializer.data['author_is_hidden']
        comments_allowed = serializer.data['comments_allowed']
        images = request.FILES.getlist('images')
        blog.count_of_posts += 1
        blog.save(update_fields=("count_of_posts",))
        post_id = blog.count_of_posts

        post = Post(
            title=title,
            body=body,
            map_type=map_type,
            map=map_1,
            is_published=is_published,
            author_is_hidden=author_is_hidden,
            comments_allowed=comments_allowed,
            author=author,
            blog=blog,
            post_id=post_id,
            tags=tags,
        )
        print(post)
        post.save()

        for image in images:
            post_image = PostImage(
                post=post,
                image=image
            )
            post_image.save()

        post_serializer = PostSerializer(post)
        return Response(data=post_serializer.data, status=status.HTTP_201_CREATED)


class BlogSubscription(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def toggle_subscription(self, request, slug):
        blog = get_object_or_404(Blog, slug=slug)
        user = get_object_or_404(UserProfile, username=request.user)
        if user.subscriptions.filter(slug=slug).exists():
            user.subscriptions.remove(blog)
            return Response({'status': 'successful'}, status=status.HTTP_200_OK)
        else:
            user.subscriptions.add(blog)
            return Response({'status': 'successful'}, status=status.HTTP_200_OK)


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

class PostLikeDislikeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def set_or_remove_like(self, request, slug, post_id):
        user = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        if post.disliked_users.contains(user):
            post.disliked_users.remove(user)
            post.dislikes -= 1
        if not post.liked_users.contains(user):
            post.liked_users.add(user)
            post.likes += 1
        else:
            post.liked_users.remove(user)
            post.likes -= 1
        post.save(update_fields=("likes", "dislikes"))
        return Response({'status': 'successful'}, status=status.HTTP_200_OK)

    def set_or_remove_dislike(self, request, slug, post_id):
        user = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        if post.liked_users.contains(user):
            post.liked_users.remove(user)
            post.likes -= 1
        if not post.disliked_users.contains(user):
            post.disliked_users.add(user)
            post.dislikes += 1
        else:
            post.disliked_users.remove(user)
            post.dislikes -= 1
        post.save(update_fields=("likes", "dislikes"))
        return Response({'status': 'successful'}, status=status.HTTP_200_OK)


class InvitationCreateView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = InviteUserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
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
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(addressee=request.user).order_by('status')
        paginated_result = self.paginate_queryset(queryset)
        if paginated_result is not None:
            serializer = self.serializer_class(paginated_result, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_200_OK)

class InvitationView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def accept_invite(self, request, pk):
        invite = get_object_or_404(Invite, pk=pk)
        if invite.addressee == request.user and invite.status is None:
            invite.blog.authors.add(invite.addressee)
            invite.status = True
            invite.save()
            return Response({'status': 'successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_403_FORBIDDEN)

    def reject_invite(self, request, pk):
        invite = get_object_or_404(Invite, pk=pk)
        if invite.addressee == request.user and invite.status is None:
            invite.status = False
            invite.save()
            return Response({'status': 'successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_403_FORBIDDEN)

class LeaveBlogView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def leave_blog(self, request, slug):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        user = get_object_or_404(UserProfile, username=request.user)
        if blog.authors.filter(username__contains=user.username).exists():
            blog.authors.remove(user)
            return Response({'status': 'successful'}, status.HTTP_200_OK)
        else:
            return Response(status.HTTP_403_FORBIDDEN)


class KickUserView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def kick_user(self, request, slug, username):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        user = get_object_or_404(UserProfile, username=self.kwargs['username'])
        blog.authors.remove(user)
        return Response({"status": "success"}, status=status.HTTP_200_OK)

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
    permission_classes = [AllowAny]

    def is_slug_available(self, request, slug):
        slug_exists = self.queryset.filter(slug=slug).exists()
        if slug_exists:
            return Response('Этот адрес уже занят', status=status.HTTP_200_OK)
        else:
            return Response('Адрес свободен', status=status.HTTP_200_OK)


class InviteGetUsers(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = InviteGetUsersSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset

        query = self.request.query_params.get('query', None)

        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        pending_invites = Invite.objects.filter(blog=blog, status=None).values_list('addressee__username', flat=True)
        current_blog_authors = blog.authors.values_list('username', flat=True)
        blog_owner_username = UserProfile.objects.filter(username=blog.owner.username).values_list('username', flat=True)

        excluded_usernames = set(pending_invites) | set(current_blog_authors) | set(blog_owner_username)
        print(excluded_usernames)

        queryset = queryset.exclude(username__in=excluded_usernames)
        if query:
            user_list = queryset.filter(username__icontains=query)[:5]
            if user_list:
                serializer = self.serializer_class(user_list, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user_list = queryset.order_by('?')[:5]
            if user_list:
                serializer = self.serializer_class(user_list, many=True)
                return Response(data=serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class UserProfileView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UpdateUserProfileSerializer
        if self.request.method == 'PUT':
            return UpdateUserProfileSerializer
        return UpdateUserProfileSerializer

    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.queryset.get(username=self.kwargs['username'])

            user.subscriptionList = user.subscriptions.count()
            serial = UpdateUserProfileSerializer(user)
            return Response(serial.data)
        except UserProfile.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=self.kwargs['username'])
        serializer = UpdateUserProfileSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'successful'}, status=status.HTTP_200_OK)


class PostSearchView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [PostPermissions]
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset

        result = queryset.filter(tags__icontains=self.kwargs['hashtag'])

        count_of_posts = queryset.filter(tags__icontains=self.kwargs['hashtag']).count()
        count_of_blogs = Blog.objects.filter(posts__tags__icontains=self.kwargs['hashtag']).count()

        queryset = result.annotate(
            isLiked=Case(
                When(liked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            isDisliked=Case(
                When(disliked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            isBookmarked=Case(
                When(bookmarks=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            comments=Count('comment'),
        )

        if queryset is not None:
            paginate_queryset = self.paginate_queryset(queryset)
            serializer = self.serializer_class(paginate_queryset, many=True)

            tmp = serializer.data
            response = self.get_paginated_response(tmp)
            response.data['count_of_blogs'] = count_of_blogs
            response.data['count_of_posts'] = count_of_posts
            response.data.move_to_end('results')
            return Response(data=response.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


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


class BookmarkView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def add_or_remove_bookmark(self, request, slug, post_id):
        post = get_object_or_404(Post, blog__slug=self.kwargs['slug'], post_id=self.kwargs['post_id'])
        user = get_object_or_404(UserProfile, username=request.user.username)
        if user.bookmarks.contains(post):
            user.bookmarks.remove(post)
        else:
            user.bookmarks.add(post)
        return Response({'status: successful'}, status=status.HTTP_200_OK)

class PinPostViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def pin_post(self, request, slug, post_id):
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        if not post.is_pinned:
            post.is_pinned = True
            post.save(update_fields=("is_pinned",))
            return Response({'status: success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status: unsuccessful'}, status=status.HTTP_404_NOT_FOUND)

    def unpin_post(self, request, slug, post_id):
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        if post.is_pinned:
            post.is_pinned = False
            post.save(update_fields=("is_pinned",))
            return Response({'status: success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status: unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class PinCommentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def pin_comment(self, request, slug, post_id, comment_id):
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        user = get_object_or_404(UserProfile, username=request.user.username)
        comment = get_object_or_404(Commentary, comment_id=comment_id, post=post)
        if comment.reply_to is None and comment.is_pinned == False:
            pinned_comment = Commentary.objects.filter(post=post, is_pinned=True, reply_to=None)
            if pinned_comment:
                pinned_comment.is_pinned = False
                pinned_comment.save(update_fields=("is_pinned", "pinned_by_user",))
            comment.is_pinned = True
            comment.pinned_by_user = user
            comment.save(update_fields=("is_pinned", "pinned_by_user",))
            return Response({'status: success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status: unsuccessful'}, status=status.HTTP_400_BAD_REQUEST)


    def unpin_comment(self, request, slug, post_id, comment_id):
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        comment = get_object_or_404(Commentary, comment_id=comment_id, post=post)
        if comment.reply_to is None and comment.is_pinned == True:
            comment.is_pinned = False
            comment.pinned_by_user = None
            comment.save(update_fields=("is_pinned", "pinned_by_user",))
            return Response({'status: success'}, status=status.HTTP_200_OK)
        else:
            return Response({'status: unsuccessful'}, status=status.HTTP_400_BAD_REQUEST)


class LikedUserList(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = UserProfileSerializer
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        queryset = self.queryset.filter(alex=post)
        paginatedResult = self.paginate_queryset(queryset)
        if paginatedResult is not None:
            serializer = UserSerializer(paginatedResult, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


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
        reply_to = serializer.data['reply_to']
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        if reply_to:
            parent_comment = get_object_or_404(Commentary, comment_id=reply_to, post=post)
        blog.count_of_commentaries += 1
        blog.save(update_fields=("count_of_commentaries",))
        comment_id = blog.count_of_commentaries

        if reply_to:
            print(reply_to)
            commentary = get_object_or_404(Commentary, comment_id=reply_to, post=post)
            # print(commentary)
            comm = Commentary(
                body=body,
                author=request.user,
                post=post,
                comment_id=comment_id,
                reply_to=commentary
            )
        else:
            comm = Commentary(
                body=body,
                author=request.user,
                post=post,
                comment_id=comment_id,
            )
        comm.save()

        addressee_regex = r'@\w+'
        addressees = re.findall(addressee_regex, body)
        new_addressees = ' '.join(addressees).split('@')

        for addressee in new_addressees:
            print(addressee)
            message = f'Пользователь {addressee} оставил комментарий "{body}"'
            if UserProfile.objects.filter(username=addressee).exists():
                user = UserProfile.objects.get(username=addressee)
                notification = Notification(
                    parent_comment=parent_comment,
                    replied_comment=comm,
                    post=post,
                    text=message,
                    addressee=user,
                    author=request.user,
                    is_read=False,
                )
                notification.save()

        serial = PostCommentarySerializer(comm, many=False)
        return Response(serial.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        comment = get_object_or_404(Commentary, comment_id=self.kwargs['comment_id'], post=post)
        comment.is_edited = True
        serializer = CreateCommentarySerializer(instance=comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status: successful'}, status=status.HTTP_200_OK)

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


class PostCommentNotificationView(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = PostCommentaryListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(post__blog__slug=self.kwargs['slug'], post__post_id=self.kwargs['post_id'])

        comment_reply = self.request.query_params.get('comment_reply', None)
        parent_id = self.request.query_params.get('parent_id', None)

        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)
        # comment = get_object_or_404(Commentary, comment_id=comment_reply, post=post)

        if parent_id:
            model = Commentary.objects.get(comment_id=parent_id)
            queryset = queryset.filter(reply_to=model)
        else:
            queryset = queryset.filter(reply_to=None)

        queryset = queryset.annotate(
            isLiked=Case(
                When(liked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            isDisliked=Case(
                When(disliked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            )
        )

        paginate_queryset = self.paginate_queryset(queryset)
        serializer = self.serializer_class(paginate_queryset, many=True)
        response = self.get_paginated_response(serializer.data)
        return Response(data=response.data, status=status.HTTP_200_OK)


class PostCommentListView(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = PostCommentaryListSerializer
    permission_classes = [AllowAny]
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(post__blog__slug=self.kwargs['slug'], post__post_id=self.kwargs['post_id'])
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        post = get_object_or_404(Post, post_id=self.kwargs['post_id'], blog=blog)

        parent_id = self.request.query_params.get('parent_id', None)
        sort_by = self.request.query_params.get('sort_by', None)

        if sort_by:
            if sort_by == 'newest':
                queryset = queryset.order_by('-is_pinned', '-created_at')
            if sort_by == 'oldest':
                queryset = queryset.order_by('-is_pinned', 'created_at')

        if parent_id:
            model = Commentary.objects.get(comment_id=parent_id, post=post, post__blog=blog)
            queryset = queryset.filter(reply_to=model)
        else:
            queryset = queryset.filter(reply_to=None)

        if request.user.is_authenticated:
            queryset = queryset.annotate(
                isLiked=Case(
                    When(liked_users=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
                isDisliked=Case(
                    When(disliked_users=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
        else:
            queryset = queryset.annotate(
                isLiked=Value(False, output_field=BooleanField()),
                isDisliked=Value(False, output_field=BooleanField()),
            )

        paginate_queryset = self.paginate_queryset(queryset)
        serializer = self.serializer_class(paginate_queryset, many=True)
        response = self.get_paginated_response(serializer.data)
        return Response(data=response.data, status=status.HTTP_200_OK)


class ChangeAvatarView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = ChangeAvatarSerializer
    parser_class = (MultiPartParser, FormParser)

    def update(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=self.kwargs['username'])
        serializer = ChangeAvatarSerializer(instance=user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'status': 'success'}, status=status.HTTP_200_OK)

class DeleteAvatarView(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()

    # def destroy(self, request, *args, **kwargs):
    #     user = get_object_or_404(UserProfile, username=self.kwargs['username'])

class BlogEditorPostsView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [permissions.AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset

        queryset = queryset.annotate(
            isLiked=Case(
                When(liked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            isDisliked=Case(
                When(disliked_users=request.user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField(),
            ),
            comments=Count('comment')
        )

        title = self.request.query_params.get('title', None)
        state = self.request.query_params.get('state', None)
        column_type = self.request.query_params.get('columnType', None)
        sort_order = self.request.query_params.get('sortOrder', None)

        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        count_of_published_posts = queryset.filter(blog=blog, is_published=True).count()
        const_of_drafted_posts = queryset.filter(blog=blog, is_published=False).count()

        if state:
            if state == 'published' or state == 'undefined':
                queryset = queryset.filter(blog=blog, is_published=True)
            if state == 'draft':
                queryset = queryset.filter(blog=blog, is_published=False)
        else:
            queryset = queryset.filter(blog=blog, is_published=True)

        if title:
            queryset = queryset.filter(title__icontains=title)

        if column_type and sort_order:
            if column_type == 'date':
                if sort_order == 'ascending':
                    queryset = queryset.order_by('created_at')
                if sort_order == 'descending':
                    queryset = queryset.order_by('-created_at')
            if column_type == 'views':
                if sort_order == 'ascending':
                    queryset = queryset.order_by('views')
                if sort_order == 'descending':
                    queryset = queryset.order_by('-views')
            if column_type == 'comments':
                if sort_order == 'ascending':
                    queryset = queryset.order_by('comments')
                if sort_order == 'descending':
                    queryset = queryset.order_by('-comments')

        if queryset is not None:
            paginate_queryset = self.paginate_queryset(queryset)
            serializer = self.serializer_class(paginate_queryset, many=True)

            tmp = serializer.data
            response = self.get_paginated_response(tmp)
            response.data['count_of_published_posts'] = count_of_published_posts
            response.data['const_of_drafted_posts'] = const_of_drafted_posts
            # response.data.move_to_end('results')
            return Response(data=response.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class BlogsWhereUserIsOwner(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=request.user.username)
        blogs_where_user_is_owner = self.queryset.filter(owner=user)

        paginatedResult = self.paginate_queryset(blogs_where_user_is_owner)
        if paginatedResult is not None:
            serializer = self.serializer_class(paginatedResult, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class BlogsWhereUserIsAuthor(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = BlogSerializer
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=request.user.username)
        blogs_where_user_is_author = self.queryset.filter(authors=user)

        paginatedResult = self.paginate_queryset(blogs_where_user_is_author)
        if paginatedResult is not None:
            serializer = self.serializer_class(paginatedResult, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class BlogInvitationListView(viewsets.ModelViewSet):
    serializer_class = InviteListUserSerializer
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        blog_invitations = blog.invites.all()
        paginated_result = self.paginate_queryset(blog_invitations)
        if paginated_result is not None:
            serializer = self.serializer_class(paginated_result, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(result.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class BlogComments(viewsets.ModelViewSet):
    queryset = Commentary.objects.all()
    serializer_class = BlogCommentListSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        queryset = queryset.filter(post__blog=blog)

        parent_id = self.request.query_params.get('parent_id', None)
        sort_by = self.request.query_params.get('sort_by', None)
        search_query = self.request.query_params.get('search_query', None)

        if sort_by:
            if sort_by == 'newest':
                queryset = queryset.order_by('-created_at')
            if sort_by == 'oldest':
                queryset = queryset.order_by('created_at')

        if search_query:
            queryset = queryset.filter(Q(title__icontains=search_query))

        if parent_id:
            pass
            model = Commentary.objects.get(comment_id=parent_id)
            queryset = queryset.filter(reply_to=model)
        else:
            queryset = queryset.filter(reply_to=None)

        if queryset is not None:
            queryset = queryset.annotate(
                isLiked=Case(
                    When(liked_users=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                ),
                isDisliked=Case(
                    When(disliked_users=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField(),
                )
            )
            paginate_queryset = self.paginate_queryset(queryset)
            serializer = self.serializer_class(paginate_queryset, many=True)
            response = self.get_paginated_response(serializer.data)
            return Response(data=response.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class LikedPostListView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        query_dict = {}

        before = self.request.query_params.get('before', None)
        after = self.request.query_params.get('after', None)
        search = self.request.query_params.get('search', None)
        sort_by = self.request.query_params.get('sort_by', None)

        if after:
            query_dict['created_at__gte'] = after
        if before:
            query_dict['created_at__lte'] = before

        if search:
            queryset = queryset.filter(Q(title__icontains=search))

        if sort_by:
            if sort_by == 'date':
                queryset = queryset.order_by('-created_at')
            if sort_by == '-date':
                queryset = queryset.order_by('created_at')
            if sort_by == 'title_asc':
                queryset = queryset.order_by('title')
            if sort_by == 'title_desc':
                queryset = queryset.order_by('-title')

        queryset = queryset.filter(**query_dict)

        user = get_object_or_404(UserProfile, username=request.user)
        if user:
            queryset = queryset.filter(liked_users=user)
            result = queryset.annotate(
                isLiked=Case(
                    When(liked_users=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                isDisliked=Case(
                    When(disliked_users=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                isBookmarked=Case(
                    When(bookmarks=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                comments=Count('comment'),
            )
            paginate_queryset = self.paginate_queryset(result)
            if paginate_queryset:
                serializer = self.serializer_class(paginate_queryset, many=True)
                result = self.get_paginated_response(serializer.data)
                return Response(data=result.data, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_200_OK)


class SubscriptionListView(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = PostSerializer
    pagination_class = BlogListPagination
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=request.user)
        blog_slug_list = self.queryset.filter(subscribers=user).values_list('slug')
        post_list = Post.objects.filter(blog__slug__in=blog_slug_list).order_by('-created_at')

        if user:
            result = post_list.annotate(
                isLiked=Case(
                    When(liked_users=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                isDisliked=Case(
                    When(disliked_users=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                isBookmarked=Case(
                    When(bookmarks=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                comments=Count('comment'),
            )
            paginate_queryset = self.paginate_queryset(result)
            if paginate_queryset:
                serializer = self.serializer_class(paginate_queryset, many=True)
                result = self.get_paginated_response(serializer.data)
                return Response(data=result.data, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_200_OK)


class BookmarksListView(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = ListSetPagination
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        query_dict = {}

        before = self.request.query_params.get('before', None)
        after = self.request.query_params.get('after', None)
        search = self.request.query_params.get('search', None)
        sort_by = self.request.query_params.get('sort_by', None)

        if after:
            query_dict['created_at__gte'] = after
        if before:
            query_dict['created_at__lte'] = before

        if search:
            queryset = queryset.filter(Q(title__icontains=search))

        if sort_by:
            if sort_by == 'date':
                queryset = queryset.order_by('-created_at')
            if sort_by == '-date':
                queryset = queryset.order_by('created_at')
            if sort_by == 'title_asc':
                queryset = queryset.order_by('title')
            if sort_by == 'title_desc':
                queryset = queryset.order_by('-title')

        queryset = queryset.filter(**query_dict)

        user = get_object_or_404(UserProfile, username=request.user)
        if user:
            queryset = queryset.filter(bookmarks=user)
            result = queryset.annotate(
                isLiked=Case(
                    When(liked_users=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                isDisliked=Case(
                    When(disliked_users=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                isBookmarked=Case(
                    When(bookmarks=request.user, then=Value(True)),
                    default=Value(False),
                    output_field=BooleanField()
                ),
                comments=Count('comment'),
            ).distinct()

            print(queryset)

            paginate_queryset = self.paginate_queryset(result)
            if paginate_queryset:
                serializer = self.serializer_class(paginate_queryset, many=True)
                result = self.get_paginated_response(serializer.data)
                return Response(data=result.data, status=status.HTTP_200_OK)
            else:
                return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_200_OK)


class SubscriptionMiniList(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    serializer_class = SubscriptionListMiniSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = get_object_or_404(UserProfile, username=request.user)
        blog_list = self.queryset.filter(subscribers=user)
        serializer = self.serializer_class(blog_list, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class BlogAuthorList(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = InviteGetUsersSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset

        query = self.request.query_params.get('query', None)
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        if query:
            query_authors = UserProfile.objects.filter(username__icontains=query, blog_list=blog)
            serializer = self.serializer_class(query_authors, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            blog_authors = blog.authors.all()
            serializer = self.serializer_class(blog_authors, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)


class SetCommentLikeView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def set_or_remove_like(self, request, slug, post_id, comment_id):
        user = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        comment = get_object_or_404(Commentary, comment_id=comment_id, post=post)
        if comment.disliked_users.contains(user):
            comment.disliked_users.remove(user)
            comment.dislikes -= 1
        if not comment.liked_users.contains(user):
            comment.liked_users.add(user)
            comment.likes += 1
        else:
            comment.liked_users.remove(user)
            comment.likes -= 1
        comment.save(update_fields=("likes", "dislikes"))
        return Response({'status': 'successful'}, status=status.HTTP_200_OK)

    def set_or_remove_dislike(self, request, slug, post_id, comment_id):
        user = get_object_or_404(UserProfile, username=request.user)
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        comment = get_object_or_404(Commentary, comment_id=comment_id, post=post)
        if comment.liked_users.contains(user):
            comment.liked_users.remove(user)
            comment.likes -= 1
        if not comment.disliked_users.contains(user):
            comment.disliked_users.add(user)
            comment.dislikes =+ 1
        else:
            comment.disliked_users.remove(user)
            comment.dislikes -= 1
        comment.save(update_fields=("likes", "dislikes"))
        return Response({'status': 'successful'}, status=status.HTTP_200_OK)


class SetCommentLikeByAuthorView(viewsets.ModelViewSet):
    permissions_classes = [IsAuthenticated]

    def set_or_remove_like_by_author(self, request, slug, post_id, comment_id):
        blog = get_object_or_404(Blog, slug=slug)
        post = get_object_or_404(Post, post_id=post_id, blog=blog)
        comment = get_object_or_404(Commentary, comment_id=comment_id, post=post)
        if not comment.liked_by_author:
            comment.liked_by_author = True
            comment.save(update_fields=("liked_by_author",))
            return Response({'status': 'successful'}, status=status.HTTP_200_OK)
        else:
            comment.liked_by_author = False
            comment.save(update_fields=("liked_by_author",))
            return Response({'status': 'successful'}, status=status.HTTP_200_OK)


class UserNotificationListView(viewsets.ModelViewSet):
    queryset = Notification.objects.filter(is_hidden=False)
    permission_classes = [IsAuthenticated]
    serializer_class = UserNotificationsSerializer
    pagination_class = ListSetPagination

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.filter(addressee=request.user)

        paginate_queryset = self.paginate_queryset(queryset)
        if paginate_queryset:
            serializer = self.serializer_class(paginate_queryset, many=True)
            result = self.get_paginated_response(serializer.data)
            return Response(data=result.data, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class SetNotificationIsRead(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def read_notification(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=("is_read",))
            return Response({'status': 'successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class HideNotificationView(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def hide_notification(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk)
        if not notification.is_hidden:
            notification.is_hidden = True
            notification.save(update_fields=("is_hidden",))
            return Response({'status': 'successful'}, status=status.HTTP_200_OK)
        else:
            return Response({'status': 'unsuccessful'}, status=status.HTTP_404_NOT_FOUND)


class BlogDeletePostsView(viewsets.ModelViewSet):
    serializer_class = BlogDeletePostsSerializer
    permission_classes = [IsAuthenticated]

    def delete_posts(self, request, slug):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        blog = get_object_or_404(Blog, slug=slug)
        selected_posts = serializer.data['selectedPosts']
        print(selected_posts)
        for post in selected_posts:
            post = get_object_or_404(Post, post_id=post, blog=blog)
            post.delete()
        return Response('status: successful', status=status.HTTP_200_OK)


class BlogCommentsDeleteView(viewsets.ModelViewSet):
    serializer_class = BlogCommentListDeleteSerializer
    permission_classes = [IsAuthenticated]

    def delete_comments(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        comment_list = serializer.data['comment_list']
        blog = get_object_or_404(Blog, slug=self.kwargs['slug'])
        print(comment_list)
        # for comment in comment_list:
        return Response({'status: successful'}, status=status.HTTP_200_OK)