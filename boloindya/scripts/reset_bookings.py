
import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from multiprocessing import Process, Pool

from django.db import connections

from payment.razorpay import get_order_payments
from payment.helpers import execute_query

def update_booking_state(slot_id, booking_id, order_id):
    order_status = get_order_payments(order_id)
    for payment in order_status.get('items'):
        if payment.get('status') == 'captured':
            return {'status': 'paid', 'transaction_id': payment.get('id'), 'args': (slot_id, booking_id, order_id)}
    return {'status': 'failed', 'args': (slot_id, booking_id, order_id)}

def update_paid_bookings(payment_info_list):
    values = ["(%s, '%s')"%(value.get('booking_id'), value.get('transaction_id')) for value in payment_info_list]

    execute_query("""
        UPDATE booking_eventbooking
        SET 
            transaction_id = payment.txn_id,
            payment_status = 'success',
            state = 'booked'
        FROM (VALUES %s) as payment(id, txn_id)
        WHERE booking_eventbooking.id = payment.id
        RETURNING booking_eventbooking.id;
    """%(','.join(values),), [])

    execute_query("""
        UPDATE booking_eventslot slot
        SET
            state = 'booked'
        FROM booking_eventbooking booking
        WHERE booking.id in %s and booking.event_slot_id = slot.id
        RETURNING booking.id
    """, [tuple([value.get('booking_id') for value in payment_info_list])])

def update_failed_bookings(slot_ids):
    execute_query("""
        UPDATE booking_eventslot
        SET 
            state = 'available'
        WHERE id in %s
        RETURNING id
    """, [tuple(slot_ids)])

def run():
    pending_bookings = execute_query("""
        SELECT slot.id as slot_id, booking.id as booking_id, booking.payment_gateway_order_id as order_id
        FROM booking_eventbooking booking
        INNER JOIN booking_eventslot slot on slot.id = booking.event_slot_id
        WHERE 
            booking.state = 'draft' AND 
            booking.payment_status != 'success' AND
            slot.state = 'hold' AND
            booking.created_at < now() - interval '12 minutes'
    """, [])

    pool = Pool(processes=8)
    results = []
    for booking in pending_bookings:
        results.append(pool.apply_async(update_booking_state, args=(
                                booking.get('slot_id'),
                                booking.get('booking_id'),
                                booking.get('order_id')
                            )))

    pool.close()
    pool.join()

    paid_bookings = []
    failed_bookings = []

    for result in results:
        resp = result._value
        if resp.get('status') == 'paid':
            paid_bookings.append({
                'transaction_id': resp.get('transaction_id'),
                'booking_id': resp.get('args')[1]
            })
        else:
            failed_bookings.append(resp.get('args')[0])

    print "paid bookings", paid_bookings
    print "failed booking", failed_bookings

    if paid_bookings:
        update_paid_bookings(paid_bookings)

    if failed_bookings:
        update_failed_bookings(failed_bookings)