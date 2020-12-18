from django.conf.urls import include, url
from django.contrib.admin.views.decorators import staff_member_required

from .web_views import AdStatsDashboardView

urlpatterns = [
    url(r'^ad/install/stats/$', AdStatsDashboardView.as_view()),
]

print "urlpattern == = ", urlpatterns[0].__dict__