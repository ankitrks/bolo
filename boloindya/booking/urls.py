from django.conf.urls import include, url
from .views import *

urlpatterns = [
	url(r'^bookings/$', BookingDetails.as_view()),
	url(r'^user_bookings/', UserBookingList.as_view())
]
