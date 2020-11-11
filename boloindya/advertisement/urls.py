from django.conf.urls import include, url
from .views import OrderPaymentRedirectView, OrderTemplateView, AdTemplateView, ProductTemplateView

urlpatterns = [
    url(r'^order/(?P<order_id>[\d]+)/pay/$', OrderPaymentRedirectView.as_view()),
    url(r'^$', AdTemplateView.as_view()),
    url(r'^order/$', OrderTemplateView.as_view()),
    url(r'^product/$', ProductTemplateView.as_view()),
]
