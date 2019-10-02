from __future__ import unicode_literals
from django.conf.urls import url, include
from jarvis import views
urlpatterns = [
    url(r'^$',views.home,name='jarvis-home'),
    url(r'^importcsv/$',views.importcsv,name = 'import-csv'),
    url(r'^getcsvdata/$',views.getcsvdata),
    url(r'^csvupload/$',views.uploaddata),
    url(r'^geturl/$',views.geturl),
    url(r'^get_kyc_user_list/$',views.get_kyc_user_list,name='get_kyc_user_list'),
    url(r'^single_kyc/$',views.get_kyc_of_user,name='get_kyc_of_user'),
    url(r'^get_secret_file/$',views.SecretFileView, name='SecretFileView'),
    url(r'^get_encashable_detail/$',views.get_encashable_detail, name='get_encashable_detail'),
    url(r'^get_single_encash_detail/$',views.get_single_encash_detail, name='get_single_encash_detail'),
    url(r'^calculate_encashable_detail/$',views.calculate_encashable_detail, name='calculate_encashable_detail'),
    url(r'^bolo_payment/$',views.PaymentView.as_view(),name='bolo_payment'),
    url(r'^bolo_cycle/$',views.PaymentCycleView.as_view(),name='bolo_cycle'),
    url(r'^accept_kyc/$',views.accept_kyc, name='accept_kyc'),
    url(r'^reject_kyc/$',views.reject_kyc, name='reject_kyc'),
    url(r'^uploadvideofile/$',views.uploadvideofile,name = 'uploadvideofile'),
    url(r'^upload_n_transcode/$',views.upload_n_transcode),
    url(r'^upload_details/$',views.upload_details),
    url(r'^uploaded_list/$',views.uploaded_list),
    url(r'^get_submitted_kyc_user_list/$',views.get_submitted_kyc_user_list, name='get_submitted_kyc_user_list'),
    url(r'^get_pending_kyc_user_list/$',views.get_pending_kyc_user_list, name='get_pending_kyc_user_list'),
    url(r'^get_accepted_kyc_user_list/$',views.get_accepted_kyc_user_list, name='get_accepted_kyc_user_list'),
]