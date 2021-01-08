
import os
import sys
from datetime import datetime
from random import Random

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from multiprocessing import Process, Pool

from django.db import connections
from django.db import transaction

from dynamodb_api import query
from redis_utils import get_redis, set_redis
from advertisement.models import Ad, AdEvent, Seen, Skipped, Install, ShopNow, LearnMore, PlaceOrder, FullWatched
from advertisement.utils import filter_data_from_dict
from drf_spirit.models import SystemParameter
from marketing.models import AdStats

rand = Random()

dashboard_data = {}


def get_last_processed_id(name):
    param, is_created = SystemParameter.objects.get_or_create(name=name, defaults={'value': 0})
    return param.value

def update_last_processed_id(name, value):
    param = SystemParameter.objects.get(name=name)
    param.value = str(value)
    param.save()

@transaction.atomic
def process_ad_event(event, keys):
    print "Processing for event: ", event
    event_list = query('EventBookingEvent_PROD', {
        ':v1': {'S': event,},
        ':v2':{'N': get_last_processed_id('ad:%s:last_processed_id'%event),},
    }, 'event = :v1 and id > :v2')

    item_list = []
    max_id = 0

    for item in event_list:
        event_data = filter_data_from_dict(keys, item)
        event_data['event_id'] = int(item.get('event_id'))

        if int(item.get('id')) > max_id:
            max_id = int(item.get('id'))

        item.update(event_data)

    if max_id == 0:
        return

    update_last_processed_id('ad:%s:last_processed_id'%event, max_id)

    for item in event_list:
        data = dashboard_data.setdefault(int(item.get('event_id')), {}).setdefault(str(datetime.strptime(item.get('created_at'), '%Y-%m-%d %H:%M:%S.%f').date()), {})


        if event == 'event_view':
            data['event_view'] = data.setdefault('event_view', 0) + 1

        elif event == 'event_register_click':
            data['event_register_click'] = data.setdefault('event_register_click', 0) + 1

        elif event == 'payment_initiated':
            data['payment_initiated'] = data.setdefault('payment_initiated', 0) + 1

        elif event == 'confirm_booking':
            data['confirm_booking'] = data.setdefault('confirm_booking', 0) + 1


def process_events_in_parallel():
    for event in ['event_view', 'event_register_click', 'payment_initiated', 'confirm_booking']:
        get_last_processed_id('event:booking:%s:last_processed_id'%event)

    process_ad_event('event_view', ('user_id', 'event_id', 'created_at'))
    process_ad_event('event_register_click', ('user_id', 'event_id', 'created_at'))
    process_ad_event('payment_initiated', ('user_id', 'event_id', 'created_at'))
    process_ad_event('confirm_booking', ('user_id', 'event_id', 'created_at'))

    item_list = []

    for event_id, data in dashboard_data.items():
        for date, item in data.items():
            stats, is_created = EventStats.objects.get_or_create(event_id=event_id, date=date)
            stats.view_count += item.get('event_view', 0)
            stats.click_count += item.get('event_register_click', 0)
            stats.payment_initiated_count += item.get('payment_initiated', 0)
            stats.confirm_booking_count += item.get('confirm_booking', 0)
            stats.save()

def run():
    process_events_in_parallel()
