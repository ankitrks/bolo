# from django.urls import path
from django.conf.urls import include, url
from .views import TopicList,SearchTopic,SearchUser, TopicDetails, TopicCommentList, CategoryList, CommentList, CommentDetails, SingUpOTPView,\
	verify_otp, password_set, create_user_facebook,Usertimeline
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
topicsearch_urls = [
    url(r'^$', SearchTopic.as_view(), name='search-topic'),
]
usersearch_urls = [
    url(r'^$', SearchUser.as_view(), name='search-user'),
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
    url(r'^search/', include(topicsearch_urls)),
    url(r'^search/users/', include(usersearch_urls)),
    url(r'^categories/', include(category_urls)),
    url(r'^comments/', include(comment_urls)),
    
    url(r'^token/$', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token/refresh/$', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),

    url(r'^otp/send/$', SingUpOTPView.as_view(), name='token_obtain_pair'),

    # Get Params could be ?is_reset_password=1 OR ?is_for_change_phone=1
    url(r'^otp/verify/$', verify_otp, name='token_obtain_pair'),

    url(r'^create/user/facebook/$', create_user_facebook, name='create_user_facebook'),
    url(r'^password/set/$', password_set, name='password_set'),
]
