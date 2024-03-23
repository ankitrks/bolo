import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from datetime import datetime, timedelta

from payment.payout.models import Transaction


def run():
    for transaction in Transaction.objects.filter(state='pending'):
        transaction.check_status()