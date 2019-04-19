from django_filters.rest_framework import CharFilter, FilterSet

from forum.comment.models import Comment
from forum.topic.models import Topic 


class CommentFilter(FilterSet):
    """
    A filter class for filtering comments
    """

    topic = CharFilter(name="topic__slug")
    user = CharFilter(name="user__id")

    class Meta:
        model = Comment
        fields = ['topic', 'user']


class TopicFilter(FilterSet):
    """
    A filter class for filtering Topics
    """

    class Meta:
        model = Topic
        fields = ['is_removed', 'is_pinned', 'is_globally_pinned']
