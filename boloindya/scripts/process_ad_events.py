
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

def get_mapped_ad(ad_id):
    if ad_id in (0, 1, 2, 3):
        return 4
    return ad_id

def get_last_processed_id(name):
    param, is_created = SystemParameter.objects.get_or_create(name=name, defaults={'value': 0})
    return param.value

def update_last_processed_id(name, value):
    param = SystemParameter.objects.get(name=name)
    param.value = str(value)
    param.save()

@transaction.atomic
def process_ad_event(Model, event, keys):
    print "Processing for event: ", event
    event_list = query('AdEvent_PROD', {
        ':v1': {'S': event,},
        ':v2':{'N': get_last_processed_id('ad:%s:last_processed_id'%event),},
    }, 'event = :v1 and id > :v2')

    ad_list = list(Ad.objects.all().values_list('id', flat=True))
    item_list = []
    max_id = 0

    for item in event_list:
        event_data = filter_data_from_dict(keys, item)

        ad_id = int(item.get('ad_id'))
        
        event_data['ad_id'] = get_mapped_ad(ad_id)
        event_data['user_id'] = 1  # temp added

        playtime = item.get('playtime', item.get('data', {}).get('playtime', '0'))

        seconds = 0
        splitted_playtime = playtime.split(':')

        if len(splitted_playtime) == 2:
            seconds = int(splitted_playtime[0]) * 60 + int(splitted_playtime[1])
        else:
            seconds = int(int(playtime) / 1000)

        event_data['playtime'] = seconds if seconds >= 0 else -seconds

        item_list.append(Model(**event_data))

        if int(item.get('id')) > max_id:
            max_id = int(item.get('id'))

        item.update(event_data)


    if max_id == 0:
        return

    created_items = Model.objects.bulk_create(item_list)
    update_last_processed_id('ad:%s:last_processed_id'%event, max_id)

    if event in ('place_order'):
        return

    for item in event_list:
        data = dashboard_data.setdefault(int(item.get('ad_id')), {}).setdefault(str(datetime.strptime(item.get('created_at'), '%Y-%m-%d %H:%M:%S.%f').date()), {})
        data['views'] = data.setdefault('views', 0) + 1

        if event == 'skip':
            data['skip_playtime'] = data.setdefault('skip_playtime', 0) + item.get('playtime', 0)
        elif event == 'install_now':
            data['install_playtime'] = data.setdefault('install_playtime', 0) + item.get('playtime', 0)

        if event == 'install_now':
            data['installs'] = data.setdefault('installs', 0) + 1

        elif event == 'skip':
            data['skips'] = data.setdefault('skips', 0) + 1

        elif event == 'Entire Video':
            data['full_watched'] = data.setdefault('full_watched', 0) + 1


def process_events_in_parallel():
    for event in ['skip', 'install_now', 'shop_now', 'buy_now', 'learn_more', 'place_order', 'Entire Video']:
        get_last_processed_id('ad:%s:last_processed_id'%event)

    process_ad_event(Skipped, 'skip', ('user_id', 'ad_id', 'created_at'))
    process_ad_event(Install, 'install_now', ('user_id', 'ad_id', 'created_at'))
    process_ad_event(ShopNow, 'shop_now', ('user_id', 'ad_id', 'created_at'))
    process_ad_event(ShopNow, 'buy_now', ('user_id', 'ad_id', 'created_at'))
    process_ad_event(LearnMore, 'learn_more', ('user_id', 'ad_id', 'created_at'))
    process_ad_event(PlaceOrder, 'place_order', ('user_id', 'ad_id', 'created_at'))
    process_ad_event(FullWatched, 'Entire Video', ('user_id', 'ad_id', 'created_at'))

    item_list = []

    for ad_id, data in dashboard_data.items():
        for date, item in data.items():
            stats, is_created = AdStats.objects.get_or_create(ad_id=ad_id, date=date)
            stats.view_count += item.get('views', 0)
            stats.install_count += item.get('installs', 0)
            stats.skip_count += item.get('skips', 0)
            stats.full_watched += item.get('full_watched', 0)
            stats.skip_playtime += item.get('skip_playtime', 0)
            stats.install_playtime += item.get('install_playtime', 0)
            stats.save()

def run():
    process_events_in_parallel()
