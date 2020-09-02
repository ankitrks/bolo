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
    url(r'^get_active_reports/$',views.get_active_reports, name='get_active_reports'),
    url(r'^get_moderated_reports/$',views.get_moderated_reports, name='get_moderated_reports'),
    url(r'^remove_post_or_block_user_temporarily/$',views.remove_post_or_block_user_temporarily, name='remove_post_or_block_user_temporarily'),
    url(r'^seems_fine/$',views.seems_fine, name='seems_fine'),
    url(r'^unremove_video_or_unblock/$',views.unremove_video_or_unblock, name='unremove_video_or_unblock'),
    url(r'^get_single_encash_detail/$',views.get_single_encash_detail, name='get_single_encash_detail'),
    url(r'^calculate_encashable_detail/$',views.calculate_encashable_detail, name='calculate_encashable_detail'),
    url(r'^bolo_payment/$',views.PaymentView.as_view(),name='bolo_payment'),
    url(r'^bolo_cycle/$',views.PaymentCycleView.as_view(),name='bolo_cycle'),
    url(r'^accept_kyc/$',views.accept_kyc, name='accept_kyc'),
    url(r'^reject_kyc/$',views.reject_kyc, name='reject_kyc'),
    url(r'^uploadvideofile/$',views.uploadvideofile,name = 'uploadvideofile'),
    url(r'^boloindya_uploadvideofile/$',views.boloindya_uploadvideofile,name = 'boloindya_uploadvideofile'),
    url(r'^management/video/$',views.video_management,name = 'video_management'),
    url(r'^management/user/$',views.user_management,name = 'user_management'),
    url(r'^referral/$',views.referral,name = 'referral'),
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
    url(r'^approve_all_completd_kyc/$',views.approve_all_completd_kyc, name='approve_all_completd_kyc'),
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
    url(r'^analytics_jarvis/get_csvdata/$', views.get_csv_data),
    url(r'^analytics_jarvis/get_playdata/$', views.get_playdata), 
    url(r'^analytics_jarvis/get_totalplaytime/$', views.get_total_playtime),  

    url(r'^upload_image_notification/$',views.upload_image_notification, name='search_notification'),  
    url(r'^get_count_notification/$',views.get_count_notification, name='get_count_notification'),  

    url(r'^update_user_time/$',views.update_user_time, name='update_user_time'),
    url(r'^upload_audio_file/$',views.boloindya_upload_audio_file,name = 'upload_audio_file'),
    url(r'^upload_audio_file_to_s3/$',views.boloindya_upload_audio_file_to_s3,name = 'upload_audio_file_to_s3'),

    #urls for campaign panel
    url(r'^campaigns_panel/$',views.campaigns_panel,name = 'campaigns_panel'),
    url(r'^new_campaign_page/$',views.new_campaign_page,name = 'campaigns_panel'),
    url(r'^add_campaign/$',views.add_campaign,name = 'add_campaign'),
    url(r'^search_fields_for_campaign/$',views.search_fields_for_campaign, name='search_hashtags'),
    url(r'^particular_campaign/(?P<campaign_id>\d+)$',views.particular_campaign,name = 'particular_campaign'),
    url(r'^search_and_add_hashtag/$',views.search_and_add_hashtag, name='search_and_add_hashtag'),
    url(r'^bot_user_form/$',views.bot_user_form, name='bot_user_form'),
    url(r'^bot_user_list/$',views.get_bot_user_list, name='bot_user_list'),
    url(r'^get_bot_video_list/$',views.get_bot_video_list, name='get_bot_video_list'),
    url(r'^delete_bot_video/$',views.delete_bot_video, name='delete_bot_video'),
]
