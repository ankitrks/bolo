from django.conf.urls import include, url

urlpatterns = [
	url(r'', include('payment.payin.urls')),
]

