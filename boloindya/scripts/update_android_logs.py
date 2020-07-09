from forum.user.models import AndroidLogs
from redis_utils import *

def run():
  try:
    all_entries = []
    all_keys = []
    for key in redis_cli.keys("bi:android_logs:*"):
        try:
            data = redis_cli.get(key)
            data =  json.loads(data) if data else None
            if data:
                all_entries += data
                all_keys.append(key)
        except Exception as e:
            print e
    if all_entries:
        aList = [AndroidLogs(**vals) for vals in all_entries]
        AndroidLogs.objects.bulk_create(aList, batch_size=10000)
        for each_key in all_keys:
            try:
                redis_cli.delete(each_key)
            except Exception as e:
                print e

    except Exception as e:
        print e