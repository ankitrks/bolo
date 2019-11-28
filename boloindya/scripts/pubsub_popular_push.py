from forum.topic.models import Topic
from drf_spirit.serializers import PubSubPopularSerializer
from django.http import JsonResponse
from django.db.models import Q

def run():
    pubsub_obj = Topic.objects.filter(Q(is_pubsub_popular_push=True) & Q(is_popular = False))
    if pubsub_obj:
        serialized_data = JsonResponse(PubSubPopularSerializer(pubsub_obj, many=True).data, safe=False)
        print serialized_data
    pubsub_obj.update(is_popular = True)