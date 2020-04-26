from rest_framework import viewsets
from .models import Post
from .serializers import PostSerializer
from rest_framework.permissions import IsAuthenticated
from authentication.authentication import FirebaseAuthentication


class PostView(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (FirebaseAuthentication,)

    queryset = Post.objects.all()
    serializer_class = PostSerializer
