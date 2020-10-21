import requests
import hmac
import hashlib

from django.conf import settings

razorpay_credentials = settings.RAZORPAY

from redis_utils import get_redis, set_redis, incr_redis

BASE_URL = "https://api.razorpay.com/v1"

def get_receipt():
    receipt_number = get_redis('RAZORPAY_RECEIPT_NO')
    if not receipt_number:
        set_redis('RAZORPAY_RECEIPT_NO', 1)
        receipt_number = 1
    else:
        incr_redis('RAZORPAY_RECEIPT_NO')

    return 'receipt_no_%s'%receipt_number 


def get_auth():
    return (razorpay_credentials.get('USERNAME'), razorpay_credentials.get('PASSWORD'))


def razorpay_get(url):
    response = requests.get(url, auth=get_auth())

    if response.ok:
        return response.json()
    else:
        print response.text
    

def create_order(amount, currency="INR", receipt=None, notes=None):
    url = BASE_URL + '/orders'
    post_data = {
        "amount": int(amount) * 100,
        "currency": currency,
        "receipt": receipt if receipt else get_receipt(),
        "payment_capture": 1,
        "notes": notes if notes else {}
    }
    print "post data", post_data
    response = requests.post(url, data=post_data, auth=(razorpay_credentials.get('USERNAME'), razorpay_credentials.get('PASSWORD')))
    if response.ok:
        return response.json()
    else:
        print response.text


def get_order(order_id):
    url = ''.join([BASE_URL, '/orders/', order_id])
    response = requests.get(url, auth=get_auth())

    if response.ok:
        return response.json()
    else:
        print response.text

def get_order_payments(order_id):
    url = ''.join([BASE_URL, '/orders/', order_id, '/payments'])
    return razorpay_get(url)


def is_signature_verified(order_id, payment_id, signature):
    if signature == hmac.new(
                        razorpay_credentials.get('PASSWORD'), 
                        msg=str(order_id) + "|" + str(payment_id), 
                        digestmod=hashlib.sha256).hexdigest():
        return True
    return False