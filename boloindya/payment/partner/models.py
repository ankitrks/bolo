import json
from datetime import datetime

from simple_history.models import HistoricalRecords

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.conf import settings

from rest_framework import serializers

from payment.paytm_api import generate_order_id, verify_beneficiary, wallet_transfer, account_transfer, upi_transfer

from payment.payout.models import Transaction

from payment.utils import log_message

PAYMENT_METHOD_CHOICES = (
    ('paytm_wallet', 'PayTM Wallet'),
    ('upi', 'UPI'),
    ('account_transfer', 'Bank Account Transfer')
)

VERIFICATION_STATUS_CHOICES = (
    ('pending', 'Pending'),
    ('verified', 'Verified'),
    ('failed', 'Failed')
)

BENEFICIARY_TYPE_CHOICES = (
    ('emp_salary', 'Employee Salary'),
    ('creator_payout', 'Creator Payout')
)


class Beneficiary(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    boloindya_id = models.IntegerField(_("BoloIndya ID"), blank=True, null=True)
    payment_method = models.CharField(_("Payment Method"), choices=PAYMENT_METHOD_CHOICES, max_length=20)
    paytm_number = models.CharField(_("Paytm Number"), max_length=20, blank=True, null=True)
    upi = models.CharField(_("UPI"), max_length=50, null=True, blank=True)
    account_number = models.CharField(_("Account Number"), null=True, blank=True, max_length=50)
    bank_ifsc = models.CharField(_("Bank IFSC"), max_length=30, null=True, blank=True)
    verification_status = models.CharField(_("Bank IFSC"), max_length=30, 
                                choices=VERIFICATION_STATUS_CHOICES, default='pending')
    is_active = models.BooleanField(_("Is active"), default=True)
    verification_txn_id = models.CharField(_("Verification TXN ID"), max_length=30, null=True, blank=True)
    created_by = models.ForeignKey(User, related_name='created_beneficiary')
    created_at = models.DateTimeField(_("Created At"), auto_now_add=True, auto_now=False)
    modified_at = models.DateTimeField(_("Created At"), auto_now_add=False, auto_now=True)
    modified_by = models.ForeignKey(User, related_name='modified_beneficiary')
    beneficiary_type = models.CharField(_("Beneficiary Type"), max_length=30, choices=BENEFICIARY_TYPE_CHOICES, default='creator_payout')
    history = HistoricalRecords()

    def __str__(self):
        return self.name

    def verify(self):
        if self.payment_method == 'account_transfer':
            self.verification_txn_id = generate_order_id()
            response = verify_beneficiary(self.verification_txn_id, beneficiaryAccount, beneficiaryIFSC)

            if response.get('status') in ('SUCCESS', 'ACCEPTED'):
                self.verification_status = 'verified'
            elif response.get('status') == 'FAILURE':
                self.verification_status = 'failed'
        else:
            self.verification_status = 'verified'

        self.save()


    def transfer(self, amount):
        if not settings.ALLOW_PAYMENT_TRANSACTION:
            raise serializers.ValidationError("Transaction not allowed!!")

        if not self.is_active:
            raise serializers.ValidationError("Beneficiary is not active!!")

            
        if self.verification_status != 'verified':
            raise serializers.ValidationError("Beneficiary is not verified!!")


        txn_id = generate_order_id()
        if self.payment_method == 'paytm_wallet':
            response = wallet_transfer(txn_id, self.paytm_number, amount)
        elif self.payment_method == 'account_transfer':
            response = account_transfer(txn_id, self.account_number, self.bank_ifsc, amount)
        elif self.payment_method == 'upi':
            response = upi_transfer(txn_id, self.upi, amount)

        state = 'draft'

        if response.get('status') == 'SUCCESS':
            state = 'success'
            log_message("Payment success for beneficiary %s of amount %s.\nPayment Gateway Response\n%s"%(\
                        self.name, amount, json.dumps(response, indent=4)), 
                    "Payment Success", 'transaction', True)
        elif response.get('status') == 'FAILURE':
            state = 'failed'
            log_message("Payment failed for beneficiary %s of amount %s.\nPayment Gateway Response\n%s"%(\
                        self.name, amount, json.dumps(response, indent=4)), 
                    "Payment Failed", 'transaction', True)
        else:
            state = 'pending'

        print "creating transaction", Transaction.objects.create(
            beneficiary=self,
            amount=amount,
            state=state,
            pg_state=response.get('status'),
            transaction_id=txn_id,
            payment_gateway_response=json.dumps(response),
            transaction_date=datetime.now()
        )

        return True


class TopUser(models.Model):
    name = models.CharField(_("Name"), max_length=100)
    boloindya_id = models.IntegerField(_("BoloIndya ID"), default=0)
    username = models.CharField(_("Username"), max_length=100)
    agg_month = models.DateField(_("Agg Month"))
    video_count = models.IntegerField(_("Video Count"), default=0)
    follower_count = models.IntegerField(_("Follower Count"), default=0)
    playtime = models.FloatField(_("Playtime Count"), default=0)
    view_count = models.IntegerField(_("View Count"), default=0)


