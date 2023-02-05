from rest_framework import viewsets, status
from rest_framework.response import Response

from .serializers import BlogSerializer, PostSerializer
from .models import Post, Blog


class CreatePost(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer


class CreateBlog(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = BlogSerializer

    # def create(self, request, *args, **kwargs):
    #     serializer = self.serializer_class(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     title = serializer.data['title']
    #     description = serializer.data['description']
    #     # created_at = serializer.data['created_at']
    #     updated_at = serializer.data['updated_at']
    #     # authors = serializer.data['authors']
    #     # owner = serializer.data['owner']
    #
    #     blog_object = Blog(
    #         title=title,
    #         description=description,
    #         updated_at=updated_at,
    #         # authors=authors,
    #         # owner=owner
    #     )
    #
    #     blog_object.save()
    #
    #     return Response(blog_object, status=status.HTTP_200_OK)
