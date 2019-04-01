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

patterns = [
    url(r'^$', forum.topic.views.index_active, name='index'),
    url(r'^st/admin/', include(forum.admin.urls, namespace='admin')),
    url(r'^user/', include(forum.user.urls, namespace='user')),
    url(r'^search/', include(forum.search.urls, namespace='search')),
    url(r'^category/', include(forum.category.urls, namespace='category')),
    url(r'^topic/', include(forum.topic.urls, namespace='topic')),
    url(r'^comment/', include(forum.comment.urls, namespace='comment')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


urlpatterns = [
    url(r'^', include(patterns, namespace='spirit', app_name='forum')),
]
