from django.conf.urls import include, url
from .views import EventDetailsV2

urlpatterns = [
	url(r'^events/$', EventDetailsV2.as_view()),
	# url(r'^event/bookings/$', EventBookingDetails.as_view())
]