from rest_framework import viewsets
from .serializers import PostsSerializer
from .models import Post


class PostsList(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostsSerializer
