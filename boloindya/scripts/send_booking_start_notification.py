import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from multiprocessing import Process, Pool

from django.db import connections

from payment.razorpay import get_order_payments
from payment.helpers import execute_query


def send_notification_in_parallel():
    pool = Pool(processes=len(command_list))
    for cmd in command_list:
        pool.apply_async(run_command, args=(cmd,))

    pool.close()
    pool.join()


def run():
    notification_data_list = []

    for booking in EventBooking.objects.filter(event_slot__start_time__lte = datetime.now() + timedelta(minutes=60)):
        booker = booking.user
        _data = {

        }