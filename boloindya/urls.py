# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
import forum.topic.views
import forum.admin.urls
import forum.admin.api_urls
import forum.user.urls
import forum.search.urls
import forum.category.urls
import forum.topic.urls
import forum.comment.urls
import forum.booking.urls
import drf_spirit.urls
import drf_spirit.api_urls_v2
import jarvis.urls
import allauth
import coupon.urls
import booking.urls
import payment.urls
import booking.api_urls
import advertisement.api_urls
import advertisement.urls
import report.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view
from rest_framework.documentation import include_docs_urls

import drf_spirit.views

schema_view = get_swagger_view(title='BoloIndya API')

patterns = [
    url(r'^timeout/test/$', jarvis.views.timeout_test),
    url(r'^analytics_jarvis/$', jarvis.views.statistics_all_jarvis),
    url(r'^match/(?P<match_id>\d+)/(?P<slug>[\w-]+)/$', forum.topic.views.share_match_page, name='share_match_page'),
    url(r'^predict/(?P<poll_id>\d+)/(?P<slug>[\w-]+)/$', forum.topic.views.share_poll_page, name='share_poll_page'),
    url(r'^user/(?P<user_id>\d+)/(?P<username>[\w-]+)/$', forum.topic.views.share_user_page, name='share_user_page'),
    url(r'^video_bytes/(?P<user_id>\d+)/(?P<poll_id>\d+)/(?P<slug>[\w-]+)/$', forum.topic.views.share_vb_page, name='share_vb_page'),

    url(r'^about/$', forum.topic.views.get_about, name='get_about'),
    url(r'^login/$', forum.topic.views.login_user, name='login'),
    url(r'^profile/(?P<username>[\w-]+)/$', forum.topic.views.user_profile, name='user_profile'),
    url(r'^terms-of-service/$', forum.topic.views.get_termofservice, name='get_termofservice'),
    url(r'^privacy-policy/$', forum.topic.views.get_privacypolicy, name='get_privacypolicy'),
    url(r'^bolo-action/$', forum.topic.views.get_bolo_action, name='get_bolo_action'),
    url(r'^challenge/(?P<hashtag>[\w-]+)$', forum.topic.views.share_challenge_page, name='share_challenge_page'),
    url(r'^trending/(?P<hashtag>[\w-]+)$', forum.topic.views.share_challenge_page, name='share_challenge_page'),
    url(r'^robots.txt$', forum.topic.views.robotstext, name='roboxt'),
    url(r'^sitemap.xml$', forum.topic.views.sitemapxml, name='sitemap'),

    url(r'^ajax/login/$', forum.user.auth.views.login_new_bolo_user, name='index_login_new_bolo_user'),
    url(r'^ajax/verify_user/$', forum.user.auth.views.verify_user, name='index_login_new_bolo_user'),
    url(r'^videos/$', forum.topic.views.index_videos, name='videos'),

    url(r'^referral-code/validate/$', forum.user.views.referral_code_validate, name='referral_code_validate'),
    url(r'^referral-code/update/$', forum.user.views.referral_code_update, name='referral_code_update'),
    url(r'^analytics/$', jarvis.views.statistics_all),
    

    url(r'^ajax/pageno/$', forum.topic.views.get_topics_feed, name='ajax_lazy_topic_fetch'),
    url(r'^st/admin/', include(forum.admin.urls, namespace='admin')),
    url(r'^user/', include(forum.user.urls, namespace='user')),
    # url(r'^search/', include(forum.search.urls, namespace='search')),
    url(r'^search/', include('haystack.urls')),
    url(r'^category/', include(forum.category.urls, namespace='category')),
    url(r'^topic/', include(forum.topic.urls, namespace='topic')),
    url(r'^comment/', include(forum.comment.urls, namespace='comment')),
    url(r'^api/v1/', include(drf_spirit.urls, namespace='api')),
    url(r'^api/v1/', include(coupon.urls, namespace='api')),
    url(r'^api/v1/', include(booking.api_urls, namespace='api')),
    url(r'^api/v2/fetch_audio_list', drf_spirit.views.audio_list),
    url(r'fcm/', include('fcm.urls')),
    url(r'^jarvis/',include('jarvis.urls', namespace='jarvis')),
    url(r'^get-html-content-app/',forum.user.views.getpagecontent,name='get_html_content_app'),
    url(r'^download/$',drf_spirit.views.redirect_to_store,name='download'),
    url(r'^invite/(?P<slug>[\w-]+)/(?P<user_id>\d+)/$', forum.user.views.referral_link, name='invite'),
    url(r'^careers/$',forum.topic.views.boloindya_careers,name='boloindya_careers'),
    url(r'^careers/openings/$',forum.topic.views.boloindya_openings,name='boloindya_openings'),
    url(r'^careers/openings/(?P<slug>[\w-]+)/$',forum.topic.views.boloindya_opening_details,name='boloindya_opening_details'),
    url(r'^careers/application/$',forum.topic.views.job_request,name='job_request'),
    url(r'^team/$',forum.topic.views.boloindya_team_details,name='boloindya_team_details'),
    url(r'^login/auth_api/$',forum.topic.views.login_using_api,name='login_using_api'),
    url(r'^help_support/$',forum.topic.views.help_support,name='help_support'),
    url(r'^api/v1/delete_video', forum.topic.views.delete_video, name='delete_video'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    patterns.append(url(r'^api/v1/docs/$', schema_view))


urlpatterns = [
    # url(r'^jet/', include('jet.urls', 'jet')),  # Django JET URLS
    url('grappelli/', include('grappelli.urls')), # grappelli URLS
	url(r'^superman/', include(admin.site.urls)),
    url(r'^api/superman/', include(forum.admin.api_urls)),
    url(r'^_nested_admin/', include('nested_admin.urls')),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^', include(patterns, namespace='spirit', app_name='forum')),
    url(r'docs/', include_docs_urls(title='Boloindya API')),
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^payment/', include(payment.urls, namespace='payment')),
    url(r'^api/v1/payment/', include('payment.api_urls', namespace='payment')),
    url(r'^booking/', include(booking.urls)),
    url(r'^api/v1/ad/', include('advertisement.api_urls', namespace='ad')),
    url(r'^api/v2/', include('drf_spirit.api_urls_v2')),
    url(r'^ad/', include(advertisement.urls)),
    url(r'^report/', include(report.urls)),
]

urlpatterns += i18n_patterns(
    url(r'^$', forum.topic.views.new_home_updated, name='index'),
    url(r'^home/$', forum.topic.views.old_home, name='old_home'),
    url(r'^new_home/$', forum.topic.views.new_home_updated, name='new_home_updated'),
    url(r'^trending/$', forum.topic.views.boloindya_feed, name='boloindya_feed'),
    url(r'^feed/$', forum.topic.views.new_home, name='new_home'),
    url(r'^trending_videojs/$', forum.topic.views.trending_videojs, name='trending_videojs'),
    url(r'^trending_polyplayer/$', forum.topic.views.trending_polyplayer, name='trending_polyplayer'),
    url(r'^upload/$', forum.topic.views.upload_video_boloindya, name='upload_video'),
    url(r'^video_details/(?P<id>\d+)/$', forum.topic.views.video_details, name='video_details'),
    url(r'^video/(?P<slug>[\w-]+)/(?P<id>\d+)/$', forum.topic.views.video_details_by_slug, name='video_details_by_slug'),
    url(r'^explore/(?P<slug>[\w-]+)/(?P<id>\d+)/$', forum.topic.views.explore_video_details_by_slug, name='video_details_by_slug'),
    url(r'^tag/(?P<category_slug>[\w-]+)/$', forum.topic.views.get_feed_list_by_category, name='get_feed_list_by_category'),
    #url(r'^tag/(?P<category_slug>[\w-]+)/$', forum.topic.views.get_topic_details_by_category, name='topic_details'),
    url(r'^hashtag/(?P<hashtag>[\w-]+)/$', forum.topic.views.get_topic_list_by_hashtag, name='get_topic_list_by_hashtag'),
    url(r'^search/', forum.topic.views.search_by_term, name='search_by_term'),
    url(r'^discover/$', forum.topic.views.video_discover, name='video_discover'),
    url(r'^timeline/$', forum.topic.views.user_timeline, name='user_timeline'),
    url(r'^get_challenge_details/$', forum.topic.views.get_challenge_details, name='get_challenge_details'),
    url(r'^(?P<username>[\w-]+)/$', forum.topic.views.bolo_user_details, name='bolo_user_details'),
    url(r'^(?P<username>[\w-]+)/(?P<id>\d+)/$', forum.topic.views.video_details, name='video_details'),
    url(r'^(?P<username>[\w-]+)/(?P<id>\d+)/(?P<userid>\d+)/$', forum.topic.views.video_details, name='video_details'),
    url(r'^test/testurllang/$', forum.topic.views.testurllang, name='testurllang'),
    #prefix_default_language=True
    
)

