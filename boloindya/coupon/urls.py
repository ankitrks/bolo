from django.conf.urls import include, url
from .views import *

urlpatterns = [
	url(r'^get_coupons/$', get_coupons),
	url(r'^get_user_coupons/', get_user_coupons)
]
