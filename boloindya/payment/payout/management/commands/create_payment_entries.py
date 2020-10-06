from datetime import datetime, timedelta

from django.core.management.base import BaseCommand, CommandError

from payment.payout.models import ScheduledPayment, Transaction

class Command(BaseCommand):
    help = "Create payments entries"


    def handle(self, *args, **options):
        next_date = (datetime.now() + timedelta(days=1)).date()
        transactions = []

        for scheduled_payment in ScheduledPayment.objects.filter(is_active=True, 
                            added_for_payment=False, payment_date=next_date.day):
            print("scheduled_payment", scheduled_payment)
            transactions.append(Transaction(
                beneficiary=scheduled_payment.beneficiary,
                amount=scheduled_payment.amount,
                state='draft',
                transaction_date=next_date
            ))

        Transaction.objects.bulk_create(transactions)

        

