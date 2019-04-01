# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from django.conf.urls import url, include

from ..core.conf import settings
import forum.comment.bookmark.urls
import forum.comment.flag.urls
import forum.comment.history.urls
import forum.comment.like.urls
import forum.comment.poll.urls
from . import views


urlpatterns = [
    url(r'^(?P<topic_id>\d+)/publish/$', views.publish, name='publish'),
    url(r'^(?P<topic_id>\d+)/publish/(?P<pk>\d+)/quote/$', views.publish, name='publish'),

    url(r'^(?P<pk>\d+)/update/$', views.update, name='update'),
    url(r'^(?P<pk>\d+)/find/$', views.find, name='find'),
    url(r'^(?P<topic_id>\d+)/move/$', views.move, name='move'),

    url(r'^(?P<pk>\d+)/delete/$', views.delete, name='delete'),
    url(r'^(?P<pk>\d+)/undelete/$', views.delete, kwargs={'remove': False, }, name='undelete'),

    url(r'^bookmark/', include(forum.comment.bookmark.urls, namespace='bookmark')),
    url(r'^flag/', include(forum.comment.flag.urls, namespace='flag')),
    url(r'^history/', include(forum.comment.history.urls, namespace='history')),
    url(r'^like/', include(forum.comment.like.urls, namespace='like')),
    url(r'^poll/', include(forum.comment.poll.urls, namespace='poll')),
]

if settings.ST_UPLOAD_IMAGE_ENABLED:
    urlpatterns.append(
        url(r'^upload/$', views.image_upload_ajax, name='image-upload-ajax'))

if settings.ST_UPLOAD_FILE_ENABLED:
    urlpatterns.append(
        url(r'^upload/file/$', views.file_upload_ajax, name='file-upload-ajax'))
