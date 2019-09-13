from __future__ import unicode_literals
from django.conf.urls import url, include
from jarvis import views
urlpatterns = [
    url(r'^$',views.home,name='jarvis-home'),
    url(r'^importcsv/$',views.importcsv,name = 'import-csv'),
    url(r'^getcsvdata/$',views.getcsvdata),
    url(r'^csvupload/$',views.uploaddata),
    url(r'^geturl/$',views.geturl),
    url(r'^uploadvideofile/$',views.uploadvideofile,name = 'uploadvideofile'),
    url(r'^upload_n_transcode/$',views.upload_n_transcode),
    url(r'^upload_details/$',views.upload_details),
    url(r'^uploaded_list/$',views.uploaded_list),
]