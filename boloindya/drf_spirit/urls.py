# from django.urls import path
from django.conf.urls import include, url
from .views import TopicList, TopicDetails,SearchTopic,SearchUser,replyOnTopic,createTopic, TopicCommentList, CategoryList, CommentList, CommentDetails, SingUpOTPView,\
	verify_otp, password_set, fb_profile_settings,Usertimeline,follow_user,follow_sub_category,like,shareontimeline,GetProfile,SubCategoryList,upload_video_to_s3,comment_view,\
    follow_like_list,upload_audio_to_s3,reply_delete,editTopic,topic_delete,notification_topic,GetUserProfile,RegisterDevice,UnregisterDevice,NotificationAPI,get_bolo_score,\
    GetTopic,GetQuestion,GetAnswers,CricketMatchList,get_single_match,get_single_poll,predict,LeaderBoradList,vb_seen,VBList,ExpertList,GetHomeAnswer,transcoder_notification,\
    vb_transcode_status,get_follow_user,upload_profile_image,get_following_list,get_follower_list,GetChallenge,GetChallengeDetails,save_android_logs,SyncDump,get_hash_list,\
    KYCDocumentTypeList,save_kyc_basic_info,save_kyc_documents,save_kyc_selfie,save_kyc_additional_info,save_bank_details_info,kyc_profession_status,get_kyc_status,my_app_version,\
    EncashableDetailList,get_bolo_details, get_category_detail, UserLogStatistics,GetFollowigList,GetFollowerList, get_category_with_video_bytes, get_category_detail_with_views, \
    get_category_video_bytes, get_popular_video_bytes
from rest_framework_simplejwt import views as jwt_views

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
    url(r'^search/users/', include(usersearch_urls)),
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

    # Get Params could be ?is_reset_password=1 OR ?is_for_change_phone=1
    url(r'^otp/verify/$', verify_otp, name='token_obtain_pair'),

    url(r'^save_kyc_basic_info/$', save_kyc_basic_info, name='save_kyc_basic_info'),
    url(r'^save_kyc_documents/$', save_kyc_documents, name='save_kyc_documents'),
    url(r'^save_kyc_selfie/$', save_kyc_selfie, name='save_kyc_selfie'),
    url(r'^save_kyc_additional_info/$', save_kyc_additional_info, name='save_kyc_additional_info'),
    url(r'^save_bank_details_info/$', save_bank_details_info, name='save_bank_details_info'),
    url(r'^get_kyc_status/$', get_kyc_status, name='get_kyc_status'),
    url(r'^get_bolo_details/$', get_bolo_details, name='get_bolo_details'),
    url(r'^get_encash_details/$', EncashableDetailList.as_view(), name='get_encash_details'),


    url(r'^fb_profile_settings/$', fb_profile_settings, name='fb_profile_settings'),
    url(r'^follow_user/$', follow_user, name='follow_user'),
    url(r'^follow_sub_category/$', follow_sub_category, name='follow_sub_category'),
    url(r'^get_follow_user/$', get_follow_user, name='get_follow_user'),
    url(r'^get_following_list/$', GetFollowigList.as_view(), name='get_following_list'),
    url(r'^get_follower_list/$', GetFollowerList.as_view(), name='get_follower_list'),
    url(r'^shareontimeline/$', shareontimeline, name='shareontimeline'),
    url(r'^like/$', like, name='like'),
    url(r'^get_challenge/$', GetChallenge.as_view(), name='get_challenge'),
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
    url(r'^topic_delete/$', topic_delete, name='topic_delete'),
    url(r'^notification/(?P<action>click|get)$', NotificationAPI.as_view(), name='notification'),
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
    url(r'^predict/$', predict, name='predict'),
    url(r'^vb_seen/$', vb_seen, name='vb_seen'),
    url(r'^transcoder_notification/$', transcoder_notification, name='transcoder_notification'),
    url(r'^vb_transcode_status/$', vb_transcode_status, name='vb_transcode_status'),
    url(r'^get_vb_list/$', VBList.as_view(), name='get_vb_list'),
    url(r'^leaderboard_view/$', LeaderBoradList.as_view(), name='leaderboard_view'),
    url(r'^topics/', include(topic_urls)),
    url(r'^get_hash_list/$',get_hash_list,name='get_hash_list'),
    url(r'^sync/dump/',SyncDump,name='sync_dump'),
    #url(r'^user/statistics/$', user_statistics, name = 'user_statistics'),          # url for dumping values in user statistics table

    url(r'^get_category_detail/$', get_category_detail),
    url(r'^get_category_detail_with_views/$', get_category_detail_with_views),
    url(r'^get_category_video_bytes/$', get_category_video_bytes),
    url(r'^get_popular_video_bytes/$', get_popular_video_bytes),
    
    url(r'^get_category_with_video_bytes/$', get_category_with_video_bytes),
]
