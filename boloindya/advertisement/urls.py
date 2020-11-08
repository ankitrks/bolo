from django.conf.urls import include, url
from .views import OrderPaymentRedirectView

urlpatterns = [
    url(r'^order/(?P<order_id>[\d]+)/pay/$', OrderPaymentRedirectView.as_view()),
]
