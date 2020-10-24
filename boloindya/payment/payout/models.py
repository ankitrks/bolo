import jsonfield

from simple_history.models import HistoricalRecords

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import ugettext_lazy as _


PAYMENT_STATE_CHOICES = (
    ('draft', 'Draft'),
    ('timeout', 'Timeout'),
    ('success', 'Success'),
    ('failed', 'Failed'),
    ('cancel', 'Cancelled')
)

PAYMENT_GATEWAY_STATE_CHOICE = (
    ('pending', 'Pending'),
    ('success', 'Success'),
    ('failed', 'Failed')
)


class ScheduledPayment(models.Model):
    beneficiary = models.ForeignKey('partner.Beneficiary', on_delete=models.CASCADE, related_name='scheduled_payments')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='created_payments', null=True, blank=True)
    created_at = models.DateTimeField(_("Created at"), auto_now_add=True, auto_now=False)
    amount = models.FloatField(_("Amount"))
    payment_date = models.IntegerField(_("Payment Day"))
    modified_at = models.DateTimeField(_("Modified at"), null=True, blank=True)
    is_active = models.BooleanField(_("Is Active"), default=True)
    added_for_payment = models.BooleanField(_("Added for Payment"), default=False)
    history = HistoricalRecords()



class Transaction(models.Model):
    beneficiary = models.ForeignKey('partner.Beneficiary', blank=True, null=True, on_delete=models.SET_NULL, related_name='translation')
    amount = models.FloatField(_("Amount"))
    state = models.CharField(_("State"), choices=PAYMENT_STATE_CHOICES, default='draft', max_length=20)
    pg_state = models.CharField(_("PG State"), choices=PAYMENT_GATEWAY_STATE_CHOICE, null=True, blank=True, max_length=20)
    transaction_id = models.CharField(_("Transaction ID"), null=True, blank=True, max_length=50)
    payment_gateway_response = jsonfield.JSONField(_("Payment Gateway Response"))
    transaction_date = models.DateTimeField(_("Transaction DateTime"), null=True, blank=True)

    def make_payment(self):
        self.state = 'success'
        self.save()



class TransactionState(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='states')
    state = models.CharField(_("State"), choices=PAYMENT_STATE_CHOICES, default='draft', max_length=20)
    datetime = models.DateTimeField(_("DateTime"), auto_now_add=True, auto_now=False)


class TransactionPGState(models.Model):
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='pg_states')
    state = models.CharField(_("State"), choices=PAYMENT_GATEWAY_STATE_CHOICE, default='draft', max_length=20)
    datetime = models.DateTimeField(_("DateTime"), auto_now_add=True, auto_now=False) 


