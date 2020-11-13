from django.conf.urls import include, url

from drf_spirit.views import PopularVideoBytesV2

urlpatterns = [
    url(r'^get_popular_video_bytes/$', PopularVideoBytesV2.as_view()),
]


