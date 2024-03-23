from jarvis.models import FCMDevice
from redis_utils import *
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models import Q
from forum.topic.utils import delete_redis_fcm_token

def run():
    try:
        all_entries = []
        all_keys = []
        fcm_tokens_keys_to_be_deleted = []
        for key in redis_cli.keys("bi:fcm_device:*"):
            try:
                data = redis_cli.get(key)
                data =  json.loads(data) if data else None
                if data:
                    all_entries += data
                    all_keys.append(key)
                    for each_data in data:
                        if ('user_id' in each_data) and (each_data['user_id']):
                            fcm_tokens_keys_to_be_deleted.append(each_data['user_id'])
            except Exception as e:
                print e

        if all_entries:
            for entry in all_entries:
                try:
                    reg_id = entry.get('reg_id', None)
                    dev_id = entry.get('dev_id', None)
                    created_at = entry.get('created_at', datetime.now() - timedelta(days=1))
                    entry['created_at'] = created_at
                    entry['is_active'] = True
                    entry['is_uninstalled'] = False
                    instance = FCMDevice.objects.using('default').filter(Q(reg_id = reg_id) | Q(dev_id = dev_id))
                    if not len(instance):
                        print 'Not Exists'
                        raise Exception
                    print 'Exisits'
                    desc=instance[0].uninstalled_desc
                    entry['uninstalled_desc'] = desc
                    if desc:
                        list_data = json.loads(desc)
                        if 'uninstall' in list_data[len(list_data)-1]:
                            list_data.append({'install': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                        desc=json.dumps(list_data)
                    
                    if ('user_id' in each_data) and (each_data['user_id']):
                        instance.update(**entry)
                    else:
                        entry.pop('user_id',None)
                        instance.update(**entry)
                except Exception as e:
                    print e
                    entry.pop('uninstalled_desc', None)
                    entry.pop('is_active', None)
                    if ('user_id' in each_data) and (each_data['user_id']):
                        instance = FCMDevice.objects.create(**entry)
                    else:
                        entry.pop('user_id',None)
                        entry['name'] = 'Anonymous'
                        instance = FCMDevice.objects.create(**entry)
            for each_key in all_keys:
                try:
                    redis_cli.delete(each_key)
                except Exception as e:
                    print e
            try:
                for each_key in fcm_tokens_keys_to_be_deleted:
                    delete_redis_fcm_token(each_key)
            except Exception as e:
                print e
    except Exception as e:
        print e