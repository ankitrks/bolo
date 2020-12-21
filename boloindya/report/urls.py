from django.conf.urls import include, url
from django.contrib.admin.views.decorators import staff_member_required

from .views import AdOrderDownload, AdInstallStatsDownloadView

urlpatterns = [
    url(r'^ad/order/download$', staff_member_required(AdOrderDownload.as_view())),
    url(r'^ad/install/stats/download$', staff_member_required(AdInstallStatsDownloadView.as_view())),
]
