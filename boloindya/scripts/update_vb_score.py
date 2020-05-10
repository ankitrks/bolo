from datetime import datetime, timedelta, date
from forum.topic.models import Topic
from forum.user.models import UserProfile, Weight
from forum.category.models import Category
from drf_spirit.utils import language_options
from datetime import datetime
from redis_utils import * 
from jarvis.models import FCMDevice
from django.conf import settings 
from forum.topic.utils import update_redis_hashtag_paginated_data, update_redis_paginated_data

def run():
    now = datetime.now()
    all_post = False
    if all_post:
        last_modified_post = Topic.objects.filter(is_vb=True).order_by('-date')
    else:
        last_modified_post = Topic.objects.filter(is_vb=True,is_removed=False,last_modified__gt=now-timedelta(days=700)).order_by('-date')
    total_elements = len(last_modified_post)
    counter=1
    for each_post in last_modified_post:
        print "###########",counter,"/",total_elements,"###########"
        print "old score:  ",each_post.vb_score
        new_score = each_post.calculate_vb_score()
        counter+=1
        print "new score:  ",new_score

    start_total = datetime.now()
    for each_language in language_options:
        if not each_language[0] == '0':
            start = datetime.now()
            for each_category in Category.objects.filter(parent__isnull=False):
                inside_start = datetime.now()
                key = 'cat:'+str(each_category.id)+':lang:'+str(each_language[0])
                query = Topic.objects.filter(is_vb=True,is_removed=False,m2mcategory__id = each_category.id,language_id = each_language[0])
                final_data = update_redis_paginated_data(key, query, settings.CACHE_MAX_PAGES)
                # print final_data
                end = datetime.now()
                print 'Runtime: Category'+str(each_category.title)+' Language ' + str(each_language[1]) + ' is ' + str(end - inside_start)
            end = datetime.now()
            print 'Runtime: Category Language ' + str(each_language[1]) + ' is ' + str(end - start)
            print "\n\n\n\n"
    print 'Runtime Total Category Language is ' + str(datetime.now() - start_total)
    start_total = datetime.now()
    for each_language in language_options:
        if not each_language[0] == '0':
            start = datetime.now()
            final_data = update_redis_hashtag_paginated_data(each_language[0], {}, settings.CACHE_MAX_PAGES)
            # print final_data
            end = datetime.now()
            print 'Runtime: hashtag language ' + str(each_language[1]) + ' is ' + str(end - start)
            print "\n\n\n\n"
    print 'Runtime  hashtag language Total is ' + str(datetime.now() - start_total)
    start_total = datetime.now()
    for each_language in language_options:
        if not each_language[0] == '0':
            start = datetime.now()
            key = 'lang:'+str(each_language[0])
            query = Topic.objects.filter(is_removed=False,is_vb=True,language_id=each_language[0])
            final_data = update_redis_paginated_data(key, query, settings.CACHE_MAX_PAGES)
            # final_data = update_redis_language_paginated_data(each_language[0])
            # print final_data
            end = datetime.now()
            print 'Runtime: Language ' + str(each_language[1]) + ' is ' + str(end - start)
            print "\n\n\n\n"
    print 'Runtime Language Total is ' + str(datetime.now() - start_total)
    print 'total script run time :', str(datetime.now() - now)


