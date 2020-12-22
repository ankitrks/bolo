from django.conf.urls import include, url

from rest_framework import routers

from marketing.api_views import AdStatsListAPIView, AdCreatorAPIView, AdBrandAPIView, AdInstallChartDataAPIView, AdInstallDashboadCountAPIView

urlpatterns = [
    url(r'^dashboard/counts/$', AdInstallDashboadCountAPIView.as_view()),
    url(r'^ad/stats/$', AdStatsListAPIView.as_view()),
    url(r'^ad/creator/$', AdCreatorAPIView.as_view()),
    url(r'^ad/brand/$', AdBrandAPIView.as_view()),
    url(r'^ad/install/chart/$', AdInstallChartDataAPIView.as_view()),
]