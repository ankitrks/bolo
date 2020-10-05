from django.conf.urls import include, url

from rest_framework import routers

from bipayments.payout.views import ScheduledPaymentModelViewSet, TransactionListAPIView, PayAPIView

router = routers.SimpleRouter()

router.register('schedule-payment', ScheduledPaymentModelViewSet)

urlpatterns = [
    url('beneficiary/<int:beneficiary>/', include(router.urls)),
    url('transaction/', TransactionListAPIView.as_view()),
    url('pay', PayAPIView.as_view()),
    url('', include(router.urls))
]


