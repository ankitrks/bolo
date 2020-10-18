from django.conf.urls import include, url

urlpatterns = [
	url(r'payin/', include('payment.payin.urls')),
]

