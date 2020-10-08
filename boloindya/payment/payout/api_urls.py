from django.conf.urls import include, url

from rest_framework import routers

from payment.payout.views import ScheduledPaymentModelViewSet, TransactionListAPIView, PayAPIView

router = routers.SimpleRouter()

router.register('schedule-payment', ScheduledPaymentModelViewSet)

urlpatterns = [
    url(r'^beneficiary/(?P<beneficiary>\d+)/', include(router.urls)),
    url(r'^beneficiary/(?P<beneficiary>\d+)/pay$', PayAPIView.as_view()),
    url(r'^transaction/$', TransactionListAPIView.as_view()),
    url(r'^pay$', PayAPIView.as_view()),
    url(r'^', include(router.urls))
]

print router.urls


