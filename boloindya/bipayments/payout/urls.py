from django.contrib import admin
from django.conf.urls import include, url

from bipayments.payout.views import PaymentStatusView, TransactionView, ScheduledPaymentView

urlpatterns = [
    url('', PaymentStatusView.as_view()),
    url('transaction/', TransactionView.as_view()),
    url('scheduled-payments', ScheduledPaymentView.as_view(), name='scheduled_payments')
]