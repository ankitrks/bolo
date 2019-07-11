from __future__ import unicode_literals
from django.conf.urls import url, include
from jarvis import views
urlpatterns = [
    url(r'^$',views.home,name='jarvis-home'),
    url(r'^importcsv/$',views.importcsv,name = 'import-csv'),
    url(r'^getcsvdata/$',views.getcsvdata),
    url(r'^csvupload/$',views.uploaddata),
]