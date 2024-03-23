from django.contrib import admin
from django.conf.urls import include, url

from payment.payout.views import PaymentStatusView, TransactionView, ScheduledPaymentView

urlpatterns = [
    url(r'^$', PaymentStatusView.as_view()),
    url(r'^transaction/$', TransactionView.as_view(), name='all_payments'),
    url(r'^scheduled-payments$', ScheduledPaymentView.as_view(), name='scheduled_payments')
]