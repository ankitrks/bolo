from __future__ import unicode_literals
from django.conf.urls import url, include
from jarvis import views
urlpatterns = [
    url(r'^$',views.home,name='jarvis-home'),
    url(r'^importcsv/$',views.importcsv,name = 'import-csv'),
    url(r'^getcsvdata/$',views.getcsvdata),
    url(r'^csvupload/$',views.uploaddata),
    url(r'^geturl/$',views.geturl),
    url(r'^get_kyc_user_list/$',views.get_kyc_user_list),
    url(r'^single_kyc/$',views.get_kyc_of_user)
]