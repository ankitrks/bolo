from forum.topic.models import Topic
from drf_spirit.serializers import PubSubPopularSerializer
from django.http import JsonResponse
from django.db.models import Q
from jarvis.models import FCMDevice

def run():
    pubsub_obj = Topic.objects.filter(Q(is_pubsub_popular_push=True) & Q(is_popular = False))
    if pubsub_obj:
        devices = FCMDevice.objects.filter(user__pk=41)
        print len(devices)
        # for index in xrange(0, len(devices), 1000):
        #     device = devices[index:index + 1000]
        #     print len(device)
        print devices
        t = devices.send_message(data={'pupluar_data': 'true' })
        # print devices
        # Send Popular Data to Users 

    # pubsub_obj.update(is_popular = True)
