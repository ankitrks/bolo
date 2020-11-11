from django.conf.urls import include, url

from rest_framework import routers

from advertisement.views import (AdDetailAPIView, ReviewListAPIView, CityListAPIView, ProductDetailAPIView,
                                    AddressViewset, OrderViewset, OrderCreateAPIView, AdEventCreateAPIView,
                                    GetAdForUserAPIView, DashBoardCountAPIView, JarvisOrderViewset, JarvisAdViewset)

router = routers.SimpleRouter()
router.register('address', AddressViewset)
router.register('order', OrderViewset)
# router.register('ad', AdViewset)

jarvis_router = routers.SimpleRouter()
jarvis_router.register('order', JarvisOrderViewset)
jarvis_router.register('ad', JarvisAdViewset)

urlpatterns = router.urls

urlpatterns += [
    url(r'^(?P<pk>\d+)$', AdDetailAPIView.as_view()),
    url(r'^(?P<pk>\d+)/product$', ProductDetailAPIView.as_view()),
    url(r'^product/(?P<product_id>\d+)/review$', ReviewListAPIView.as_view()),
    url(r'^city-list$', CityListAPIView.as_view()),
    url(r'^place-order$', OrderCreateAPIView.as_view()),
    url(r'^event$', AdEventCreateAPIView.as_view()),
    url(r'^for-user$', GetAdForUserAPIView.as_view()),
    url(r'^dashboard-counts$', DashBoardCountAPIView.as_view()),
    url(r'^jarvis/', include(jarvis_router.urls)),
]

print "urlpatterns", urlpatterns


