from django.conf.urls import include, url

from rest_framework import routers

from marketing.api_views import AdStatsListAPIView, AdCreatorAPIView, AdBrandAPIView, AdInstallChartDataAPIView, DashboadCountAPIView

urlpatterns = [
    url(r'^dashboard/counts/$', DashboadCountAPIView.as_view()),
    url(r'^ad/stats/$', AdStatsListAPIView.as_view()),
    url(r'^ad/creator/$', AdCreatorAPIView.as_view()),
    url(r'^ad/brand/$', AdBrandAPIView.as_view()),
    url(r'^ad/install/chart/$', AdInstallChartDataAPIView.as_view()),
]