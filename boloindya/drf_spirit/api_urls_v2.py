from django.conf.urls import include, url

from drf_spirit.views import PopularVideoBytesV2, ReportListAPIView, ReportCreateAPIView

urlpatterns = [
    url(r'^get_popular_video_bytes/$', PopularVideoBytesV2.as_view()),
    url(r'^report/items/$', ReportListAPIView.as_view()),
    url(r'^(?P<target>video|user|music)/(?P<id>\d+)/report/$', ReportCreateAPIView.as_view()),
]


