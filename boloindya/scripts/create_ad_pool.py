
import os
import sys
import json
from datetime import datetime

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from multiprocessing import Process, Pool

from django.db import connections

from redis_utils import get_redis, set_redis, redis_cli
from advertisement.models import Ad
from advertisement.serializers import AdSerializer
from advertisement.utils import filter_data_from_dict
from drf_spirit.models import SystemParameter
from drf_spirit.utils import language_options


def save_ad_data_in_redis(ad):
    print "setting data", 'ad:%s'%ad.id,  AdSerializer(ad).data
    set_redis('ad:%s'%ad.id, AdSerializer(ad).data, False)


def save_ad_data_in_redis_in_parallel(ad_ids):
    # pool = Pool(processes=8)

    for ad in Ad.objects.filter(id__in=ad_ids):
        # pool.apply_async(save_ad_data_in_redis, args=(ad,))
        save_ad_data_in_redis(ad)

    # pool.close()
    # pool.join()


def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def run():
    cursor = connections['default'].cursor()
    ad_sequence_dict = {}
    max_scroll = 100
    now = datetime.now()

    #Ad.objects.filter(start_time__lte=now, end_time__gte=now)\
    #            .exclude(state__in=['completed', 'ongoing', 'inactive'], is_deleted=True)\
    #            .update(state='ongoing')

    Ad.objects.filter(end_time__lte=now, state=['ongoing'], is_deleted=False).update(state='completed')

    cursor.execute("""
        SELECT ad.title, ad.id, ad.frequency_type, ad.languages, freq.sequence, freq.scroll
        FROM advertisement_ad ad
        INNER JOIN advertisement_frequency freq on freq.ad_id = ad.id
        WHERE  state = 'ongoing' and not is_deleted
    """)
    result = dictfetchall(cursor)

    for ad in result:
        if ad.get('frequency_type') == 'constant':
            scroll = ad.get('scroll')

            next_scroll = scroll
            while next_scroll <= max_scroll:
                ad_sequence_dict.setdefault(str(next_scroll), []).append(ad)
                next_scroll += scroll

        elif ad.get('frequency_type') == 'variable':
            ad_sequence_dict.setdefault(str(ad.get('scroll')), []).append(ad)
    for id_, value in language_options:
        lang_specific_ad_sequence_dict = {}
        for key,value in ad_sequence_dict.items():
            lang_specific_data = list(filter(lambda x: id_ in x['languages'], value))
            if lang_specific_data:
                lang_specific_ad_sequence_dict[key] = lang_specific_data
        set_redis('ad:pool:lang:%s'%id_, lang_specific_ad_sequence_dict, False)
    save_ad_data_in_redis_in_parallel([ad.get('id') for ad in result])
    print json.dumps(ad_sequence_dict, indent=3)
