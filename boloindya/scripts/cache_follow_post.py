from forum.user.models import UserProfile
from jarvis.models import FCMDevice
from drf_spirit.utils import language_options
from datetime import datetime,timedelta
from redis_utils import *
from forum.topic.utils import update_redis_follow_paginated_data
from django.conf import settings

def run():
    start_total = datetime.now()
    last_n_active_days = settings.LAST_N_ACTIVE_DAYS
    all_last_n_day_active_user = FCMDevice.objects.filter(user__isnull=False,end_time__gte=datetime.now()-timedelta(days=last_n_active_days)).distinct('-user_id')
    for each_device in all_last_n_day_active_user:
            each_device = FCMDevice.objects.filter(user_id=each_device).order_by('-end_time').first()
            start = datetime.now()
            final_data = update_redis_follow_paginated_data(each_device.user.id)
            print final_data
            end = datetime.now()
            print 'Runtime: Folow post of user_id ' + str(each_device.user.id) + ' is ' + str(end - start)
            print "\n\n\n\n"
    print 'Runtime Total is ' + str(datetime.now() - start_total)
