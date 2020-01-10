from forum.topic.models import Topic
from drf_spirit.serializers import PubSubPopularSerializer
from django.http import JsonResponse
from django.db.models import Q
from jarvis.models import FCMDevice

def run():
    pubsub_obj = Topic.objects.filter(Q(is_pubsub_popular_push=False) & Q(is_popular = True))
    pubsub_obj.update(is_popular = False)
