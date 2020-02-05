# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ..comment.bookmark.models import CommentBookmark
from .notification.models import TopicNotification
from .unread.models import TopicUnread
from redis_utils import *
from .models import VBseen


def topic_viewed(request, topic):
    # Todo test detail views
    user = request.user
    comment_number = CommentBookmark.page_to_comment_number(request.GET.get('page', 1))

    CommentBookmark.update_or_create(
        user=user,
        topic=topic,
        comment_number=comment_number
    )
    TopicNotification.mark_as_read(user=user, topic=topic)
    TopicUnread.create_or_mark_as_read(user=user, topic=topic)
    topic.increase_view_count()

def get_redis_vb_seen(user_id):
    key = 'vb_seen:'+str(user_id)
    vb_seen_list = get_redis(key)
    if not vb_seen_list:
        vb_seen_list = list(VBseen.objects.filter(user_id=user_id).distinct('topic_id').values_list('topic_id',flat=True))
        set_redis(key,vb_seen_list)
    return vb_seen_list

def update_redis_vb_seen(user_id,topic_id):
    key = 'vb_seen:'+str(user_id)
    vb_seen_list = get_redis(key)
    if not vb_seen_list:
        vb_seen_list = list(VBseen.objects.filter(user_id=user_id).distinct('topic_id').values_list('topic_id',flat=True))
    if topic_id not in vb_seen_list:
        vb_seen_list.append(topic_id)
    set_redis(key,vb_seen_list)


