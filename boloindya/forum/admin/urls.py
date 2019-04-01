# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url

from . import views
import forum.category.admin.urls
import forum.comment.flag.admin.urls
import forum.topic.admin.urls
import forum.user.admin.urls


urlpatterns = [
    url(r'^$', views.dashboard, name='index'),
    url(r'^dashboard/$', views.dashboard, name='dashboard'),
    url(r'^config/$', views.config_basic, name='config-basic'),

    url(r'^category/', include(forum.category.admin.urls, namespace='category')),
    url(r'^comment/flag/', include(forum.comment.flag.admin.urls, namespace='flag')),
    url(r'^topic/', include(forum.topic.admin.urls, namespace='topic')),
    url(r'^user/', include(forum.user.admin.urls, namespace='user')),
]
