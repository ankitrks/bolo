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
    url(r'^get_user_pay_details/$',views.get_user_pay_details, name='get_user_pay_details'),
    url(r'^get_single_encash_detail/$',views.get_single_encash_detail, name='get_single_encash_detail'),
    url(r'^calculate_encashable_detail/$',views.calculate_encashable_detail, name='calculate_encashable_detail'),
    url(r'^bolo_payment/$',views.PaymentView.as_view(),name='bolo_payment'),
    url(r'^bolo_cycle/$',views.PaymentCycleView.as_view(),name='bolo_cycle'),
    url(r'^accept_kyc/$',views.accept_kyc, name='accept_kyc'),
    url(r'^reject_kyc/$',views.reject_kyc, name='reject_kyc'),
    url(r'^uploadvideofile/$',views.uploadvideofile,name = 'uploadvideofile'),
    url(r'^boloindya_uploadvideofile/$',views.boloindya_uploadvideofile,name = 'boloindya_uploadvideofile'),
    url(r'^management/video/$',views.video_management,name = 'video_management'),
    url(r'^upload_n_transcode/$',views.upload_n_transcode),
    url(r'^boloindya_upload_n_transcode/$',views.boloindya_upload_n_transcode),
    url(r'^get_filtered_user/$',views.get_filtered_user,name = 'get_filtered_user'),
    url(r'^upload_details/$',views.upload_details),
    url(r'^uploaded_list/$',views.uploaded_list),
    url(r'^user_statistics/$', views.user_statistics),
    url(r'^video_statistics/$', views.video_statistics),
    url(r'^get_user_stats/$', views.get_stats_data),
    url(r'^get_hau_data/$', views.get_hau_data),
    url(r'^get_dau_data/$', views.get_dau_data),
    url(r'^get_installs_data/$', views.get_installs_data),
    url(r'^get_impr_data/$', views.get_daily_impressions_data),
    url(r'^get_top_impr/$', views.get_top_impressions_data),
    url(r'^get_weekly_vplay_data/$', views.weekly_vplay_data),
    url(r'^get_daily_vplay_data/$', views.daily_vplay_data),
    #url(r'^barchart/$', views.barchart, name= 'create_barchart'),              # url for rendering the bar chart
    url(r'^edit_upload/$',views.edit_upload),
    url(r'^delete_upload/$',views.delete_upload),
    url(r'^boloindya_upload_details/$',views.boloindya_upload_details),
    url(r'^boloindya_uploaded_list/$',views.boloindya_uploaded_list),
    url(r'^edit_upload/$',views.edit_upload),
    url(r'^boloindya_edit_upload/$',views.boloindya_edit_upload),
    url(r'^get_submitted_kyc_user_list/$',views.get_submitted_kyc_user_list, name='get_submitted_kyc_user_list'),
    url(r'^get_single_user_pay_details/$',views.get_single_user_pay_details, name='get_single_user_pay_details'),
    url(r'^get_pending_kyc_user_list/$',views.get_pending_kyc_user_list, name='get_pending_kyc_user_list'),
    url(r'^get_accepted_kyc_user_list/$',views.get_accepted_kyc_user_list, name='get_accepted_kyc_user_list'),
    url(r'^notification_panel/$',views.notification_panel, name='notification_panel'),
    url(r'^particular_notification/(?P<notification_id>\d+)/(?P<status_id>\d+)/(?P<page_no>\d+)/(?P<is_uninstalled>\d+)$',views.particular_notification, name='particular_notification'),
    url(r'^add_user_pay/$',views.add_user_pay, name='add_user_pay'),
    url(r'^send_notification/$',views.send_notification, name='send_notification'),
    url(r'^create_user_notification_delivered/$',views.create_user_notification_delivered, name='create_user_notification_delivered'),
    url(r'^open_notification_delivered/$',views.open_notification_delivered, name='open_notification_delivered'),   
    url(r'^remove_notification/$',views.remove_notification, name='remove_notification'),   

    # api for notification search
    url(r'^search_notification/$',views.search_notification, name='search_notification'),
    url(r'^search_notification_users/$',views.search_notification_users, name='search_notification_users'),

    # url for rendering analytics panel
    url(r'^analytics/$', views.analytics),  

    url(r'^upload_image_notification/$',views.upload_image_notification, name='search_notification'),  

    url(r'^update_user_time/$',views.update_user_time, name='update_user_time'),
]