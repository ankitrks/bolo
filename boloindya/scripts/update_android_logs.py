from forum.user.models import AndroidLogs
from redis_utils import *

def run():
    try:
        all_entries = []
        all_keys = []
        for key in redis_cli_logs_read_only.keys("bi:android_logs:*"):
            try:
                data = redis_cli_logs_read_only.get(key)
                data =  json.loads(data) if data else None
                # print data['log_type'], len(data['log_type'])
                if data and data.has_key('log_type') and len(data['log_type']) < 255:
                    all_entries += [data]
                    all_keys.append(key)
            except Exception as e:
                print e
        if all_entries:
            aList = [AndroidLogs(**vals) for vals in all_entries]
            AndroidLogs.objects.bulk_create(aList, batch_size=10000)
            for each_key in all_keys:
                try:
                    redis_cli_logs.delete(each_key)
                except Exception as e:
                    print e
    except Exception as e:
        print e
