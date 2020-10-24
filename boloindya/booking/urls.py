from django.conf.urls import include, url
from .views import BookingPaymentRedirectView

urlpatterns = [
	url(r'^(?P<booking_id>[\d]+)/pay$', BookingPaymentRedirectView.as_view()),
]
