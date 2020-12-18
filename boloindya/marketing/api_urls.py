from django.conf.urls import include, url

from rest_framework import routers

from marketing.api_views import AdStatsListAPIView, AdCreatorAPIView, AdBrandAPIView, AdInstallChartDataAPIView

urlpatterns = [
    url(r'^jarvis/ad/stats/$', AdStatsListAPIView.as_view()),
    url(r'^jarvis/ad/creator/$', AdCreatorAPIView.as_view()),
    url(r'^jarvis/ad/brand/$', AdBrandAPIView.as_view()),
    url(r'^jarivs/ad/install/chart/$', AdInstallChartDataAPIView.as_view()),
]