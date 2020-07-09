from drf_spirit.models import UserJarvisDump
from redis_utils import *

def run():
    try:
        key = "bi:sync_dump"
        all_entries = get_redis(key)
        if all_entries:
            aList = [UserJarvisDump(**vals) for vals in all_entries]
            UserJarvisDump.objects.bulk_create(aList, batch_size=10000)
            set_redis(key,[])
    except Exception as e:
        print e