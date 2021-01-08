from django.db import connections
from datetime import datetime

from tasks import webengage_event, send_fcm_push_notifications
from dynamodb_api import create as dynamodb_create

from booking.models import EventBookingEvent

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def execute_query(query, params):
    cursor = connections['default'].cursor()
    print "query", cursor.mogrify(query, params)
    cursor.execute(query, params)
    return dictfetchall(cursor)


def get_user_info(user_id):
    return execute_query("""
        SELECT COALESCE(p.name, u.username) as name, p.id, p.mobile_no as mobile, u.email
        FROM forum_user_userprofile p 
        INNER JOIN auth_user u on u.id = p.user_id
        WHERE user_id = %s
    """, [user_id])


def get_booking_info(order_id):
    return execute_query("""
        SELECT profile.name as name, u.email as email, profile.mobile_no as mobile, event.price as amount,
                booking.payment_gateway_order_id as order_id
        FROM booking_eventbooking booking
        INNER JOIN forum_user_userprofile profile ON profile.user_id = booking.user_id
        INNER JOIN auth_user u ON u.id = profile.user_id
        INNER JOIN booking_event event ON event.id = booking.event_id
        WHERE booking.payment_gateway_order_id = %s
    """, [order_id])


def get_ad_order_info(order_id):
    return execute_query("""
        SELECT a.name, a.mobile, o.amount, o.payment_gateway_order_id as order_id, u.email as email
        from advertisement_order o
        inner join advertisement_address a on a.id = o.shipping_address_id
        inner join auth_user u on u.id = o.user_id
        where o.payment_gateway_order_id = %s
    """, [order_id])

    
def update_booking_payment_status(order_id, payment_status, transaction_id=None):
    if payment_status == 'success':
        result = execute_query("""
            UPDATE booking_eventbooking
            SET 
                transaction_id = %s,
                payment_status = 'success',
                state = 'booked'
            WHERE payment_gateway_order_id = %s
            RETURNING id;
            UPDATE booking_eventslot slot
            SET
                state = 'booked'
            FROM booking_eventbooking booking
            WHERE booking.payment_gateway_order_id = %s and booking.event_slot_id = slot.id
            RETURNING booking.id;
            INSERT into forum_topic_notification
                SELECT nextval('forum_topic_notification_id_seq'), now() as created_at, now() as modified_at, true as is_active, 
                        '11' as notification_type, false as is_read, null as read_at, b.id as topic_id, e.creator_id as for_user_id, 
                        ct.id as topic_type_id, b.user_id as user_id, 0 as status
                FROM booking_eventbooking b
                INNER JOIN booking_event e on e.id = b.event_id
                INNER JOIN django_content_type ct on ct.app_label = 'booking' and ct.model = 'eventbooking'
                WHERE b.payment_gateway_order_id = %s
            RETURNING forum_topic_notification.id;
            SELECT b.id, e.title, coalesce(NULLIF(cp.name, ''), cp.slug) as creator, 
                coalesce(NULLIF(bp.name,''), bp.slug) as booker, cf.reg_id as creator_device_id,
                (EXTRACT(EPOCH FROM (s.start_time - now()))/60)::numeric::integer as time_remaining,
                e.price as event_price, e.id as event_id, b.user_id as booker_id
            FROM booking_eventbooking b
            INNER JOIN booking_eventslot s on s.id = b.event_slot_id
            INNER JOIN booking_event e on e.id = b.event_id
            LEFT JOIN jarvis_fcmdevice cf on cf.user_id = e.creator_id
            LEFT JOIN forum_user_userprofile cp on cp.user_id = e.creator_id
            LEFT JOIN forum_user_userprofile bp on bp.user_id = b.user_id
            WHERE b.payment_gateway_order_id = %s
        """, [transaction_id, order_id, order_id, order_id, order_id])

        if result:
            booking_info = result[0]

        if booking_info.get('creator_device_id'):
            send_fcm_push_notifications(
                booking_info.get('creator_device_id'), 
                "Bolo Meet Booking Alert",
                "%s has booked your session '%s'"%(booking_info.get('booker'), booking_info.get('title')), 
            )

        try:
            data = {
                'event_id': booking_info.get('event_id'),
                'user_id': booking_info.get('booker_id'),
                'created_at': datetime.now(),
                'event': 'confirm_booking',
                'data': {
                    'price': booking_info.get('event_price')
                }
            }
            dynamodb_create(EventBookingEvent, data)
        except Exception as e:
            print "While updating event booking event", str(e)

    elif payment_status == 'failed':
        execute_query("""
            UPDATE booking_eventbooking
            SET 
                payment_status = 'failed'
            WHERE payment_gateway_order_id = %s
            RETURNING id
        """, [order_id])

    booking_event_data = get_event_webengage_data(order_id)
    print "booking_event_data", order_id, booking_event_data
    if len(booking_event_data) > 0:
        booking_event_data = booking_event_data[0]

    webengage_event.delay({
        "userId": booking_event_data.pop('booking_user_id'),
        "eventName": "Booking Payment %s"%payment_status.capitalize(),
        "eventData": booking_event_data
    })


def update_ad_order_payment_status(order_id, payment_status, transaction_id=None):
    if payment_status == "success":
        execute_query("""
            UPDATE advertisement_order
            SET 
                payment_status = 'success',
                state = 'order_placed'
            WHERE payment_gateway_order_id = %s
            RETURNING id;
        """, [order_id])

    elif payment_status == "failed":
        # execute_query("""
        #     UPDATE advertisement_order
        #     SET 
        #         payment_status = 'failed',
        #     WHERE payment_gateway_order_id = %s
        #     RETURNING id;
        # """, [order_id])
        pass

def get_event_webengage_data(order_id):
    return execute_query("""
        SELECT b.user_id as booking_user_id, b.id as event_booking_id, e.id as event_id, s.id as event_slot_id, s.state as slot_status,
            b.state as booking_status, b.payment_status as payment_status, b.user_id as creator_id,
            e.creator_id as booker_id, to_char(s.start_time, 'YYYY-MM-DD HH24:MI:SS') as slot_start_time,
            to_char(s.end_time, 'YYYY-MM-DD HH24:MI:SS') as slot_end_time
        FROM booking_eventbooking b
        INNER JOIN booking_eventslot s on s.id = b.event_slot_id
        INNER JOIN booking_event e on e.id = b.event_id
        WHERE b.payment_gateway_order_id = %s
    """, [order_id])