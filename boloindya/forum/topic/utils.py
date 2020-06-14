# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from ..comment.bookmark.models import CommentBookmark
from .notification.models import TopicNotification
from .unread.models import TopicUnread
from redis_utils import *
from .models import VBseen, RankingWeight, Topic
from forum.category.models import Category
from django.core.paginator import Paginator
from forum.user.utils.follow_redis import get_redis_following
from forum.user.models import UserProfile
from django.db.models import F, Q
import pandas as pd
from django.conf import settings
from datetime import datetime

def topic_viewed(request, topic):
    # Todo test detail views
    user = request.user
    comment_number = CommentBookmark.page_to_comment_number(request.GET.get('page', 1))

    CommentBookmark.update_or_create(
        user = user,
        topic = topic,
        comment_number = comment_number
    )
    TopicNotification.mark_as_read(user = user, topic = topic)
    TopicUnread.create_or_mark_as_read(user = user, topic = topic)
    topic.increase_view_count()

def get_redis_vb_seen(user_id):
    key = 'vb_seen:'+str(user_id)
    vb_seen_list = get_redis(key)
    if not vb_seen_list:
        vb_seen_list = list(VBseen.objects.filter(user_id = user_id).distinct('topic_id').values_list('topic_id', flat = True))
        set_redis(key, vb_seen_list)
    return vb_seen_list

def update_redis_vb_seen(user_id, topic_id):
    key = 'vb_seen:'+str(user_id)
    vb_seen_list = get_redis(key)
    if not vb_seen_list:
        vb_seen_list = list(VBseen.objects.filter(user_id = user_id).distinct('topic_id').values_list('topic_id', flat = True))
    if int(topic_id) not in vb_seen_list:
        vb_seen_list.append(int(topic_id))
    set_redis(key, vb_seen_list)

def get_ranking_feature_weight(feature):
    ranking_feature, is_created = RankingWeight.objects.get_or_create(features = feature)
    return ranking_feature.weight

## for vb_score sorted video in single category and language ##

def get_redis_data(key, query, page_no):
    topic_ids = []
    topics = []
    if not page_no:
        page_no = 1
    paginated_data = get_redis(key)
    if not paginated_data:
        paginated_data = update_redis_paginated_data(key, query)
    if paginated_data and (str(page_no) in paginated_data.keys() or 'remaining' in paginated_data.keys()):
        if str(page_no) in paginated_data.keys():
            topic_ids = paginated_data[str(page_no)]['id_list']
            topics = Topic.objects.filter(pk__in = topic_ids, is_removed = False).order_by('-vb_score')
        elif 'remaining' in paginated_data.keys():
            last_page_no = int(paginated_data['remaining']['last_page'])
            try:
                last_page_data = paginated_data[str(last_page_no)]
            except:
                last_page_data = paginated_data[last_page_no]
            topics = query.exclude(id__in = last_page_data['id_list']).filter(vb_score__lte = last_page_data['scores'][-1])
            new_page = page_no - last_page_no #(191-190)
            paginator = Paginator(topics, settings.REST_FRAMEWORK['PAGE_SIZE'])
            if paginator.num_pages >= new_page:
                topics = paginator.page(new_page)
            else:
                topics = []
    else:
        topics =  query.order_by('-vb_score')
        paginator = Paginator(topics, settings.REST_FRAMEWORK['PAGE_SIZE'])
        if paginator.num_pages >= page_no:
            topics = paginator.page(page_no)
        else:
            topics = []
    return topics

def get_redis_category_paginated_data(language_id, category_id, page_no):
    key = 'cat:'+str(category_id)+':lang:'+str(language_id)
    query = Topic.objects.filter(is_vb = True, is_removed = False, m2mcategory__id = category_id, language_id = language_id).order_by('-vb_score')
    return get_redis_data(key, query, page_no)
    
## For vb_score sorted filter in single language ##

def get_redis_language_paginated_data(language_id, page_no):
    key = 'lang:'+str(language_id)
    query = Topic.objects.filter(is_removed = False, is_vb = True, language_id = language_id).order_by('-vb_score')
    return get_redis_data(key, query, page_no)

def get_redis_follow_paginated_data(user_id, page_no):

    key = 'follow_post:'+str(user_id)
    all_follower = get_redis_following(user_id)
    category_follow = UserProfile.objects.get(user_id = user_id).sub_category.all().values_list('pk', flat = True)
    query = Topic.objects.filter(Q(user_id__in = all_follower)|Q(m2mcategory__id__in = category_follow, \
        language_id = UserProfile.objects.get(user_id = user_id).language), is_vb = True, is_removed = False).order_by('-vb_score')
    return get_redis_data(key, query, page_no)

def get_popular_paginated_data(user_id, language_id, page_no):
    all_seen_vb = []
    key = 'lang:'+str(language_id)+':popular_post:'+str(user_id)
    if user_id:
        all_seen_vb = get_redis_vb_seen(user_id)
    query = Topic.objects.filter(is_vb = True, is_removed = False, language_id = language_id, is_popular = True)\
        .exclude(pk__in = all_seen_vb).order_by('-vb_score')
    return get_redis_data(key, query, page_no)

