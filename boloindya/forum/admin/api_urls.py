# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import include, url

from . import views


urlpatterns = [
    url(r'^user/(?P<user_id>\w+)/(?P<action>\w+)/$', views.block_user),
]
