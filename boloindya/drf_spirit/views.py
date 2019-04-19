from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated, AllowAny

from .filters import TopicFilter, CommentFilter
from forum.topic.models import Topic
from forum.category.models import Category
from forum.comment.models import Comment
from .permissions import IsOwnerOrReadOnly
from .serializers import TopicSerializer, CategorySerializer, CommentSerializer


class TopicList(generics.ListCreateAPIView):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = TopicFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TopicDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TopicSerializer
    queryset = Topic.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    lookup_field = 'slug'


class TopicCommentList(generics.ListAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.filter()
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self):
        topic_slug = self.kwargs['slug']
        return self.queryset.filter(topic__slug=topic_slug)


class CategoryList(generics.ListAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (IsAuthenticated,)

class CommentList(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = CommentFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentDetails(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentSerializer
    queryset = Comment.objects.all()
    permission_classes = (IsOwnerOrReadOnly,)
    lookup_field = 'id'
