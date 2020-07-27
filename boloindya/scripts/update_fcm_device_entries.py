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
                        if not each_data['user_id']:
                            user_id = key.split(":")[-1]
                            fcm_tokens_keys_to_be_deleted.append(user_id)
            except Exception as e:
                print e
        if all_entries:
            for entry in all_entries:
                try:
                    created_at = entry.get('created_at', datetime.now() - timedelta(days=1))
                    instance = FCMDevice.objects.using('default').filter(Q(reg_id = entry['reg_id']) | Q(dev_id = entry['dev_id']))
                    if not len(instance):
                        print 'Not Exists'
                        raise Exception
                    print 'Exisits'
                    desc=instance[0].uninstalled_desc
                    if desc:
                        list_data = json.loads(desc)
                        if 'uninstall' in list_data[len(list_data)-1]:
                            list_data.append({'install': datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
                        desc=json.dumps(list_data)
                    if entry['user_id'] == None:
                        instance.update(is_active = True,dev_id=entry['dev_id'],device_type = entry['device_type'], reg_id=entry['reg_id'], is_uninstalled=False, uninstalled_desc=desc, device_model=entry['device_model'], current_version=entry['current_version'], manufacturer=entry['manufacturer'], created_at=created_at)
                    else:
                        instance.update(user_id = entry['user_id'],is_active = True,dev_id=entry['dev_id'],device_type = entry['device_type'],reg_id=entry['reg_id'] , is_uninstalled=False, uninstalled_desc=desc, device_model=entry['device_model'], current_version=entry['current_version'], manufacturer=entry['manufacturer'], created_at=created_at)
                except Exception as e:
                    print e
                    if entry['user_id'] == None:
                        instance = FCMDevice.objects.create(reg_id = entry['reg_id'],name='Anonymous',dev_id=entry['dev_id'],device_type = entry['device_type'], is_uninstalled=False, device_model=entry['device_model'], current_version=entry['current_version'], manufacturer=entry['manufacturer'], created_at=created_at)
                    else:
                        instance = FCMDevice.objects.create(user_id = entry['user_id'],reg_id = entry['reg_id'],dev_id=entry['dev_id'],device_type = entry['device_type'], is_uninstalled=False, device_model=entry['device_model'], current_version=entry['current_version'], manufacturer=entry['manufacturer'], created_at=created_at)
            for each_key in all_keys:
                try:
                    redis_cli.delete(each_key)
                except Exception as e:
                    print e
            for each_key in fcm_tokens_keys_to_be_deleted:
                delete_redis_fcm_token(each_key)
    except Exception as e:
        print e