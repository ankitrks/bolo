from django.conf.urls import include, url
from .views import *

urlpatterns = [
	url(r'^bookings/$', BookingDetails.as_view()),
	url(r'^user_bookings/', UserBookingList.as_view()),
	url(r'^myslots/',MySlotsList.as_view()),
	url(r'^payout/tnc/', PayOutConfigDetails.as_view()),
	url(r'^events/$', EventDetails.as_view()),
	url(r'^event/slots/$', EventSlotsDetails.as_view()),
	url(r'^event/bookings/$', EventBookingDetails.as_view())
]