def update_redis_paginated_data(key, query, cache_max_pages = settings.CACHE_MAX_PAGES_REAL_TIME):
    items_per_page = settings.REST_FRAMEWORK['PAGE_SIZE']
    min_count_per_page = settings.MIN_COUNT_PER_PAGE
    # cache_max_pages = settings.CACHE_MAX_PAGES
    extra_pages_beyond_max_pages = settings.EXTRA_PAGES_BEYOND_MAX_PAGES
    # print language_id, category_id, "############"
    page = 1
    final_data = {}
    exclude_ids = []
    topics_df = pd.DataFrame.from_records(query.order_by('-vb_score').values('id', 'user_id', 'vb_score'))
    if topics_df.empty:
        final_data[page] = {'id_list' : [], 'scores' : []}
    else:
        while(page != None):
            updated_df = topics_df.query('id not in [' + ','.join(exclude_ids) + ']').drop_duplicates('user_id')\
                    .nlargest(items_per_page, 'vb_score', keep = 'last')
            id_list = updated_df['id'].tolist()
            if len(id_list) >= min_count_per_page and page <= cache_max_pages:
                exclude_ids.extend( map(str, id_list) )
                if id_list:
                    final_data[page] = { 'id_list' : id_list, 'scores' : updated_df['vb_score'].tolist() }
                    page += 1
                else:
                    page = None
            else:
                remaining_count = len(topics_df) - len(exclude_ids) - len(updated_df)
                if remaining_count <= items_per_page * extra_pages_beyond_max_pages:
                    remaining_page_no = (remaining_count / items_per_page) + 1
                    if (remaining_count % items_per_page) > 0:
                        remaining_page_no += 1
                    while( remaining_page_no > 0):
                        updated_df = topics_df.query('id not in [' + ','.join(exclude_ids) + ']')[:items_per_page]
                        id_list = updated_df['id'].tolist()
                        exclude_ids.extend( map(str, id_list) )
                        remaining_page_no -= 1
                        if id_list:
                            final_data[page] = { 'id_list' : id_list, 'scores' : updated_df['vb_score'].tolist() }
                            page += 1
                        else:
                            page = None
                else:
                    # if remaining items are too many (more than "extra_pages_beyond_max_pages" pages).
                    # these will be filtered realtime then.
                    final_data['remaining'] = {'remaining_count' : remaining_count, 'last_page' : page - 1}
                    page = None
                page = None
    set_redis(key, final_data)
    if key:
        return get_redis(key)
    return final_data
## For vb_score sorted filter in single hashtag ##

def get_redis_hashtag_paginated_data(language_id, hashtag_id, page_no):
    if not page_no:
        page_no = 1
    key = 'hashtag:'+str(hashtag_id)+':lang:'+str(language_id)
    paginated_data = get_redis(key)
    topic_ids = []
    topics = []
    if not paginated_data:
        paginated_data = update_redis_hashtag_paginated_data(language_id, {'hashtag__id':hashtag_id})
    if paginated_data and (str(page_no) in paginated_data.keys() or 'remaining' in paginated_data.keys()):
        if str(page_no) in paginated_data.keys():
            topic_ids = paginated_data[str(page_no)]['id_list']
            topics = Topic.objects.filter(pk__in = topic_ids, is_removed = False)
        elif 'remaining' in paginated_data.keys():
            last_page_no = int(paginated_data['remaining']['last_page'])
            try:
                last_page_data = paginated_data[str(last_page_no)]
            except:
                last_page_data = paginated_data[last_page_no]
            topics = Topic.objects.filter(is_vb = True, is_removed = False, language_id = language_id, \
                    hash_tags__id = hashtag_id).exclude(id__in = last_page_data['id_list']).filter(vb_score__lte = last_page_data['scores'][-1])
            new_page = page_no - last_page_no #(191-190)
            paginator = Paginator(topics, settings.REST_FRAMEWORK['PAGE_SIZE'])
            if paginator.num_pages >= new_page:
                topics = list(paginator.page(new_page))
            else:
                topics = []
    else:
        topics = Topic.objects.filter(is_vb = True, is_removed = False, language_id = language_id, \
            hash_tags__id = hashtag_id).order_by('-vb_score')
        paginator = Paginator(topics, settings.REST_FRAMEWORK['PAGE_SIZE'])
        if paginator.num_pages >= page_no:
            topics = list(paginator.page(page_no))
        else:
            topics = []
    print topics,"####"
    return topics

def update_redis_hashtag_paginated_data(language_id, extra_filter, cache_max_pages = settings.CACHE_MAX_PAGES_REAL_TIME):
    try:
        items_per_page = settings.REST_FRAMEWORK['PAGE_SIZE']
        # cache_max_pages = settings.CACHE_MAX_PAGES
        min_rec_to_cache = settings.MIN_REC_TO_CACHE
        # print language_id, "############", extra_filter
        list_page = 0
        final_data = {}
        paginated_data = []
        key = None
        from forum.topic.models import HashtagViewCounter
        hash_df = pd.DataFrame.from_records(HashtagViewCounter.objects.filter(language = language_id).filter(**extra_filter)\
                .order_by('-hashtag__is_popular', '-hashtag__popular_date', '-view_count').values('hashtag__id', 'video_count'))
        while(list_page != None):
            page_data = hash_df[(list_page*items_per_page):((list_page+1)*items_per_page)]
            item_list = page_data['hashtag__id'].tolist()
            count_list = page_data['video_count'].tolist()

            if page_data.empty or list_page >= cache_max_pages:
                list_page = None
            else:
                paginated_data.append({ (list_page+1) : item_list })
                list_page += 1

                loop_counter = 0
                for each_rec in item_list:
                    key = 'hashtag:'+str(each_rec)+':lang:'+str(language_id)
                    loop_counter += 1
                    if count_list[loop_counter-1] <= min_rec_to_cache:
                        # print 'Skipping... not gte ' + str(min_rec_to_cache)
                        continue
                    page = 1
                    final_data = {}
                    exclude_ids = []
                    query = Topic.objects.filter(is_removed = False, is_vb = True, hash_tags__id = each_rec, language_id = language_id)
                    final_data = update_redis_paginated_data(key, query)            
        if key:
            return get_redis(key)
        return final_data
    except:
        return {}

