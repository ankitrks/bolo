from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError

from payment.payout.models import Transaction

class Command(BaseCommand):
    help = "Create payments entries"


    def handle(self, *args, **options):
        for transaction in Transaction.object.filter(
                                state='draft',
                                transaction_date=datetime.now().date()
                            ):
            transaction.make_payment()

        

