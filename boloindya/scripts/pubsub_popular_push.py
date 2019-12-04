from forum.topic.models import Topic
from drf_spirit.serializers import PubSubPopularSerializer
from django.http import JsonResponse
from django.db.models import Q
from jarvis.models import FCMDevice

def run():
    from django.core.paginator import Paginator
    pubsub_obj = Topic.objects.filter(Q(is_pubsub_popular_push=True) & Q(is_popular = False))
    if pubsub_obj:
        devices = FCMDevice.objects.all(user__isnull=False)
        device_pagination = Paginator(devices, 1000)
        for index in range(1, (device_pagination.num_pages+1)):
            device = device_pagination.page(index)
            t = device.object_list.send_message(data={'pupluar_data': 'true' })
                
    pubsub_obj.update(is_popular = True)
