# from django.urls import pat
from django.conf.urls import include, url
from rest_framework_simplejwt import views as jwt_views
from .views import *

app_name = 'drf_spirit'

topic_urls = [
    url(r'^$', TopicList.as_view(), name='topic-list'),
    url(r'^(?P<slug>[\w-]+)/$', TopicDetails.as_view(), name='topic-detail'),
    url(r'^(?P<slug>[\w-]+)/(?P<topic_id>\d+)/comments/$', TopicCommentList.as_view(), name='topic-comment-list')
]
timeline_urls = [
    url(r'^$', Usertimeline.as_view(), name='usertimeline-list'),
]
topicsearch_urls = [
    url(r'^$', SearchTopic.as_view(), name='search-topic'),
]
usersearch_urls = [
    url(r'^$', SearchUser.as_view(), name='search-user'),
]
replyontopic_urls = [
    url(r'^$', replyOnTopic, name='reply-topic'),
]

createtopic_urls = [
    url(r'^$', createTopic, name='create-topic'),
]

comment_urls = [
    url(r'^$', CommentList.as_view(), name='comments'),
    url(r'^(?P<id>\d+)/$', CommentDetails.as_view(), name='comment-details'),
]

category_urls = [
    url(r'^$', CategoryList.as_view(), name='category-list'),
]

