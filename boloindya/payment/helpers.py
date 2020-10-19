

from django.db import connections

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def execute_query(query, params):
    cursor = connections['default'].cursor()
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
    
def update_booking_payment_status(order_id, payment_status, transaction_id=None):
    if payment_status == 'success':
        execute_query("""
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
            RETURNING booking.id
        """, [transaction_id, order_id, order_id])
    elif payment_status == 'failed':
        execute_query("""
            UPDATE booking_eventbooking
            SET 
                payment_status = 'failed'
                state = 'cancelled'
            WHERE payment_gateway_order_id = %s
            RETURNING id
        """, [order_id])