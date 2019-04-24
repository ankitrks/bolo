# from django.urls import path
from django.conf.urls import include, url
from .views import TopicList, TopicDetails, TopicCommentList, CategoryList, CommentList, CommentDetails, SingUpOTPView,\
	verify_otp, password_set, fb_profile_settings,Usertimeline,follow_user,follow_sub_category,like,shareontimeline
from rest_framework_simplejwt import views as jwt_views

app_name = 'drf_spirit'

topic_urls = [
    url(r'^$', TopicList.as_view(), name='topic-list'),
    url(r'^(?P<slug>[\w-]+)/$', TopicDetails.as_view(), name='topic-detail'),
    url(r'^(?P<slug>[\w-]+)/comments/$', TopicCommentList.as_view(), name='topic-comment-list')
]
timeline_urls = [
    url(r'^$', Usertimeline.as_view(), name='usertimeline-list'),
]

comment_urls = [
    url(r'^$', CommentList.as_view(), name='comments'),
    url(r'^(?P<id>\d+)/$', CommentDetails.as_view(), name='comment-details'),
]

category_urls = [
    url(r'^$', CategoryList.as_view(), name='category-list'),
]

urlpatterns = [
    url(r'^topics/', include(topic_urls)),
    url(r'^timeline/', include(timeline_urls)),
    url(r'^categories/', include(category_urls)),
    url(r'^comments/', include(comment_urls)),
    
    url(r'^token/$', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token/refresh/$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    url(r'^otp/send/$', SingUpOTPView.as_view(), name='token_obtain_pair'),

    # Get Params could be ?is_reset_password=1 OR ?is_for_change_phone=1
    url(r'^otp/verify/$', verify_otp, name='token_obtain_pair'),

    url(r'^fb_profile_settings$', fb_profile_settings, name='fb_profile_settings'),
    url(r'^follow_user$', follow_user, name='follow_user'),
    url(r'^follow_sub_category$', follow_sub_category, name='follow_sub_category'),
    url(r'^shareontimeline$', shareontimeline, name='shareontimeline'),
    url(r'^like$', like, name='like'),
    url(r'^password/set/$', password_set, name='password_set'),
]
