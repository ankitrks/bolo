import os
import sys
import json
import requests

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

import django
from django.conf import settings
from django.db import connections
import threading


region = 'ap-south-1'
service = 'es'

def get_topic_data(offset=0, limit=2000):
    print("db offset", offset, "db limit ", limit)
    with connections['default'].cursor() as cr:
        cr.execute("""
            SELECT tp.id, date_trunc('second', tp.created_at)::text, tp.created_at::date::text as create_date, tp.user_id, tp.language_id, array_agg(tc.category_id) as category_id
            FROM forum_topic_topic tp
            LEFT JOIN forum_topic_topic_m2mcategory tc on tc.topic_id = tp.id
            GROUP BY tp.id order by tp.id offset %s limit %s
        """, [offset, limit])

        columns = [col[0] for col in cr.description]
        return [
            dict(zip(columns, row))
            for row in cr.fetchall()
        ]


def get_topic_count():
    with connections['default'].cursor() as cr:
        cr.execute("""
            SELECT count(1)
            FROM forum_topic_topic
        """)

        return cr.fetchall()[0][0]

def get_es_client():
    return (settings.ES_7_CONFIG.get('username'), settings.ES_7_CONFIG.get('password'))


def es_bulk_insert(doc_list, index_name):
    bulk_body = []

    for doc in doc_list:
        bulk_body.append({'index': {'_index': index_name, '_id': doc.pop('id')}})
        bulk_body.append(doc)
        
    # print(es.bulk(body=bulk_body, headers={"Content-Type": "application/x-ndjson"}))
    body = '\n'.join(map(json.dumps, bulk_body)) + '\n'

    url = 'https://'+settings.ES_7_CONFIG.get('host')+'/%s/_bulk'%index_name
    response = requests.post(url, headers={"Content-Type": "application/x-ndjson"}, data=body, auth=get_es_client())

    if response.ok:
        print("data successfully indexed")
    else:
        raise Exception(response.text)



def run_by_threads(offset, offset_limit):
    while True:
        print("offset", offset)
        topic_data = get_topic_data(offset, 50000)
        print("data fetched")
        topic_data_len = len(topic_data)
        if topic_data_len == 0:
            break

        es_bulk_insert(topic_data, 'topic-index')
        offset += len(topic_data)

        if offset > offset_limit:
            break


def run():
    es = get_es_client()

    THREADS = 5 #os.cpu_count() * 3

    total_topic = get_topic_count()

    segments_partition = list(range(0, total_topic, int((total_topic)/THREADS))) + [total_topic]
    segments = [(segments_partition[i], segments_partition[i+1]) for i in range(0, len(segments_partition)-1)]


    print("segments_partition", segments)
    for segment in segments:
        threading.Thread(target=run_by_threads, args=(segment[0], segment[1] + 1)).start()    
