# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static

import forum.topic.views
import forum.admin.urls
import forum.user.urls
import forum.search.urls
import forum.category.urls
import forum.topic.urls
import forum.comment.urls
import drf_spirit.urls
import jarvis.urls

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view
from rest_framework.documentation import include_docs_urls

import drf_spirit.views

schema_view = get_swagger_view(title='BoloIndya API')

patterns = [
    url(r'^$', forum.topic.views.new_home, name='index'),
    url(r'^match/(?P<match_id>\d+)/(?P<slug>[\w-]+)/$', forum.topic.views.share_match_page, name='share_match_page'),
    url(r'^predict/(?P<poll_id>\d+)/(?P<slug>[\w-]+)/$', forum.topic.views.share_poll_page, name='share_poll_page'),
    url(r'^user/(?P<user_id>\d+)/(?P<username>[\w-]+)/$', forum.topic.views.share_user_page, name='share_user_page'),
    url(r'^video_bytes/(?P<user_id>\d+)/(?P<poll_id>\d+)/(?P<slug>[\w-]+)/$', forum.topic.views.share_vb_page, name='share_vb_page'),

    url(r'^about/$', forum.topic.views.get_about, name='get_about'),
    url(r'^terms-of-service/$', forum.topic.views.get_termofservice, name='get_termofservice'),
    url(r'^privacy-policy/$', forum.topic.views.get_privacypolicy, name='get_privacypolicy'),
    url(r'^challenge/GameOfTongues$', forum.topic.views.share_challenge_page, name='share_challenge_page'),
    url(r'^robots.txt$', forum.topic.views.robotstext, name='roboxt'),
    url(r'^sitemap.xml$', forum.topic.views.sitemapxml, name='sitemap'),

    url(r'^ajax/login/$', forum.user.auth.views.login_new_bolo_user, name='index_login_new_bolo_user'),
    url(r'^ajax/verify_user/$', forum.user.auth.views.verify_user, name='index_login_new_bolo_user'),
    url(r'^videos/$', forum.topic.views.index_videos, name='videos'),

    url(r'^referral-code/validate/$', forum.user.views.referral_code_validate, name='referral_code_validate'),
    url(r'^referral-code/update/$', forum.user.views.referral_code_update, name='referral_code_update'),

    url(r'^ajax/pageno/$', forum.topic.views.get_topics_feed, name='ajax_lazy_topic_fetch'),
    url(r'^st/admin/', include(forum.admin.urls, namespace='admin')),
    url(r'^user/', include(forum.user.urls, namespace='user')),
    url(r'^search/', include(forum.search.urls, namespace='search')),
    url(r'^category/', include(forum.category.urls, namespace='category')),
    url(r'^topic/', include(forum.topic.urls, namespace='topic')),
    url(r'^comment/', include(forum.comment.urls, namespace='comment')),
    url(r'^api/v1/docs/$', schema_view),
    url(r'^api/v1/', include(drf_spirit.urls, namespace='api')),
    url(r'fcm/', include('fcm.urls')),
    url(r'^jarvis/',include('jarvis.urls', namespace='jarvis')),
    url(r'^get-html-content-app/',forum.user.views.getpagecontent,name='get_html_content_app'),
    url(r'^download/$',drf_spirit.views.redirect_to_store,name='download'),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns = [
	url(r'^superman/', include(admin.site.urls)),
    url(r'^', include(patterns, namespace='spirit', app_name='forum')),
    url(r'docs/', include_docs_urls(title='Boloindya API')),
]
