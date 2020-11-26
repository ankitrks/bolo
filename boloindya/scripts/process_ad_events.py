
import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from multiprocessing import Process, Pool

from django.db import connections

from dynamodb_api import query
from redis_utils import get_redis, set_redis
from advertisement.models import AdEvent, Seen, Skipped, Clicked, Playtime
from advertisement.utils import filter_data_from_dict
from drf_spirit.models import SystemParameter


def get_last_processed_id(name):
    param, is_created = SystemParameter.objects.get_or_create(name=name, defaults={'value': 0})
    return param.value

def update_last_processed_id(name, value):
    param = SystemParameter.objects.get(name=name)
    param.value = str(value)
    param.save()

def process_ad_event(Model, event, keys):
    event_list = query(AdEvent, {
        ':v1': {'S': event,},
        ':v2':{'N': get_last_processed_id('ad:%s:last_processed_id'%event),},
    }, 'event = :v1 and id > :v2')

    item_list = []
    max_id = 0
    for item in event_list:
        event_data = filter_data_from_dict(keys, item)
        item_list.append(Model(**event_data))

        if int(item.get('id')) > max_id:
            max_id = int(item.get('id'))

    if not max_id == 0:
        Model.objects.bulk_create(item_list)
        update_last_processed_id('ad:%s:last_processed_id'%event, max_id)


def process_events_in_parallel():
    pool = Pool(processes=4)

    pool.apply_async(process_ad_event, args=(Seen, 'seen', ('user_id', 'ad_id', 'created_at')))
    pool.apply_async(process_ad_event, args=(Skipped, 'skip', ('user_id', 'ad_id', 'created_at')))
    pool.apply_async(process_ad_event, args=(Clicked, 'click', ('user_id', 'ad_id', 'created_at')))
    pool.apply_async(process_ad_event, args=(Playtime, 'playtime', ('user_id', 'ad_id', 'created_at', 'playtime')))
    pool.apply_async(process_ad_event, args=(Install, 'install_now', ('user_id', 'ad_id', 'created_at')))
    pool.apply_async(process_ad_event, args=(Playtime, 'shop_now', ('user_id', 'ad_id', 'created_at')))
    pool.apply_async(process_ad_event, args=(Playtime, 'buy_now', ('user_id', 'ad_id', 'created_at')))
    pool.apply_async(process_ad_event, args=(LearnMore, 'learn_more', ('user_id', 'ad_id', 'created_at')))
    pool.apply_async(process_ad_event, args=(PlaceOrder, 'place_order', ('user_id', 'ad_id', 'created_at')))

    pool.close()
    pool.join()

def run():
    process_events_in_parallel()
