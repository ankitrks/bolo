import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from multiprocessing import Process, Pool

from django.db import connections
from django.conf import settings

from tasks import send_fcm_push_notifications
from payment.helpers import execute_query

check_time = settings.BOOKING_NOTIFICATION_CHECK_TIME

def send_notification_in_parallel(notification_data_list):
    if len(notification_data_list) < 1:
        return 

    pool = Pool(processes=len(notification_data_list))
    for notification_data in notification_data_list:
        pool.apply_async(send_fcm_push_notifications, 
                        args=(notification_data.get('device_id'), notification_data.get('title'), notification_data.get('body')))

    pool.close()
    pool.join()


def prepare_notification(booking):
    if booking.get('creator_device_id'):
        return {
            "device_id": booking.get('creator_device_id'),
            "title": 'Bolo Meet Reminder',
            "body": "Your online session '%s' starts in %s minutes."%(
                booking.get("title"), booking.get("time_remaining")
            ) 
        }

    if booking.get('booker_device_id'):
        return {
            "device_id": booking.get('booker_device_id'),
            "title": 'Bolo Meet Reminder',
            "body": "Your online session '%s' starts in %s minutes."%(
                booking.get("title"), booking.get("time_remaining")
            ) 
        }


def run():
    notification_data_list = []

    bookings_data_for_creator = execute_query("""
        select b.id, e.title, coalesce(NULLIF(cp.name, ''), cp.slug) as creator, 
            coalesce(NULLIF(bp.name,''), bp.slug) as booker, cf.reg_id as creator_device_id,
            (EXTRACT(EPOCH FROM (s.start_time - now()))/60)::numeric::integer as time_remaining
        from booking_eventbooking b
        inner join booking_eventslot s on s.id = b.event_slot_id
        inner join booking_event e on e.id = b.event_id
        left join jarvis_fcmdevice cf on cf.user_id = e.creator_id
        left join forum_user_userprofile cp on cp.user_id = e.creator_id
        left join forum_user_userprofile bp on bp.user_id = b.user_id
        where s.start_time between now() and now() + interval %s
    """, [check_time])

    for booking in bookings_data_for_creator:
        notification_data_list.append(prepare_notification(booking))


    bookings_data_for_booker = execute_query("""
        select b.id, e.title, coalesce(NULLIF(cp.name, ''), cp.slug) as creator, 
            coalesce(NULLIF(bp.name,''), bp.slug) as booker, cf.reg_id as creator_device_id,
            (EXTRACT(EPOCH FROM (s.start_time - now()))/60)::numeric::integer as time_remaining
        from booking_eventbooking b
        inner join booking_eventslot s on s.id = b.event_slot_id
        inner join booking_event e on e.id = b.event_id
        left join jarvis_fcmdevice cf on cf.user_id = e.creator_id
        left join forum_user_userprofile cp on cp.user_id = e.creator_id
        left join forum_user_userprofile bp on bp.user_id = b.user_id
        where s.start_time between now() and now() + interval %s
    """, [check_time])

    for booking in bookings_data_for_booker:
        notification_data_list.append(prepare_notification(booking))

    send_notification_in_parallel(notification_data_list)