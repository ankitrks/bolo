import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from datetime import datetime, timedelta

from payment.payout.models import ScheduledPayment


def run():
    today = datetime.now().date()
    for schedule_payment in ScheduledPayment.objects.filter(payment_date=today.day, is_active=True):
        beneficiary = schedule_payment.beneficiary
        beneficiary.transfer(schedule_payment.amount)