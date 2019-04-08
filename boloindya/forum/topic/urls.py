# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

import forum.topic.moderate.urls
import forum.topic.unread.urls
import forum.topic.notification.urls
import forum.topic.favorite.urls
import forum.topic.private.urls
from . import views


urlpatterns = [

    url(r'^/$', views.index, name='index'),
    url(r'^publish/$', views.publish, name='publish'),
    url(r'^discussion/$', views.ques_ans_index, name='discussion'),

    url(r'^publish/(?P<category_id>\d+)/$', views.publish, name='publish'),

    url(r'^update/(?P<pk>\d+)/$', views.update, name='update'),

    url(r'^(?P<pk>\d+)/$', views.detail, kwargs={'slug': "", }, name='detail'),
    url(r'^(?P<pk>\d+)/(?P<slug>[\w-]+)/$', views.detail, name='detail'),

    url(r'^active/$', views.index_active, name='index-active'),

    url(r'^moderate/', include(forum.topic.moderate.urls, namespace='moderate')),
    url(r'^unread/', include(forum.topic.unread.urls, namespace='unread')),
    url(r'^notification/', include(forum.topic.notification.urls, namespace='notification')),
    url(r'^favorite/', include(forum.topic.favorite.urls, namespace='favorite')),
    url(r'^private/', include(forum.topic.private.urls, namespace='private')),
]
