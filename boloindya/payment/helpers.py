

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


def get_booking_info(booking_id):
    return execute_query("""
        SELECT user_id, amount, payment_gateway_order_id
        FROM forum_eventbooking booking
        WHERE id = %s
    """, [booking_id])
    