urlpatterns = [
    url(r'^timeline/', include(timeline_urls)),
    url(r'^get_topic/$', GetTopic.as_view(), name='get_topic'),
    url(r'^get_question/$', GetQuestion.as_view(), name='get_question'),
    url(r'^get_home_answer/$', GetHomeAnswer.as_view(), name='get_home_answer'),
    url(r'^get_answers/$', GetAnswers.as_view(), name='get_answers'),
    url(r'^search/', include(topicsearch_urls)),
    url(r'^solr/search/$', SolrSearchTopic.as_view(), name='solr-search-topic'),
    url(r'^search/users/', include(usersearch_urls)),
    url(r'^solr/search/users/$', SolrSearchUser.as_view(), name='solr-search-user'),
    url(r'^search/hash_tag/',SearchHashTag.as_view(),name='search_hash_tag'),
    url(r'^solr/search/hash_tag/$',SolrSearchHashTag.as_view(),name='solr-search_hash_tag'),
    url(r'^solr/search/top/$',SolrSearchTop.as_view(),name='solr-search-top'),
    url(r'^create_topic', include(createtopic_urls)),
    url(r'^reply_on_topic', include(replyontopic_urls)),
    url(r'^categories/', include(category_urls)),
    url(r'^kyc_document_types/', KYCDocumentTypeList.as_view(), name='kyc_document_types'),
    url(r'^kyc_profession_status/', kyc_profession_status, name='kyc_profession_status'),
    url(r'^comments/', include(comment_urls)),
    url(r'^upload_profile_image$', upload_profile_image, name='upload_profile_image'),
    url(r'^my_app_version/$', my_app_version, name='my_app_version'),
    
    url(r'^token/$', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token/refresh/$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    url(r'^otp/send/$', SingUpOTPView.as_view(), name='token_obtain_pair'),
    url(r'^otp/send_with_country_code/$', SingUpOTPCountryCodeView.as_view(), name='token_obtain_pair'),
    # Get Params could be ?is_reset_password=1 OR ?is_for_change_phone=1
    url(r'^otp/verify/$', verify_otp, name='token_obtain_pair'),
    url(r'^otp/verify_with_country_code/$', verify_otp_with_country_code, name='otp_verify_with_cc'),
    url(r'^user/user_data/$', generate_login_data, name='generate_login_data'),

    url(r'^save_kyc_basic_info/$', save_kyc_basic_info, name='save_kyc_basic_info'),
    url(r'^save_kyc_documents/$', save_kyc_documents, name='save_kyc_documents'),
    url(r'^save_kyc_selfie/$', save_kyc_selfie, name='save_kyc_selfie'),
    url(r'^save_kyc_additional_info/$', save_kyc_additional_info, name='save_kyc_additional_info'),
    url(r'^save_bank_details_info/$', save_bank_details_info, name='save_bank_details_info'),
    url(r'^get_kyc_status/$', get_kyc_status, name='get_kyc_status'),
    url(r'^get_bolo_details/$', get_bolo_details, name='get_bolo_details'),
    url(r'^get_encash_details/$', EncashableDetailList.as_view(), name='get_encash_details'),


    url(r'^fb_profile_settings/$', fb_profile_settings, name='fb_profile_settings'),
    url(r'^get_search_suggestion/$', get_search_suggestion, name='get_search_suggestion'),
    url(r'^follow_user/$', follow_user, name='follow_user'),
    url(r'^follow_sub_category/$', follow_sub_category, name='follow_sub_category'),
    url(r'^get_follow_user/$', get_follow_user, name='get_follow_user'),
    url(r'^get_following_list/$', GetFollowigList.as_view(), name='get_following_list'),
    url(r'^get_follower_list/$', GetFollowerList.as_view(), name='get_follower_list'),
    url(r'^shareontimeline/$', shareontimeline, name='shareontimeline'),
    url(r'^get_auth_login_as_user_id/$', get_auth_login_as_user_id, name='get_auth_login_as_user_id'),
    url(r'^like/$', like, name='like'),
    url(r'^mention_suggestion/$', mention_suggestion, name='mention_suggestion'),
    url(r'^get_challenge/$', GetChallenge, name='get_challenge'),
    url(r'^get_popular_hash_tag/$', GetPopularHashTag.as_view(), name='get_popular_hash_tag'),
    url(r'^get_follow_post/$', GetFollowPost, name='get_follow_post'),
    url(r'^get_follow_post_load_test/$', get_follow_post_load_test, ),
    url(r'^get_user_pay_datatbale/$', UserPayDatatableList.as_view(), name='get_user_pay_datatbale'),
    url(r'^get_report_datatbale/$', ActiveReoprtsDatatableList.as_view(), name='get_report_datatbale'),
    url(r'^bot_user_list_datatable/$', BotUserDatatableList.as_view(), name='bot_user_list_datatable'),
    url(r'^bot_video_list_datatable/$', BotVideoListDatatableList.as_view(), name='bot_video_list_datatable'),
    url(r'^get_challenge_details/$', GetChallengeDetails, name='get_challenge_details'),
    url(r'^password/set/$', password_set, name='password_set'),
    url(r'^get_profile/$', GetProfile.as_view(), name='get_profile'),
    url(r'^get_sub_category/$', SubCategoryList.as_view(), name='get_sub_category'),
    url(r'^upload_video_to_s3/$', upload_video_to_s3, name='upload_video_to_s3'),
    url(r'^upload_audio_to_s3/$', upload_audio_to_s3, name='upload_audio_to_s3'),
    url(r'^comment_view/$', comment_view, name='comment_view'),
    url(r'^follow_like_list/$', follow_like_list, name='follow_like_list'),
    url(r'^reply_delete/$', reply_delete, name='reply_delete'),
    url(r'^editTopic/$', editTopic, name='editTopic'),
    url(r'^editComment/$', editComment, name='editComment'),
    url(r'^topic_delete/$', topic_delete, name='topic_delete'),
    url(r'^notification/(?P<action>click|get|mark_all_read)$', NotificationAPI.as_view(), name='notification'),
    url(r'^notification_topic/$', notification_topic, name='notification_topic'),
    url(r'^experts/$', ExpertList.as_view(), name='list_experts'),
    url(r'^get_userprofile/$', GetUserProfile, name='get_userprofile'),
    url(r'^register_device/$', RegisterDevice, name='register_device'),
    url(r'^save_android_logs/$', save_android_logs, name='save_android_logs'),
    url(r'^unregister_device/$', UnregisterDevice, name='unregister_device'),
    url(r'^get_bolo_score/$', get_bolo_score, name='get_bolo_score'),
    url(r'^get_match_list/$', CricketMatchList.as_view(), name='get_match_list'),
    url(r'^get_single_match/$', get_single_match, name='get_single_match'),
    url(r'^get_single_poll/$', get_single_poll, name='get_single_poll'),
    url(r'^get_ip_to_language/$', get_ip_to_language, name='get_ip_to_language'),
    url(r'^predict/$', predict, name='predict'),
    url(r'^vb_seen/$', vb_seen, name='vb_seen'),
    url(r'^transcoder_notification/$', transcoder_notification, name='transcoder_notification'),
    url(r'^vb_transcode_status/$', vb_transcode_status, name='vb_transcode_status'),
    url(r'^get_vb_list/$',VBList, name='get_vb_list'),
    url(r'^leaderboard_view/$', LeaderBoradList.as_view(), name='leaderboard_view'),
    url(r'^topics/', include(topic_urls)),
    url(r'^get_hash_list/$',get_hash_list,name='get_hash_list'),
    url(r'^get_user_bolo_info/$',get_user_bolo_info,name='get_user_bolo_info'),
    url(r'^sync/dump/',SyncDump,name='sync_dump'),
    url(r'^hashtag_suggestion/$', hashtag_suggestion, name='hashtag_suggestion'),
    url(r'^store_phone_book/$', store_phone_book, name='store_phone_book'),
    url(r'^update_mobile_no/$', update_mobile_no, name='update_mobile_no'),
    url(r'^update_mobile_no_with_cc/$', update_mobile_no_with_country_code, name='update_mobile_no_with_cc'),
    url(r'^get_refer_earn_data/$', get_refer_earn_data, name='get_refer_earn_data'),
    url(r'^get_refer_earn_url/$', get_refer_earn_url, name='get_refer_earn_url'),
    url(r'^verify_otp_and_update_profile/$', verify_otp_and_update_profile, name='verify_otp_and_update_profile'),
    url(r'^verify_otp_and_update_profile_with_cc/$', verify_otp_and_update_profile_with_country_code, name='verify_otp_and_update_profile_with_cc'),
    url(r'^verify_otp_and_update_paytm_number/$', verify_otp_and_update_paytm_number, name='verify_otp_and_update_paytm_number'),
    url(r'^userprofile_update_paytm_number/$', userprofile_update_paytm_number, name='userprofile_update_paytm_number'),
    url(r'^update_mobile_invited/$', update_mobile_invited, name='update_mobile_invited'),
    url(r'^get_refer_earn_stat/$', get_refer_earn_stat, name='get_refer_earn_stat'),
    url(r'^solr/hashtag_suggestion/$', solr_hashtag_suggestion, name='solr_hashtag_suggestion'),
    #url(r'^user/statistics/$', user_statistics, name = 'user_statistics'),          # url for dumping values in user statistics table

    url(r'^get_category_detail/$', get_category_detail),
    url(r'^set_user_email/$', set_user_email,name='set_user_email'),
    url(r'^get_category_detail_with_views/$', get_category_detail_with_views),
    url(r'^get_category_video_bytes/$',get_category_video_bytes),
    url(r'^get_popular_video_bytes_old/$', get_popular_video_bytes),
    url(r'^get_popular_video_bytes/$', PopularVideoBytes.as_view()),
    url(r'^get_popular_video_bytes_load_test/$', get_popular_video_bytes_load_test),
    url(r'^pubsub/popular/$', pubsub_popular),
    url(r'^get_user_follow_and_like_list/$', get_user_follow_and_like_list),
    url(r'^get_recent_videos/$',get_recent_videos ),

    url(r'^get_landing_page_video/$', get_landing_page_video),
    url(r'^get_popular_bolo/$', get_popular_bolo),
    
    url(r'^get_category_with_video_bytes/$', get_category_with_video_bytes),

    url(r'^submit_user_feedback/$', submit_user_feedback),
    url(r'^save_banner_response/$', save_banner_response),
    url(r'^cache_user_data/$', cache_user_data,name='cache_user_data'),
    url(r'^get_hash_discover/$', get_hash_discover),
    url(r'^get_hash_discover_topics/$', get_hash_discover_topics),
    url(r'^send_sms_link/$', send_sms_link),

    url(r'^get_m3u8_of_ids/$', get_m3u8_of_ids),
    url(r'^upload_video_to_s3_for_app/$', upload_video_to_s3_for_app),
    url(r'^report/$', report,name='report'),
    url(r'^get_campaigns/$', get_campaigns,name='get_campaigns'),
    url(r'^get_popup_campaign/$', get_popup_campaign,name='get_popup_campaign'),
    url(r'^get_user_details_from_topic_id/$', get_user_details_from_topic_id,name='get_user_details_from_topic_id'),
    url(r'^update_download_url_in_topic/',update_download_url_in_topic,name='update_download_url_in_topic'),
    url(r'^update_profanity_details/',update_profanity_details,name='update_profanity_details'),
    url(r'^get_user_last_vid_lang/$', get_user_last_vid_lang,name='get_user_last_vid_lang'),
    url(r'^fetch_audio_list/$', AudioFileListView.as_view(), name='fetch_audio_list'),
    url(r'^upload_cover_pic/$', upload_cover_pic),
    url(r'^upload_pii/$', upload_pii),
    url(r'^create_bot_topic/$',create_bot_topic, name='create_bot_topic'),
    url(r'^edit_bot_video/$',edit_bot_video, name='edit_bot_video'),
    url(r'^test_api_response_time/$', test_api_response_time),
    url(r'^get_user_notification_count/', GetUserNotificationCount.as_view()),
    url(r'^upload_thumbnail/', UploadVideoThumbnail.as_view()),
    url(r'^send_push_notification/', send_push_notification),
    url(r'^music/(?P<music_id>\d+)/videos/$', MusicVideoAPIView.as_view()),
]
