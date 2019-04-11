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

# Uncomment the next two lines to enable the admin:
from django.contrib import admin

patterns = [
    url(r'^$', forum.topic.views.new_home, name='index'),
    url(r'^ajax/login/$', forum.user.auth.views.login_new_bolo_user, name='index_login_new_bolo_user'),
    url(r'^ajax/verify_user/$', forum.user.auth.views.verify_user, name='index_login_new_bolo_user'),
    url(r'^videos/$', forum.topic.views.index_videos, name='videos'),
    url(r'^ajax/pageno/$', forum.topic.views.get_topics_feed, name='ajax_lazy_topic_fetch'),
    url(r'^st/admin/', include(forum.admin.urls, namespace='admin')),
    url(r'^user/', include(forum.user.urls, namespace='user')),
    url(r'^search/', include(forum.search.urls, namespace='search')),
    url(r'^category/', include(forum.category.urls, namespace='category')),
    url(r'^topic/', include(forum.topic.urls, namespace='topic')),
    url(r'^comment/', include(forum.comment.urls, namespace='comment')),
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns = [
	url(r'^superman/', include(admin.site.urls)),
    url(r'^', include(patterns, namespace='spirit', app_name='forum')),
]
