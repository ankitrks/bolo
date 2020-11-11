import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from multiprocessing import Process, Pool
from django.db import connections
from drf_spirit.models import DatabaseRecordCount

def execute_query(record):
    cursor = connections['read'].cursor()
    if record.query.strip().split(' ')[0].lower() != 'select':
        return 

    cursor.execute(record.query)
    record.count = cursor.fetchall()[0][0]
    record.save()

def process_record_in_parallel():
    pool = Pool(processes=4)

    for record in DatabaseRecordCount.objects.filter(is_active=True):
        pool.apply_async(execute_query, args=(record,))

    pool.close()
    pool.join()

def run():
    process_record_in_parallel()