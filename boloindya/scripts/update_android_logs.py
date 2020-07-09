from forum.user.models import AndroidLogs
from redis_utils import *

def run():
    try:
        key = "bi:android_logs"
        all_entries = get_redis(key)
        if all_entries:
            aList = [AndroidLogs(**vals) for vals in all_entries]
            AndroidLogs.objects.bulk_create(aList, batch_size=10000)
            set_redis(key,[])
    except Exception as e:
        print e