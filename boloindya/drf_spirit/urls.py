# from django.urls import path
from django.conf.urls import include, url
from .views import TopicList, TopicDetails, TopicCommentList, CategoryList, CommentList, CommentDetails
from rest_framework_simplejwt import views as jwt_views

app_name = 'drf_spirit'

topic_urls = [
    url(r'^$', TopicList.as_view(), name='topic-list'),
    url(r'^(?P<slug>[\w-]+)/$', TopicDetails.as_view(), name='topic-detail'),
    url(r'^(?P<slug>[\w-]+)/comments/$', TopicCommentList.as_view(), name='topic-comment-list')
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
    url(r'^categories/', include(category_urls)),
    url(r'^comments/', include(comment_urls)),
    url(r'^token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]
