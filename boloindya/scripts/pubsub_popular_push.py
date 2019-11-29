from forum.topic.models import Topic
from drf_spirit.serializers import PubSubPopularSerializer
from django.http import JsonResponse
from django.db.models import Q
from jarvis.models import FCMDevice

def run():
    pubsub_obj = Topic.objects.filter(Q(is_pubsub_popular_push=True) & Q(is_popular = False))
    if pubsub_obj:
        serialized_data = {'pupluar_data' : PubSubPopularSerializer(pubsub_obj, many=True).data}
        devices = FCMDevice.objects.filter(user__pk=39342)
        print len(devices)
        for index in xrange(0, len(devices), 1000):
            device = devices[index:index + 1000]
            print len(device)

            # devices.send_message(data={'pupluar_data': serialized_data })
        print devices
        # print devices
        # Send Popular Data to Users 

    # pubsub_obj.update(is_popular = True)