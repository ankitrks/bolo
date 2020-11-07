from django.conf.urls import include, url

# from rest_framework import routers

# router = routers.SimpleRouter()

# router.register('beneficiary', BeneficiaryViewSet)

# urlpatterns = router.urls
from advertisement.views import AdDetailAPIView, ReviewListAPIView, OrderListCreateAPIView, CityListAPIView

urlpatterns = [
    url(r'^(?P<pk>\d+)$', AdDetailAPIView.as_view()),
    url(r'^product/(?P<pk>\d+)/review$', ReviewListAPIView.as_view()),
    url(r'^order$', OrderListCreateAPIView.as_view()),
    url(r'^city-list$', CityListAPIView.as_view()),
]


