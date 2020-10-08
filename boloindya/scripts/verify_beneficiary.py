import os
import sys

os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

from datetime import datetime, timedelta

from payment.partner.models import Beneficiary


def run():
    today = datetime.now().date()
    for beneficiary in Beneficiary.objects.filter(is_active=True, verification_status='pending', 
                created_at__lte=datetime.now() - timedelta(minutes=30)):
        print(" beneficiary", beneficiary)
        beneficiary.verify()