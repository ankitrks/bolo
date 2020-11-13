import requests
import json
from datetime import datetime
from paytmchecksum import PaytmChecksum

from django.conf import settings


import connection

redis_cli = connection.redis()

PAYTM_CONFIG = settings.PAYTM_CONFIG
MID = PAYTM_CONFIG.get('MID')
MERCHANT_KEY = PAYTM_CONFIG.get('MERCHANT_KEY')
subwalletGuid = PAYTM_CONFIG.get('subwalletGuid')
BASE_URL = PAYTM_CONFIG.get('BASE_URL')


def generate_order_id():
    key = settings.PAYTM_TXN_COUNTER_KEY
    counter = redis_cli.get(key)
    if not counter:
        redis_cli.set(settings.PAYTM_TXN_COUNTER_KEY, 1)
        counter = u'1'
    redis_cli.incr(key)
    return 'TXN_%s'%counter.decode().zfill(6)


def paytm_api_request(path, post_data, x_checksum):
    url = BASE_URL + path
    print "url", url, post_data, MID
    return requests.post(url,  data=post_data, 
                        headers={
                            "Content-type": "application/json", 
                            "x-mid": MID, 
                            "x-checksum": x_checksum
                        }).json()


def verify_beneficiary(orderId, beneficiaryAccount, beneficiaryIFSC):
    paytmParams = {
        "orderId"           : orderId,
        "subwalletGuid"     : subwalletGuid,
        "beneficiaryAccount": beneficiaryAccount,
        "beneficiaryIFSC"   : beneficiaryIFSC
    }
    post_data = json.dumps(paytmParams)

    return paytm_api_request('/beneficiary/validate', post_data,
                        PaytmChecksum.generateSignature(post_data, MERCHANT_KEY))


def wallet_transfer(orderId, beneficiaryPhoneNo, amount):
    paytmParams = {
        "subwalletGuid"      : subwalletGuid,
        "orderId"            : orderId,
        "beneficiaryPhoneNo" : beneficiaryPhoneNo,
        "amount"             : amount
    }
    post_data = json.dumps(paytmParams)

    return paytm_api_request('/disburse/order/wallet/allowance', post_data,
                        PaytmChecksum.generateSignature(post_data, MERCHANT_KEY))


def account_transfer(orderId, beneficiaryAccount, beneficiaryIFSC, amount):
    paytmParams = {
        "subwalletGuid"      : subwalletGuid,
        "orderId"            : orderId,
        "beneficiaryAccount" : beneficiaryAccount,
        "beneficiaryIFSC"    : beneficiaryIFSC,
        "amount"             : amount,
        "purpose"            : "SALARY_DISBURSEMENT",
        "date"               : datetime.strftime(datetime.now(),'%Y-%m-%d'),
        "transferMode"       : "IMPS"
    }
    post_data = json.dumps(paytmParams)

    return paytm_api_request('/disburse/order/bank', post_data,
                        PaytmChecksum.generateSignature(post_data, MERCHANT_KEY))


def upi_transfer(orderId, upiId, amount):
    paytmParams = {
        "subwalletGuid"      : subwalletGuid,
        "orderId"            : orderId,
        "beneficiaryAccount" : beneficiaryAccount,
        "beneficiaryIFSC"    : beneficiaryIFSC,
        "amount"             : amount,
        "purpose"            : "SALARY_DISBURSEMENT",
        "date"               : datetime.now().strptime('%Y-%m-%d'),
        "transferMode"       : "IMPS"
    }
    post_data = json.dumps(paytmParams)

    return paytm_api_request('/disburse/order/bank', post_data,
                        PaytmChecksum.generateSignature(post_data, MERCHANT_KEY))



