from django.conf.urls import include, url

from forum.booking.views import BookingCallView

urlpatterns = [
    url(r'^(?P<channel_id>\w+)$', BookingCallView.as_view(), name='booking-call-view'),
]
