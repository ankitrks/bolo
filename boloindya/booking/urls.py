from django.conf.urls import include, url
from .views import BookingPaymentRedirectView
from forum.booking.views import BookingCallView

urlpatterns = [
    url(r'^(?P<booking_id>[\d]+)/pay$', BookingPaymentRedirectView.as_view()),
    url(r'^(?P<channel_id>[0-9a-f-]+\w+)$', BookingCallView.as_view(), name='booking-call-view'),
]
