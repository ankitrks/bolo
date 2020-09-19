from datetime import datetime, timedelta, date
from forum.topic.models import Topic
from forum.user.models import UserProfile, Weight
from forum.category.models import Category
from drf_spirit.utils import language_options
from datetime import datetime
from redis_utils import * 
from jarvis.models import FCMDevice
from django.conf import settings 
from forum.topic.utils import update_redis_hashtag_paginated_data, update_redis_paginated_data ,new_algo_update_redis_paginated_data
from scripts import update_serialized_hashtag_paginated_data

def run():
    calculate_all_vb_score_and_set_post_in_redis()


def calculate_all_vb_score_and_set_post_in_redis():
    now = datetime.now()
    all_post = False
    if all_post:
        last_modified_post = Topic.objects.filter(is_vb=True).order_by('-date').values_list('pk', flat=True)
    else:
        last_modified_post = Topic.objects.filter(is_vb=True,is_removed=False,last_modified__gt=now-timedelta(hours = 1)).order_by('-date').values_list('pk', flat=True)
    total_elements = len(last_modified_post)
    counter=1
    for each_post in last_modified_post:
        try:
            print "###########",counter,"/",total_elements,"###########"
            topic = Topic.objects.get(pk=each_post)
            print "old score:  ",topic.vb_score
            new_score = topic.calculate_vb_score()
            counter+=1
            print "new score:  ",new_score
        except Exception as e:
            print e
