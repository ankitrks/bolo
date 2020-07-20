# -*- coding: utf-8 -*-
from forum.topic.models import *
from forum.user.models import *
from forum.comment.models import *
from django.contrib.auth.models import User
from django.db.models import Sum
import calendar
from drf_spirit.utils import shorcountertopic, calculate_encashable_details, state_language, language_options,short_time,shortcounterprofile
import random
from forum.user.utils.bolo_redis import update_profile_counter
from datetime import datetime, timedelta, date
# from drf_spirit.utils import add_bolo_score
from django.apps import apps
from forum.user.models import UserProfile, Weight
from django.contrib.contenttypes.models import ContentType
import copy
import pandas as pd
import gc
import decimal
from forum.user.utils.follow_redis import get_redis_follower,update_redis_follower,get_redis_following,update_redis_following
from drf_spirit.utils import create_random_user
import json



def run():
    counter = 0
    user_count = UserProfile.objects.filter(is_test_user = False).count()
    for each_userprofile in UserProfile.objects.filter(is_test_user = False).order_by('user__date_joined','-vb_count').values('user_id','user__username','user__date_joined'):
        print "#############################",counter," / ",user_count,"#####################################"
        counter+=1
        print each_userprofile['user__date_joined']
        start_date = each_userprofile['user__date_joined'].date().strftime("%d-%m-%Y")
        print start_date
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
        days = calendar.monthrange(int(start_date.year),int(start_date.month))[1]
        end_date = datetime.strptime(str(days)+'-'+str(start_date.month)+'-'+str(start_date.year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
        current_datetime = datetime.now()
        while(current_datetime > start_date):
            try:
                bolo_info=get_old_user_bolo_info(each_userprofile['user_id'],start_date.month,start_date.year)
                print "Old Insight Data for user and month:",each_userprofile['user__username'],start_date.month, start_date.year
                print  "Insight Data:", bolo_info
                print
                if start_date.month == 12:
                    start_date = datetime.strptime('01-01-'+str(start_date.year+1), "%d-%m-%Y")
                else:
                    start_date = datetime.strptime('01-'+str(start_date.month+1)+'-'+str(start_date.year), "%d-%m-%Y")
                days = calendar.monthrange(int(start_date.year),int(start_date.month))[1]
                end_date = datetime.strptime(str(days)+'-'+str(start_date.month)+'-'+str(start_date.year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
            except Exception as e:
                print "Error in: get_old_user_bolo_info", e

        try:

            old_lifetime_bolo_info = get_old_user_bolo_info(each_userprofile['user_id'],None,None)
            print "Old Insight Data lifetime for user:" ,each_userprofile['user__username']
            print old_lifetime_bolo_info
            old_profile_data = get_old_profile_counter(each_userprofile['user_id'])
            print 'old_profile_data',old_profile_data
        except Exception as e:
            print "Error in: lifetime get_old_user_bolo_info, get_old_profile_counter", e

        try:
            ### fix insight_ data
            is_calculated = False
            while(not is_calculated):
                is_calculated=fix_insight_data(each_userprofile['user_id'],'01-04-2019')
        except Exception as e:
            print "Error in: fix_insight_data", e


        set_profile_counter_data = set_profile_counter(each_userprofile['user_id'])
        print "updated_profile data", set_profile_counter_data
        ### fix inactive count discripency
        try:
            fix_active_inactive_view_discrepency(each_userprofile['user_id'])
        except Exception as e:
            print "Error in: fix_active_inactive_view_discrepency", e


        ###
        try:
            fix_follower(each_userprofile['user_id'])
            # pass
        except Exception as e:
            print "Error in: fix_follower", e

        ## update_profile counter
        
        set_profile_counter_data = set_profile_counter(each_userprofile['user_id'])
        print "updated_profile data", set_profile_counter_data


        print each_userprofile['user__date_joined']
        start_date = each_userprofile['user__date_joined'].date().strftime("%d-%m-%Y")
        start_date = datetime.strptime(start_date, "%d-%m-%Y")
        days = calendar.monthrange(int(start_date.year),int(start_date.month))[1]
        end_date = datetime.strptime(str(days)+'-'+str(start_date.month)+'-'+str(start_date.year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
        current_datetime = datetime.now()
        while(current_datetime > start_date):
            try:
                bolo_info = get_new_user_bolo_info(each_userprofile['user_id'],start_date.month,start_date.year)
                print "New Insight Data for user and month:",each_userprofile['user__username'],start_date.month, start_date.year
                print  "Insight Data:", bolo_info
                if start_date.month == 12:
                    start_date = datetime.strptime('01-01-'+str(start_date.year+1), "%d-%m-%Y")
                else:
                    start_date = datetime.strptime('01-'+str(start_date.month+1)+'-'+str(start_date.year), "%d-%m-%Y")
                days = calendar.monthrange(int(start_date.year),int(start_date.month))[1]
                end_date = datetime.strptime(str(days)+'-'+str(start_date.month)+'-'+str(start_date.year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
            except Exception as e:
                print "Error in: get_new_user_bolo_info", e 
        try:
            new_lifetime_bolo_info = get_new_user_bolo_info(each_userprofile['user_id'],None,None)
            print "New Insight Data lifetime for user:" ,each_userprofile['user__username']
            print new_lifetime_bolo_info
            new_profile_data = get_new_profile_counter(each_userprofile['user_id'])
            print 'new_profile_data',new_profile_data
        except Exception as e:
            print "Error in: lifetime get_new_user_bolo_info, get_new_profile_counter", e


def fix_active_inactive_view_discrepency(user_id):
    total_view_count_with_deletd = 0
    all_vb = Topic.objects.filter(user_id=user_id, is_vb=True)
    all_seen_count = all_vb.aggregate(Sum('view_count'))
    if all_seen_count.has_key('view_count__sum') and all_seen_count['view_count__sum']:
        total_view_count_with_deletd = all_seen_count['view_count__sum']
    else:
        total_view_count_with_deletd = 0

    total_view_count_active  = 0
    all_active_view_count = all_vb.filter(is_removed=False).aggregate(Sum('view_count'))
    if all_active_view_count.has_key('view_count__sum') and all_active_view_count['view_count__sum']:
        total_view_count_active = all_active_view_count['view_count__sum']
    else:
        total_view_count_active = 0
    profile_view_count = UserProfile.objects.get(user_id = user_id).view_count
    if total_view_count_with_deletd > total_view_count_active and not profile_view_count == total_view_count_active:
        discripency = total_view_count_with_deletd - total_view_count_active
        print "discripency",discripency
        start_date = datetime.strptime('01-'+str(datetime.now().month)+'-'+str(datetime.now().year), "%d-%m-%Y")
        days = calendar.monthrange(int(start_date.year),int(start_date.month))[1]
        end_date = datetime.strptime(str(days)+'-'+str(start_date.month)+'-'+str(start_date.year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
        temp_count = discripency
        total_active_video = all_vb.filter(is_removed=False).count()
        total_video = all_vb.filter(is_removed=False)
        reamining = int(temp_count%total_active_video)
        per_video_view = int((temp_count-reamining)/total_active_video)

        for each_vb in total_video:
            Topic.objects.filter(pk=each_vb.id).update(view_count = F('view_count')+per_video_view)
            profile_updation = UserProfile.objects.filter(user_id = Topic.objects.get(pk=each_vb.id).user_id).update(own_vb_view_count = F('own_vb_view_count')+per_video_view, view_count = F('view_count')+per_video_view)
            FVBseen.objects.create(topic_id = each_vb.id,view_count =per_video_view,created_at=random_datetime(start_date,end_date))
            update_profile_counter(Topic.objects.get(pk=each_vb.id).user_id,'view_count',per_video_view,True)
            temp_count-=per_video_view
        if reamining:
            Topic.objects.filter(pk=total_video[0].id).update(view_count = F('view_count')+reamining)
            profile_updation = UserProfile.objects.filter(user_id = Topic.objects.get(pk=total_video[0].id).user_id).update(own_vb_view_count = F('own_vb_view_count')+reamining, view_count = F('view_count')+reamining)
            FVBseen.objects.create(topic_id = total_video[0].id,view_count =reamining,created_at=random_datetime(start_date,end_date))
            update_profile_counter(Topic.objects.get(pk=total_video[0].id).user_id,'view_count',reamining,True)
    else:
        print " no discripency",total_view_count_with_deletd,total_view_count_active




def fix_insight_data(user_id,start_date='01-04-2019'):
    user = User.objects.get(pk=user_id)
    start_date = datetime.strptime(start_date, "%d-%m-%Y")
    days = calendar.monthrange(int(start_date.year),int(start_date.month))[1]
    end_date = datetime.strptime(str(days)+'-'+str(start_date.month)+'-'+str(start_date.year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
    current_datetime = datetime.now()
    total_video = Topic.objects.filter(is_vb = True,is_removed=False,user=user,date__gte=start_date, date__lte=end_date)
    total_video_count = total_video.count()
    print "######### fixing for month year", start_date.month,start_date.year
    if total_video_count>0:
        real_view_count = VBseen.objects.filter(topic_id__in = total_video.values_list('pk',flat=True)).count()
        real_view_in_that_month_count = VBseen.objects.filter(topic_id__in = total_video.values_list('pk',flat=True), created_at__gte=start_date, created_at__lte=end_date).count()
        diffrence_in_real_view_count = real_view_count - real_view_in_that_month_count
        # provide_fake_view_count(diffrence_in_real_view_count, total_video,total_video_count, start_date, end_date)
        fake_view_count_in_db = FVBseen.objects.filter(topic_id__in = total_video.values_list('pk',flat=True), created_at__gte=start_date, created_at__lte=end_date).aggregate(Sum('view_count'))
        if fake_view_count_in_db.has_key('view_count__sum') and fake_view_count_in_db['view_count__sum']:
            fake_view_count_in_db = fake_view_count_in_db['view_count__sum']
        else:
            fake_view_count_in_db = 0
    if total_video_count > 0:
        total_view_count = 0
        total_video = Topic.objects.filter(is_vb = True,is_removed=False,user=user,date__gte=start_date, date__lte=end_date)
        for each_vb in total_video:
            total_view_count+=each_vb.view_count


        if total_view_count >= real_view_count:
            fake_view_count = total_view_count - real_view_in_that_month_count - fake_view_count_in_db
            if fake_view_count:
                status = create_fvbseen_entry(fake_view_count, total_video, start_date, end_date)
                if not status:
                    return False
        else:
            print "this case will come very less: it will update  each topic if the real view count is less than the view count and imp count, it will cause little variance in view count"
            for each_vb in total_video:
                real_single_topic_view = VBseen.objects.filter(topic_id = each_vb.id)
                real_single_topic_view_count = real_single_topic_view.count()
                is_changed = False
                if each_vb.view_count < real_single_topic_view_count:
                    each_vb.view_count = real_single_topic_view_count
                    is_changed = True
                if each_vb.imp_count < real_single_topic_view_count:
                    each_vb.imp_count = real_single_topic_view_count
                    is_changed = True
                if is_changed:
                    each_vb.save()
            return False
        try:
            fix_topics_other_count(total_video)
        except Exception as e:
            print "in fix_topics_other_count",e



    if current_datetime > start_date:
        if end_date.month==12:
            year = str(end_date.year+1)
            return fix_insight_data(user_id,'01-01-'+year)
        else:
            month = str(end_date.month+1)
            return fix_insight_data(user_id,'01-'+month+'-'+str(end_date.year))
    return True


# def provide_fake_view_count(count, total_video,total_video_count, start_date, end_date):
#     temp_count = count
#     reamining = int(count%total_video_count)
#     per_video_view = int((count-reamining)/total_video_count)
#     for each_vb in total_video:
#         Topic.objects.filter(pk=each_vb.id).update(view_count = F('view_count')+per_video_view)
#         profile_updation = UserProfile.objects.filter(user_id = Topic.objects.get(pk=each_vb.id).user_id).update(own_vb_view_count = F('own_vb_view_count')+per_video_view, view_count = F('view_count')+per_video_view)
#         # FVBseen.objects.create(topic_id = each_vb.id,view_count =per_video_view,created_at=random_datetime(each_vb.date,end_date))
#         update_profile_counter(Topic.objects.get(pk=each_vb.id).user_id,'view_count',per_video_view,True)
#         temp_count-=per_video_view
#     if reamining:
#         Topic.objects.filter(pk=total_video[0].id).update(view_count = F('view_count')+reamining)
#         profile_updation = UserProfile.objects.filter(user_id = Topic.objects.get(pk=total_video[0].id).user_id).update(own_vb_view_count = F('own_vb_view_count')+reamining, view_count = F('view_count')+reamining)
#         # FVBseen.objects.create(topic_id = each_vb[0].id,view_count =reamining,created_at=random_datetime(each_vb.date,end_date))
#         update_profile_counter(Topic.objects.get(pk=total_video[0].id).user_id,'view_count',reamining,True)

def create_fvbseen_entry(count, total_video, start_date, end_date):
    temp_count = count
    status = check_for_count_fix(total_video)
    if not status:
        return status

    for each_vb in total_video:
        print "creating fake entry"
        real_single_topic_view = VBseen.objects.filter(topic_id = each_vb.id)
        real_single_topic_view_count = real_single_topic_view.count()
        if each_vb.view_count > real_single_topic_view_count:
            fake_counts = each_vb.view_count - real_single_topic_view_count
            print fake_counts
            if temp_count > fake_counts:
                FVBseen.objects.create(topic_id = each_vb.id,view_count =fake_counts,created_at=random_datetime(each_vb.date,end_date))
                temp_count-=fake_counts
            elif temp_count and temp_count > 0:
                FVBseen.objects.create(topic_id = each_vb.id,view_count =temp_count,created_at=random_datetime(each_vb.date,end_date))
                temp_count-=temp_count
            elif temp_count == 0  or temp_count < 0:
                break

    if temp_count > 0:
        FVBseen.objects.create(topic_id = total_video[0].id,view_count =temp_count,created_at=random_datetime(each_vb.date,end_date))
    return True

def check_for_count_fix(total_video):
    is_changed = False
    for each_vb in total_video:
        real_single_topic_view = VBseen.objects.filter(topic_id = each_vb.id)
        real_single_topic_view_count = real_single_topic_view.count()
        is_changed = False
        if each_vb.view_count < real_single_topic_view_count:
            each_vb.view_count = real_single_topic_view_count
            is_changed = True
        if each_vb.imp_count < real_single_topic_view_count:
            each_vb.imp_count = real_single_topic_view_count
            is_changed = True
        if is_changed:
            each_vb.save()
    if is_changed:
        return False
    return True

def random_datetime(start, end):
    """Generate a random datetime between `start` and `end`"""
    return start + timedelta(
        # Get a random amount of seconds between `start` and `end`
        seconds=random.randint(0, int((end - start).total_seconds())),
    )

def get_old_profile_counter(user_id):
    my_data = {}
    userprofile = UserProfile.objects.get(user_id = user_id)
    my_data['data_type'] = 'profile_counter'
    my_data['view_count'] = shorcountertopic(userprofile.view_count)
    my_data['video_count'] = shortcounterprofile(userprofile.vb_count)
    my_data['follower_count'] = shortcounterprofile(userprofile.follower_count)
    my_data['follow_count'] = shortcounterprofile(userprofile.follow_count)
    try:
        insight_data = InsightDataDump.objects.get(user_id = user_id,for_month=1,for_year=1970)
    except:
        insight_data = InsightDataDump.objects.create(user_id = user_id,for_month=1,for_year=1970, old_insight_data = json.dumps(my_data))
    return my_data

def get_old_user_bolo_info(user_id,month=None,year=None):
    from drf_spirit.serializers import TopicSerializer
    try:
        start_date = None
        end_date = None
        total_earn = 0
        video_playtime = 0
        spent_time = 0
        total_view_count=0
        total_like_count=0
        total_comment_count = 0
        total_share_count = 0
        user = User.objects.get(pk=user_id)
        if month and year:
            days = calendar.monthrange(int(year),int(month))[1]
            start_date = datetime.strptime('01-'+str(month)+'-'+str(year), "%d-%m-%Y")
            end_date = datetime.strptime(str(days)+'-'+str(month)+'-'+str(year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
        if not start_date or not end_date:
            total_video = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user.id) 
            #total_video_id = list(Topic.objects.filter(is_vb = True, user_id=user.id) .values_list('pk',flat=True))
            total_video_id = list(total_video.values_list('pk',flat=True))
            all_pay = UserPay.objects.filter( user_id=user.id, is_active=True)
            top_3_videos = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user.id) .order_by('-view_count')[:3]
            all_play_time = VideoPlaytime.objects.filter(video_id__in = total_video_id).aggregate(Sum('playtime'))
            if all_play_time.has_key('playtime__sum') and all_play_time['playtime__sum']:
                video_playtime = all_play_time['playtime__sum']
           
        else:
            total_video = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user.id, date__gte=start_date, date__lte=end_date)
            total_video_id = list(Topic.objects.filter(is_vb = True, user_id=user.id, is_removed=False).values_list('pk',flat=True))
            # total_video_id = list(total_video.values_list('pk',flat=True))
            all_pay = UserPay.objects.filter( user_id=user.id, is_active=True,for_month__gte=start_date.month,for_month__lte=start_date.month,\
                for_year__gte=start_date.year,for_year__lte=start_date.year)
            top_3_videos = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user.id, date__gte=start_date, date__lte=end_date).order_by('-view_count')[:3]
            all_play_time = VideoPlaytime.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date,video_id__in = total_video_id).aggregate(Sum('playtime'))
            if all_play_time.has_key('playtime__sum') and all_play_time['playtime__sum']:
                video_playtime = all_play_time['playtime__sum']                

        for each_pay in all_pay:
            total_earn+=each_pay.amount_pay
        total_video_count = total_video.count()
        for each_vb in total_video:
            total_view_count+=each_vb.view_count
            total_like_count+=each_vb.likes_count
            total_comment_count+=each_vb.comment_count
            total_share_count+=each_vb.total_share_count

        total_view_count = shorcountertopic(total_view_count)
        total_comment_count = shorcountertopic(total_comment_count)
        total_like_count = shorcountertopic(total_like_count)
        total_share_count = shorcountertopic(total_share_count)
        video_playtime = short_time(video_playtime)
        data = {'total_video_count' : total_video_count, \
                        'total_view_count':total_view_count,'total_comment_count':total_comment_count,\
                        'total_like_count':total_like_count,'total_share_count':total_share_count,\
                        'total_earn':total_earn,'video_playtime':video_playtime,'spent_time':spent_time,\
                        'bolo_score':shortcounterprofile(user.st.bolo_score)}
        if start_date:
            try:
                insight_data = InsightDataDump.objects.get(user_id = user_id,for_month=start_date.month,for_year=start_date.year)
            except:
                insight_data = InsightDataDump.objects.create(user_id = user_id,for_month=start_date.month,for_year=start_date.year, old_insight_data = json.dumps(data))
        else:
            try:
                insight_data = InsightDataDump.objects.get(user_id = user_id,for_month=None,for_year=None)
            except:
                insight_data = InsightDataDump.objects.create(user_id = user_id,for_month=None,for_year=None, old_insight_data = json.dumps(data))

        return data
    except Exception as e:
        print e
        data = {'total_video_count' : 0, \
                        'monetised_video_count':0, 'total_view_count':'0','total_comment_count':'0',\
                        'total_like_count':'0','total_share_count':'0','left_for_moderation':0,\
                        'total_earn':0,'video_playtime':'0 seconds','spent_time':'0 seconds',\
                        'unmonetizd_video_count':0,\
                        'bolo_score':shortcounterprofile(0)}
        if start_date:
            try:
                insight_data = InsightDataDump.objects.get(user_id = user_id,for_month=start_date.month,for_year=start_date.year)
            except:
                insight_data = InsightDataDump.objects.create(user_id = user_id,for_month=start_date.month,for_year=start_date.year, old_insight_data = json.dumps(data))
        else:
            try:
                insight_data = InsightDataDump.objects.get(user_id = user_id,for_month=None,for_year=None)
            except:
                insight_data = InsightDataDump.objects.create(user_id = user_id,for_month=None,for_year=None, old_insight_data = json.dumps(data))
        return data



def set_profile_counter(user_id):
    # calculating follower count
    real_follower_count = Follower.objects.filter(user_following_id = user_id, is_active = True).distinct('user_follower_id').count()
    redis_follower_counter = len(get_redis_follower(user_id))
    if not real_follower_count == redis_follower_counter:
        delete_redis('bi'+'follower:'+str(user_id))
        get_redis_follower(user_id)

    # calculating following count
    real_follow_count = Follower.objects.filter(user_follower_id = user_id, is_active = True).distinct('user_following_id').count()
    redis_following_counter = len(get_redis_following(user_id))
    if not real_follow_count == redis_following_counter:
        delete_redis('bi'+'following:'+str(user_id))
        get_redis_follower(user_id)

    # calculating view count
    total_video_id = list(Topic.objects.filter(is_vb = True,is_removed=False, user_id=user_id).values_list('pk',flat=True))
    real_view_count = VBseen.objects.filter(topic_id__in = total_video_id).count()
    fake_view_count = FVBseen.objects.filter(topic_id__in = total_video_id).aggregate(Sum('view_count'))
    if fake_view_count.has_key('view_count__sum') and fake_view_count['view_count__sum']:
        fake_view_count = fake_view_count['view_count__sum']
    else:
        fake_view_count = 0
    print real_view_count, fake_view_count
    view_count = real_view_count + fake_view_count

    #total video
    video_count = len(total_video_id)
    UserProfile.objects.filter(user_id = user_id).update(**{'follower_count':real_follower_count, 'follow_count': real_follow_count ,'view_count': view_count, 'vb_count':video_count,'own_vb_view_count':view_count})
    return {'follower_count':real_follower_count, 'follow_count': real_follow_count ,'view_count': view_count, 'video_count':video_count, 'last_updated': datetime.now()}


def get_new_profile_counter(user_id):
    my_data = {}
    userprofile = UserProfile.objects.get(user_id = user_id)
    my_data['data_type'] = 'profile_counter'
    my_data['view_count'] = shorcountertopic(userprofile.view_count)
    my_data['video_count'] = shortcounterprofile(userprofile.vb_count)
    my_data['follower_count'] = shortcounterprofile(userprofile.follower_count)
    my_data['follow_count'] = shortcounterprofile(userprofile.follow_count)
    try:
        insight_data = InsightDataDump.objects.get(user_id = user_id,for_month=1,for_year=1970)
        insight_data.new_insight_data = json.dumps(my_data)
        insight_data.save()
    except:
        insight_data = InsightDataDump.objects.create(user_id = user_id,for_month=1,for_year=1970, new_insight_data = json.dumps(my_data))
    return my_data

def get_new_user_bolo_info(user_id,month=None,year=None):
    from drf_spirit.serializers import TopicSerializer
    try:
        start_date = None
        end_date = None
        total_earn = 0
        video_playtime = 0
        spent_time = 0
        total_view_count=0
        total_like_count=0
        total_comment_count = 0
        total_share_count = 0
        user = User.objects.get(pk=user_id)
        if month and year:
            days = calendar.monthrange(int(year),int(month))[1]
            start_date = datetime.strptime('01-'+str(month)+'-'+str(year), "%d-%m-%Y")
            end_date = datetime.strptime(str(days)+'-'+str(month)+'-'+str(year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
        if not start_date or not end_date:
            total_video = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user.id) 
            #total_video_id = list(Topic.objects.filter(is_vb = True, user_id=user.id) .values_list('pk',flat=True))
            total_video_id = list(total_video.values_list('pk',flat=True))
            total_like_count = Like.objects.filter(topic_id__in = total_video_id, is_active = True).count()
            total_comment_count = Comment.objects.filter(topic_id__in = total_video_id, is_removed = False).count()
            all_pay = UserPay.objects.filter( user_id=user.id, is_active=True)
            top_3_videos = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user.id) .order_by('-view_count')[:3]
            all_play_time = VideoPlaytime.objects.filter(video_id__in = total_video_id).aggregate(Sum('playtime'))
            if all_play_time.has_key('playtime__sum') and all_play_time['playtime__sum']:
                video_playtime = all_play_time['playtime__sum']

            real_view_count = VBseen.objects.filter(topic_id__in = total_video_id).count()
            fake_view_count = FVBseen.objects.filter(topic_id__in = total_video_id).aggregate(Sum('view_count'))
            if fake_view_count.has_key('view_count__sum') and fake_view_count['view_count__sum']:
                fake_view_count = fake_view_count['view_count__sum']
            else:
                fake_view_count = 0
            print real_view_count, fake_view_count
            total_view_count = real_view_count + fake_view_count
           
        else:
            total_video = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user.id, date__gte=start_date, date__lte=end_date)
            total_video_id = list(Topic.objects.filter(is_vb = True, user_id=user.id, is_removed=False).values_list('pk',flat=True))
            # total_video_id = list(total_video.values_list('pk',flat=True))
            total_like_count = Like.objects.filter(topic_id__in = total_video_id, is_active = True, created_at__gte=start_date, created_at__lte=end_date).count()
            total_comment_count = Comment.objects.filter(topic_id__in = total_video_id, is_removed = False, date__gte=start_date, date__lte=end_date).count()
            all_pay = UserPay.objects.filter( user_id=user.id, is_active=True,for_month__gte=start_date.month,for_month__lte=start_date.month,\
                for_year__gte=start_date.year,for_year__lte=start_date.year)
            top_3_videos = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user.id, date__gte=start_date, date__lte=end_date).order_by('-view_count')[:3]
            all_play_time = VideoPlaytime.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date,video_id__in = total_video_id).aggregate(Sum('playtime'))
            if all_play_time.has_key('playtime__sum') and all_play_time['playtime__sum']:
                video_playtime = all_play_time['playtime__sum'] 

            real_view_count = VBseen.objects.filter(topic_id__in = total_video_id, created_at__gte=start_date, created_at__lte=end_date).count()
            fake_view_count = FVBseen.objects.filter(topic_id__in = total_video_id, created_at__gte=start_date, created_at__lte=end_date).aggregate(Sum('view_count'))
            if fake_view_count.has_key('view_count__sum') and fake_view_count['view_count__sum']:
                fake_view_count = fake_view_count['view_count__sum']
            else:
                fake_view_count = 0
            print real_view_count, fake_view_count
            total_view_count = real_view_count + fake_view_count

        for each_pay in all_pay:
            total_earn+=each_pay.amount_pay
        total_video_count = total_video.count()
        for each_vb in total_video:
            total_share_count+=each_vb.total_share_count

        total_view_count = shorcountertopic(total_view_count)
        total_comment_count = shorcountertopic(total_comment_count)
        total_like_count = shorcountertopic(total_like_count)
        total_share_count = shorcountertopic(total_share_count)
        video_playtime = short_time(video_playtime)
        data = {'total_video_count' : total_video_count, \
                        'total_view_count':total_view_count,'total_comment_count':total_comment_count,\
                        'total_like_count':total_like_count,'total_share_count':total_share_count,\
                        'total_earn':total_earn,'video_playtime':video_playtime,'spent_time':spent_time,\
                        'bolo_score':shortcounterprofile(user.st.bolo_score)}
        if start_date:
            insight_data, is_created = InsightDataDump.objects.get_or_create(user_id = user_id,for_month=start_date.month,for_year=start_date.year)
            insight_data.new_insight_data = json.dumps(data)
        else:
            insight_data, is_created = InsightDataDump.objects.get_or_create(user_id = user_id,for_month=None,for_year=None)
            insight_data.new_insight_data = json.dumps(data)
        insight_data.save()
        if start_date and end_date:
            if datetime.now() > end_date + timedelta(days=2) and not datetime.now().month == start_date.month:
                insight_obj, is_created = OldMonthInsightData.objects.get_or_create(user_id = user_id , for_month = start_date.month, for_year = start_date.year)
                insight_obj.insight_data = json.dumps(data)
                insight_obj.save()
        return data
    except Exception as e:
        print e
        data =  {'total_video_count' : 0, \
                        'total_view_count':'0','total_comment_count':'0',\
                        'total_like_count':'0','total_share_count':'0',\
                        'total_earn':0,'video_playtime':'0 seconds','spent_time':'0 seconds',\
                        'bolo_score':shortcounterprofile(0)}
        if start_date:
            insight_data, is_created = InsightDataDump.objects.get_or_create(user_id = user_id,for_month=start_date.month,for_year=start_date.year)
            insight_data.new_insight_data = data
        else:
            insight_data, is_created = InsightDataDump.objects.get_or_create(user_id = user_id,for_month=None,for_year=None)
            insight_data.new_insight_data = data
        insight_data.save()
        return data

def fix_topics_other_count(all_video):
    for each_vb in all_video:
        try:
            print "inlike"
            fix_like(each_vb)
            pass
        except Exception as e:
            print "in fix like", e
        try:
            print "inshare"
            check_share(each_vb)
        except Exception as e:
            print "in share check", e
        try:
            print "incomment"
            check_comment(each_vb)
        except Exception as e:
            print "in comment check", e



def fix_like(each_vb):
    total_like_count = Like.objects.filter(topic_id=each_vb.id, is_active = True).count()
    if total_like_count > each_vb.likes_count:
        print "in updating like"
        each_vb.likes_count = total_like_count
        each_vb.save()
    if total_like_count < each_vb.likes_count:
        print "in fixing like", total_like_count,each_vb.likes_count,each_vb.likes_count - total_like_count
        check_like(each_vb.id,each_vb.likes_count - total_like_count)

def check_comment(each_vb):
    real_comment_count = Comment.objects.filter(topic_id = each_vb.id, is_removed = False).count()
    if each_vb.comment_count < real_comment_count:
        required_comment = real_comment_count - each_vb.comment_count
        user_ids = list(UserProfile.objects.filter(is_test_user=True).values_list('user_id',flat=True)[:required_comment])
        for each_user_id in user_ids:
            action_comment(each_user_id,each_vb.id)

def check_share(each_vb):
    total_share = SocialShare.objects.filter(topic_id= each_vb.id)
    total_share_count = total_share.count()
    if each_vb.total_share_count < total_share_count:
        mismatch_of = total_share_count - each_vb.total_share_count
        fb_share_count = total_share.filter(share_type = '0').count()
        if each_vb.facebook_share_count < fb_share_count:
            fb_mismatch_of = fb_share_count - each_vb.facebook_share_count
            while(fb_mismatch_of):
                action_share(each_vb.id,'facebook_share' )
                fb_mismatch_of-=1
                mismatch_of-=1

        wp_share_count = total_share.filter(share_type = '1').count()
        if each_vb.whatsapp_share_count < wp_share_count:
            wp_mismatch_of = wp_share_count - each_vb.whatsapp_share_count
            while(wp_mismatch_of):
                action_share(each_vb.id,'whatsapp_share' )
                wp_mismatch_of-=1
                mismatch_of-=1

        li_share_count = total_share.filter(share_type = '2').count()
        if each_vb.linkedin_share_count < li_share_count:
            li_mismatch_of = li_share_count - each_vb.linkedin_share_count
            while(li_mismatch_of):
                action_share(each_vb.id,'linkedin_share' )
                li_mismatch_of-=1
                mismatch_of-=1

        tw_share_count = total_share.filter(share_type = '3').count()
        if each_vb.twitter_share_count < tw_share_count:
            tw_mismatch_of = tw_share_count - each_vb.twitter_share_count
            while(tw_mismatch_of):
                action_share(each_vb.id,'twitter_share' )
                tw_mismatch_of-=1
                mismatch_of-=1
        if mismatch_of > 0:
            share_type =['facebook_share','whatsapp_share','linkedin_share','twitter_share']
            share_on = random.choice(share_type)
            action_share(each_vb.id,share_on)


def check_like(topic_id,number_like):
    already_like=None
    now = datetime.now()
    each_like = Topic.objects.get(pk=topic_id)
    already_like = list(Like.objects.filter(topic_id = topic_id).values('user_id','topic_id'))
    user_want_like=[]
    new_vb_like =[]
    to_be_created_bolo=[]
    notific_dic= []
    already_like_user = []
    start_date = each_like.date
    days = calendar.monthrange(int(start_date.year),int(start_date.month))[1]
    end_date = datetime.strptime(str(days)+'-'+str(start_date.month)+'-'+str(start_date.year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
    for each_like_dict in already_like:
        already_like_user.append(each_like_dict['user_id'])
    user_ids = list(UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=already_like_user).values_list('user_id',flat=True)[:number_like])
    i = 0
    for each_id in user_ids:
        user_want_like.append({'user_id':each_id,'topic_id':topic_id,'created_at':random_datetime(start_date,end_date)})
    print number_like,"number_like"
    if user_want_like:
        score = get_weight('liked')
        vb_like_type = ContentType.objects.get(app_label='forum_topic', model='like')
        new_vb_like = user_want_like
        if new_vb_like:
            aList = [Like(**vals) for vals in new_vb_like]
            newly_created = Like.objects.bulk_create(aList, batch_size=10000)
            # Topic.objects.filter(pk=topic_id).update(likes_count = F('likes_count')+len(new_vb_like))
            bolo_increment_user_id = [x['user_id'] for x in new_vb_like]
            bolo_increment_user = UserProfile.objects.filter(user_id__in = bolo_increment_user_id ).update(bolo_score =F('bolo_score')+score,like_count = F('like_count')+1)
            already_liked = list(Like.objects.filter(topic_id = topic_id,user_id__in=[d['user_id'] for d in new_vb_like]).values('user_id','id'))
            for each in already_liked:
                each['action_object_id'] = each['id']
                del each['id']
            to_be_created_bolo= already_liked
            action = get_weight_object('liked')
            notific_dic = copy.deepcopy(to_be_created_bolo)
            if score > 0:
                for each_bolo in to_be_created_bolo:
                    each_bolo['action'] = action
                    each_bolo['score'] = score
                    each_bolo['action_object_type'] = vb_like_type
                aList = [BoloActionHistory(**vals) for vals in to_be_created_bolo]
                newly_bolo = BoloActionHistory.objects.bulk_create(aList, batch_size=10000)

#share
def action_share(topic_id, share_on):
    topic = get_topic(topic_id)
    if share_on == 'facebook_share':
        topic.update(facebook_share_count = F('facebook_share_count')+1 )  
        topic.update(total_share_count = F('total_share_count')+1)
    elif share_on == 'whatsapp_share':
        topic.update(whatsapp_share_count = F('whatsapp_share_count')+1)
        topic.update(total_share_count = F('total_share_count')+1)
    elif share_on == 'linkedin_share':
        topic.update(linkedin_share_count = F('linkedin_share_count')+1)
        topic.update(total_share_count = F('total_share_count')+1)
    elif share_on == 'twitter_share':
        topic.update(twitter_share_count = F('twitter_share_count')+1)
        topic.update(total_share_count = F('total_share_count')+1)

#comment
def action_comment(user_id,topic_id):
    comment_list = ["Good way of making people understand","Your videos really help.","Your depth and understanding is commendable...you are doing a great job..stay blessed","Very very helpful, thank you","Thanks for the effort.","i really apperciate your wonderful explanation","thank you  for your research on topic.....respect....!!!!!!","Very informative ","Actually , your voice soothes mind","Thank you for your time on the research and explain on this topic. Impressive !","Thanks a lot to You !!","ur way of explaining issues is quiet different. So easy","Extremely good brief explanation","great explaination thank you for your efforts","Wow, it was an amazing explanation","Quite insightful","Thank you very much .. U gav me exactly what i was looking for","thanks fr making me understand so nicely.","These are so informative and clearing out all basic confusions","Hello... I am following all your videos","Thanks you so much  for creating my interest on studies","I am so thankful to you for providing such information","I appreciate your method to avail us such information.","you are just wonderful... thank you so much.","Thankyou so much for the great great great explanation ","Great job ...really I watched your video so carefully and honestly........ Thank you ","Well Done, very informative video with all details. keep it up brother","feeling blessed to see your videos. Love.","Very well explained, made easy to understand,, Thank you so much","This video is awesome and thanks for it.","One of the best content video available for this issue!","Thanks a tone for making such efforts.","Truly liked this","Nicely presented, this lecture made clear understanding !","Every concept explained in a very lucid way.Great great great video","u always make amazing videos","Thank you so much  ji","You are a good, knowledged person..... We have been learning from your brain, thank you for the efforts..","This is very interesting knowledge for me..I think all people. Thanks.","Very well explained, thank you","Thanks mate u have great knolwedge sharing skills","U make everything really easy to understand","u have cleared our whole concept regarding the issue thanks a lot for this","ur learning journey fruitful day by day","Excellent explaination and superb sequence selection.","No one can explain with this conviction , thank you","keep the work going","Very informative lecture","Awesome video... searching for such type of knowledgeable video","I really like your video very much","u r great I like so much this video","I am happy that your good knowledge","Very nice video. Very clear and detailed explanation. Thank you for this","The video is really explanatory. Very good work","Incredibly you shared the knowledge and view","Very informative and helpful video. Please keep it up","Could you please provide more of this type video","Very interesting and informative","Very interesting and informative","Your narrative version is imppecable...too good explaination","nice analysis keep it up","Thanks . Well explained","Point to point... thank you so much","This video is so good and easy to understand","Thank you ..... for giving this video","Superrrrrrrb. thanks for making this type of marvelous video.keep it up","Very good lecture,Thanks for sharing knowledge.","I salute your dedication .. great video...","You explain it very coherently thanks.","Your videos are very informative... Thanks","Very informative and neutral view good job","Excellent.Thankyou ","Explained very clear ...thank you.","I'm extremely thankful for these amazing videos that u make","Very informative..keep them going","Very informative & explained in a lucid manner.","very detailed explanation for a very complex topic","Fantastic video good knowledge provided by you hats off to you","nice video with full of information and understandable.","One of the best video of study","Thanxs  for giving such a nice knowledge.","wonderful explanation...","very nice explanation... doubts cleared","Well explained, most of the topics covered lucidly.","Interestingly ending the topic for peaceful resolution is appreciated.","Very beutifully explained .Hatts off....Great....","Fantastic,nicely explained.","Thanks for best Presentation.","Brilliant job dear","The video was very informative","Very well described . Thanks","Very nice video ....clear understanding of the topic..","Very informative video. Hats off to you.","You are doing a tremendous job.","appreciate your efforts your narrating is best","great source of information.","very good knowledge ","thanks for the video, very informative for all of us….","Excellent...cleared all the doubts","amazing course superb way of explaining things Impressive voice","nice love you all members please keep it up ????","very informative","fantastic explaining gestures u have!!!! made me fall for your content!!! bestie for future love to get in touch with ur positivity","really awesome","thank you ","Superb","Great!","so...nice","good knowledge","interesting","Thank you so much Ma'am","its very usefull","fine , it is good for gk","Thank you so much mam this is really great explain","Great job! thank you","Good work","It's very useful","it's a fantastic initiative......for learners.","realy it is more useful..","excellent teaching skill and the way is very interesting for understanding ,good job","beautiful presentation. enjoying the new approach to learning. thank you","it's always good to know this things thankyou please continue.","Thanks alot mam.... Unbelievable things I came to know","ur voice...wowwww","Very nice piece of information. Its Amazing !!","interesting .. good teaching...","awesome video, very interesting","wonderfully explained..!","Thanks good info","wow... amazing teaching","quite interesting","Mind blowing.....","interesting...","Gr8 JOB!","perfectly explained . very clear..👍","it's beneficial for us way it taught make good","Wonderful","Very nicely explained... Please keep enriching our knowledge with this daily trivia plan..!!!","cool...","interesting thank for the knowledge","Excellent....","awesome","knowledge is the door of the oppertunity to something get new","wow its really amazing","its so great","excellent!, ur pronunciation and teaching method are so good..... when watching this i really enjoyed.","it is wonderful....","thanks a lot","awesome graphics , awesome presentation.","Information as well as presentation both were superb. Thanks","Just wow..","love the the way u teach","I would like. please continue this course. thanks again.","amazing","Nice lactur","Excellent Explain.","I like the way u learn bcoz it's Very easy to understand nd interesting also thanks keep Guiding","Thank you so much","some point but describe easily all..best way I think it's lajawab..have. a good day..","I started today only. but I am like addicted I kept on going","Your voice made me to love the reading and learning the comoplex concepts in crystal clear .","I hv never commented till date, but must praise ur way of eliminating options n getting answers.... Superb man! N yes ur voice is the best i hv ever heard","What a voice !!!","Amazing explanation.thanks :-)","U r so talented., I just can't believe u know so many facts.. Are u a cimputed or an encyclopedia","Explanation is good","Believe me you are a genius......!!!","love ur explanation n you voice too","lovely, what an explanation.Boring things even become easier in this way","way you explain it's great and your voice so innocent..","Awesome explanation!!!","I like the sound of ur accent","Superb .. no words... Brilliant 😊","Ur voice !! And obviously very good video. Thumbs up to your dedication for helping us","thanks alot , it will really help me","great job","Bdw good explanation though..","What a voice 😍","Got to know how we have to look into a question and element the wrong one's.. thanks you","what are the points one must note or study","it's a great technique","Very informative video","wow ! thanks","great work ","thank you so much....","Your way of explaining is too good to leave","Nice ","Great, more helpful","really useful","very nice ","you really have a nice voice","Outstanding pure worth to watch this video","Good job ...","too good","Nice","Thank you so much  please aisi video or banaye","Nice explanation with logic ...","more usefull information","your voice sounds like experiance guy"," your voice is too good....","Voice 👌👌","Wonderful explanation...","Ur superb ","wow, I need these types of video more.","great analysis...waiting for next videos..thanks","brilliant!!👌","Nice explaination !","awesome video","u hav an amazing voice ....just makes me do study hard .","u explains amazingly amazing........","Nicely explained. ...........","Super teaching","Thank you very much.....","Pleasant voice 👍👍👍","It make lot of sense...","thank you ! please help with other sections also.","This was great , I mean seriously the best !","excellent clarification ","Great explanation with clear pronunciation.","good ","Awesome buddy","thnx .. keep up the good work","thankyou","Your voice very sweet and english is very perfect wao nice"," plz makes more videos on this... Plz..","Thank you very much  for a wonderful and clear explanation. Btw your voice is very pleasant. Everyone gets addicted to your voice.","Ur way of explaining things is really good..","pure explanation","Yeh !! Thanks ","Great Effort ... Thanku!!!","Plz bring more such types of analysation","Blessed with mesmerizing voice","thanks please upload some more videos of same","Gud job ya","It's easyyyyy","Thank you  more update","Nicely explained and Oh My God..the voice..amazing bro.... keep it up...need more videos","Superb  I'm speechless","THANK You! So much , helping us with your great idea, Now i understand!! Really helpful!","Shaandaar explanation Thanks ","Amazing..... :)","you are a gem... 😊😊","thank you . its really helpful","u r absolutely marvelous....","perfect","Your all videos are outstanding ","great explanation....... i learnt how to related different things to reach destinations........... thankyou ","this is brilliant keep it coming !","Gr8","One of the Best analysis I have ever seen .. n what a charismatic voice !! Too good","explaning it in less time.. is also beneficial for us thank for it....","gud job..appreciations...","I have seen all your videos. They are amazing. This is something that reached my expectations after a lot of ground work.","Excellent work . Thank you so much. Please do more videos covering all the subjects. Thank you :)","Awesome ...gr8 job ur1 hlping lot of students...","ur nailed it bro",", i wish i would be as knowledgeble as u r. U analysed it very well n ur voice made me to listen it."," Thank you so much for the great explanation and ideas that you are giving us. May God continue to bless you for your good work.","This is free therapy to me... Cheers - keep up","nice explanation... it's very clear","Excellent ","I think I have nothing to say about this vid bcoz people have already stolen all the words which I want to say Thanks for the wonderful explanation","Perfect explanations thank you ","Grt ","thanks for sharing such info as it helps students.","the way you speak... .....Simply awesome","plz u make more video bcz u analysis with all point","you're so smart.","What a voice.. Simply adorable... And very well explained ","Nice strategies to solve","Thank you so much  for your conspicuous video.. You have such a clarity of thought in handling the questions..","Impresive","nice work r","Ur voice dear so soothing. Thank you for the lesson","I was AMAZED by your Great Explanation and voice","Woahhhh....!!!!","thanks a lot","Muze bahot Pasand Aya video....Mai bhi Kuch banna chahti hu...","I liked the way , how you pronounced","You are very good ...thanks for putting enormous efforts for us","Wow.... I don't have words to explain your excellency ... Thank you so much","Very very very very nyc explanation","you are osssome.","Veryyyyy intelligent .......  plz make more videos like this ...very helpful.","There is something special in your voice... that's very motivating...☺","please make more video for other topics too...","osm approach.....","Very accurate explanations.!! We would like to see more papers solved. Thank you","👍👍👍👍 knowelegeble","thanks ","Dhnyawad 🙏","Excellent","Ghazab explanation.!","Very good explanation ..... Plz gve ur conct Nmbr","Good job ","wonderful.......Thanks","please upload other topics analysis","I m in love wd ur the way of communication","Very nicely explained ..Thank you","Soooooooooo gud....😘😍","Gud explanation.. Thank a lot ","your analysis is very much useful..actually, is paving path ...awesome","what a voice....","expecting more videos from you  ,thank u","Very Thankful to you , nice explanation to each and every question.......,......","Hi and thankss for uploading this video. Although I would request you to upload more video","thanks a lot !! thump up !!","Thanks a lot  g....","Thank you  this information..","fan ban gaya, thnq ","awesome  ji thank you so much","Very useful for future","mujhe to bhut help mili thnks wonderfull aise hi lecture provide kijiye","Please make for other topics also","Make similar video for other topics also","well explained bro","Thank you Guruji🙏🙏","Nice vdo ","thankyou for guidance","Good explanation keep rocking","thanks a lot for making ma'am","Thank you so much for this contribution and for your precious time.","thanx a lot","thanks so much","NICE ","👍😊 You're the best","Helpful","Mam you are just amazing","thank you very much! please do not stop making this in the mid way, try to continue","Very marvelous deed ","I hope this course doesn't end abruptly....","It's going to be a great approach .","pls continue it  for a life long","thank you  plzzzzz continue🙏","The great initiative","that's amazing :-)","good one","not bad...","awsum","thank u so much ..","mind blowing ","i honestly watched it out of plain curiosity.. loved it.. thankyou","👍","👍👍","👍👍👍","🙏","🙏🙏","🙏🙏🙏","👍😊","😘😍","😘😍😘😍","👌👌","👌","👌👌👌"]
    comment_list+= ["i honestly watched it out of plain curiosity.. loved it.. thankyou","Your videos really help.","Your depth and understanding is commendable...you are doing a great job..stay blessed","Very very helpfull for my study, thanks you","Thanks for the effort.","i really apperciate your wonderful explanation","thank you for your research on topic.....respect....!!!!!!","Very informative","Actually, your voice soothes mind","Thank you for your time on the research and explain on this topic. Impressive !","Thanks a lot to You!!","ur way of explaining issues is quiet different. So easy","Extremely good brief explanation","great explaination thank you for your efforts","Wow, it was an amazing explanation","Quite insightful","Thank you very much .. U gav me exactly what i was looking for","thanks fr making me understand so nicely.","These are so informative and clearing out all basic confusions","Hello... I am following all your videos","Thanks you so much for creating my interest on studies","I am so thankful to you for providing such information","I appreciate your method to avail us such information.","you are just wonderful... thank you so much.","Thankyou so much for the great great great explanation","Great job...really I watched your video so carefully and honestly........ Thank you","Well Done, very informative video with all details. keep it up brother","feeling blessed. Love from Bangladesh","Very well explained, made easy to understand,, Thank you so much","This video is awesome and thanks for it.","One of the best content video available for this issue!","Thanks a tone for making such efforts.","Truly liked this","Nicely presented, this lecture made clear understanding !","Every concept explained in a very lucid way.Great great great video","u always make amazing videos","Thank you so much","you are a good, knowledged pedagogue..... We have been learning from your brain, thank you for the efforts..","This is very interesting knowledge for me..I think all people. Thanks.","Very well explained, thank you","Thanks mate u have great teaching skills","U make everything really easy to understand","u have cleared our whole concept regarding the issue thanks a lot for this","ur learning journey fruitful day by day","Excellent explaination and superb sequence selection.","No one can explain with this conviction , thank you","keep the work going","Very informative lecture","Awesome video... searching for such type of knowledgeable video","I really like your video very much","u r great I like so much this video","I am happy that your good knowledge","Very nice video. Very clear and detailed explanation. Thank you for this","The video is really explanatory. Very good work","Incredibly you taught","Very informative and helpful video. Please keep it up","Could you please provide more of this type video","Very interesting and informative","Your narrative version is imppecable...too good explaination","nice analysis keep it up","Thanks.. Well explained","Point to point... thank you so much","this video is so good and easy to understand","Thank you..... for giving this video","Superrrrrrrb. thanks for making this type of marvelous video.keep it up","Very good lecture,Thanks for sharing knowledge.","I salute your dedication... great video...","You explain it very coherently thanks.","Your videos are very informative... Thanks","Very informative and neutral view good job","Excellent.Thankyou","Explained very clear ...thank you.","I'm extremely thankful for these amazing videos that u make","Very informative..keep them going","Very informative & explained in a lucid manner.","very detailed explanation for a very complex topic","Fantastic video good knowledge provided by you hats off to you","nice video with full of information and understandable.","One of the best video of study","Thanxs for giving such a nice knowledge.","wonderful explanation...","very nice explanation... doubts cleared","Well explained, most of the topics covered lucidly.","Interestingly ending the topic for peaceful resolution is appreciated.","Very beutifully explained..Hatts off....Great....","Fantastic,nicely explained.","Thanks for best Presentation.","Brilliant job dear","The video was very informative","Very well described. Thanks","Very nice video ....clear understanding of the topic..","Very informative video. Hats off to you.","You are doing a tremendous job.","appreciate your efforts your narrating is best","great source of information.","very good knowledge","thanks for the video, very informative for all of us….","Excellent...cleared all the doubts","mind blowing","thank u so much ..","awsum","not bad...","good one","that's amazing","The great initiative","thank you  plzzzzz continue ","pls continue it  for a life long","It's going to be a great approach .","Very marvelous deed","I hope this course doesn't end abruptly....","thank you very much! please do not stop making thi mid way, try to continue","you are just amazing","You're the best","Helpful","NICE","thanks so much","thanx a lot","Thank you so much for this contribution and for you precious time.","thanks a lot","Good explanation keep rocking","thankyou for guidance","Nice vdo","Thank you","well explained bro","Make similar video for other topics also","provide kijiye","awesome thank you so much","Please make for other topics also","fan ban gaya, thnq","Thank you  this information..","Thanks a lot  g....","thanks a lot !! thump up !!","it is wonderful.... thanks a lot","Hi and thankss for uploading this video. Although I would request you to upload more video","Very Thankful to you , nice explanation to each and every","question.......","expecting more videos from you  ,thank u","what a voice....","your analysis is very much useful..actually, is paving path ...","awesome","Gud explanation.. Thank a lot","Soooooooooo gud....  ","Very nicely explained ..Thank you","I m in love wd ur the way of communication","please upload other topics analysis","wonderful.......Thanks","Good job","Very good explanation ..... Plz gve ur conct Nmbr","Ghazab explanation.!","Excellent","Dhnyawad ","thanks","   lovely","Very accurate explanations.!! We would like to see more papers solved. Thank you","osm approach....","please make more video for other topics too...","There is something special in your voice... that's very motivating..","Veryyyyy intelligent .......  plz make more videos like this ...","very helpful.","you are osssome.","Very very very very nyc explanation","Wow.... I don't have words to explain your excellency ...","Thank you so much","You are very good ...thanks for putting enormous efforts for","us","I liked the way , how you pronounced","Muze bahot Pasand Aya video","thanks a lot","Woahhhh....!!!!","I was AMAZED by your Great Explanation and voice","Ur voice dear so soothing. Thank you for the lesson","nice work r","brilliant!! ","great analysis...waiting for next videos..thanks","wow, I need these types of video more.","U r superb","Wonderful explanation...","Voice   ","your voice is too good....","your voice sounds like experiance guy","more usefull information","hank you so much  please aisi video or banaye","too good","Good job ...","Outstanding pure worth to watch this video","you really have a nice voice","really useful","Great, more helpful","Your way of explaining is too good to leave","thank you so much...","great work","it's a great technique Very informative video wow ! thanks","love the the way u teach","Just wow..","Information as well as presentation both were superb. Thanks","awesome graphics , awesome presentation.","it is wonderful.... thanks a lot","Good……… video","Video bahut acha laga","The knowledge is the best","Make more videos","that was really ossam, n powerfu","Really I tried it a lot and my brain bacame supercompute","Excllent knowledge","Itni easy language me samjhane k liye thnx","Thanks sir Yeh Vdo Banane keliye","Thanks for the knowledge","Amazing vide","Amazing video lots of thanks for this video.","please daily video upload Kiya karo","Good Amazing and interesting","Do every work on full concentration","everything will easy","Good as earlier","Accha nahi bhut accha laga","Thanks for this video ","Hope it will be helpfull","Unbelievable knowledge","Informative bro","Thanks Love you","This video is unique and knowledgefull","You are really very great ","Thanks for your knowledge ","Lovly video for this watching video","Thank you","Thanks Sir nice information","Video bhut achha h","Thanks dear","Video jabardast he","make more videos on study","thx u so much","Amazing video","Superb","Impressive video","very nice information","Good job","Superb video","Sometimes words are not enough to express what you feel.","Awesome and strange coincidence","Thank you so much for providing this knowledge.","Very Interesting","Mast knowledge di hai","Great work","Keep it up","I am looking this video","Great content, great topics","Clear voice. I like it to hear. And interesting","Thanks sir. For Developing our knowledge.","Thank you once again","Thank you for made this","Wow what an amazing knowledge","want more videos like this","Mast Video","i salute you for this ","That was great carry on give us more video","SO COOL AND CRAZY","Just amezing........ Amezing","Very very very interesting","osmmm video","Your videos are really good and great","Great work ","it's amaze","Mind blowing","Lots of love","I'm just shocked.","Wow Amazing","I really really really really like this vedio","it is very important video","OMG!!","Unbelievable how you","You r fantastic","U r the best","Superb","One of the best video","Thanks for information","Nice work information","Your information is true","Mind blowing video","Amazing vedio","O my god","Super 🤟 video","really very nyc excellent","thumbs up","One of the most awesome video","I liked it really good","Nice information","Beautiful","Best video.","Wow awesome","Wow..... superb.... nice ...awesome....","It was more than owesome","Your video is very good","nice knowledge","Superrrrr ","You are great","Very interesting","Really bahut achchhi jankari dee he","i love this","OMG","Thank you very much sir for very useful informations and knowledge.","Fantastic one ","please make more videos","great video ","It's so helpful ","thankuuu","Very helpful ","thank you so much","Heartly thank you","Make a video the same in English-language","Thanks a lot ","Thank you for helping us..... U deserve all the appreciation ","Thanking you","Brilliant explanation","Such a helpful video","Mindblowing","Nyc explaination","Outstanding information Thanks a lot","thanks for this useful vedio","It's too good thanks","Tnx for usefull information","Thankyou so much for give information","thanks making this vedio","Good thank you","VERY VERY THANKS","Brilliant lecture","thank you very much","Many many thankyou","thank u so much ","thanks a lot....","please upload the same in english","Good information","make more vedios please","vry nyc","Best video","Very helpful video thank you so much sir","Thanks a lot","Please make video on travel","Oh nice ....","Nice video","good job","Awesome video","Great video","Nice one","Very good!!!!!","Hearty thank you","Very useful. Useful","Very nice video....","Superb content","excellent","amazing thank you for that","v.informative","thank you.","Well said","Very beautiful ","Thank u","it's very beautiful","all are useful for us","great knowledge","Well explained","it's very amazing video","Thank you so much","wow thnx.....nice nice","too useful ","Thnk u for the video","ty very much ","so clear great","So sweet","Your video is so imaginative ","Marvelous","Thanks 😊😊","awesome one","NYC hardwork","fantastic","Great video","Too good","Very well","So useful for social media","Useful word","best","Nice clip","Too good video","It helps me alot. ","Keep making like this","Best of luck for new videos","Your video is very useful","very Nice","Speechless","Nyyc","Wow its very useful for me.","Keep Sharing, Keep Loving","Everyone: mmmmMmmMmmmm","Ur just like GOOSEBUMPS","I just got tears when you mentioned","That was awesome","truly good!","artists.. keep going..","I liked","my feed love you","I appreciated.","must be proud","One of the best video.","SALUTE TO YOU..","What a talent..","awsum   ","tooooo cute!!!!!","unstoppable","Who's Agree","I'm very happy","Best of the best","This is really great ","really love it","A helpful","very nice","good Idea'tyy","Thanks for your videos","Thnk u ","Thanks you so much .","It is absolutely right","I got good result","Thanks for giving me technique","helpful for me","Most effective ","great ...tnq sir ","that was absolutely great ","Thanks a lot ","This the best video i have ever seen","Very Nice and useful also.","Thanku so much","U r great","I tried this thank","Osm sach a great information","😁😁😁thanku","Thank you. for advice","Thank u very much","your video is best","Thank you very much it's very helpful","Love this video it helps","That's great","thank u v much","perfect knowledge","I like your video","it really helps me","best vidow I have ever seen","Thank youfor motivation.","So, thank you so much.","it is so amazing","I need more videos","Honestly Your video was very inspired me","salute u too good....","Best idea and very helpful","Thank's for your statement","It's a good video. ","Thank you so so much 😍","excellent its best for everyone..","This video is very helpful","This is amazing Thanku ","Thank u so much ","Thank you so much 💖💖💖💖💖","Nice vedio ","Thanks for this Video...☺️","It's really a good video 👏","Hii thnk u for your videos.","It's working for me","It will definitely help us..","very important information ","very powerful technic","its awsm","Great..","nice video ","Awsome lecture","Really informative and thanks a lottttt","So helpful.","love a lot.","Nyc superb","thanks a lot","Nice work.. thanks a lot..","this was really helpfull","thanks you so much ","that is very helpful.","a perfect material","Lots of information presented","keep it up","Simply awesome.","Thank you very much for this awesome video","Your video is very useful ","I love ur voice.. Thanks a lot..","you have great knowledge","What a explanation hats off to you","Great effort","Super !!","Thanks it's so helpful for me thanks a lot for this","really informative and easy to understand.","Thank you. You made the video","your way of expatiation is Awesome","thank you so much!!!!","adorable.","Nice video with conceptual clarity","ur lecture is awesome.","your way of expatiation is Awesome and adorable.","it is really very good.","Best vdo best explanation thank you","Wonderful work","Very nice way of teaching, truely admirable.","Thank you 💐💐","this video so good","understand in detail","Really Fruitful knowledge","absolutely glorious","very very productive....thanks a lot","nice video for knowldge","Thank you i hope you doing well....!!","very helpful. thank you so much for this video.","Excellent presentation ","your a great..","You are making it simple .","Bless you ","you are really good in explaining it..!!","u r perfect...thank u so much","Amaziggg awesome","Thankyou ....God bless you.","Tnku somuch for the information","Nice video though","Awesome Way of Explanation.","explained.. Superb ","it was awesome","Such an informative","u are aws..... Thank u so much","for such a great explanation","Thank you so much 💓","Very useful video..","concept clear ho gei,thanku","Very amazing..!!!","Thank you very very much","for this beautiful information.","very useful information plz continue. thank u","Very very very very nice ","explained very well.","Good Job..👍, really thanks","Thank u so much more","so plzz make more vedios like this .","Thanks alot. 😊 great work","Thank you for your insighful videos..Keep it going","Good job dear","Video is good.","thankyou!!!","Great work","Excellent,","Very helpful video.., thank u so much ","Very good!!","Very very thankful","Thanx allot for this. 😁","vow.","u are great","thank you so much","i love the way u explain","it,s easy nd simple 🙏Thankew","begin with sweet.","Well done ","loved ur work and loved ur accent.","woooow…","Excellant....","Delicious😊😊😊","Excellent!!","Sundar","Great video. Loved ","You guys are awesome","Loved it!","Love u always bong guys","big Hug from me.","Wonderful.","You have a fantastic","skills.. Nicely done video.","Outstanding. One of my favorite dish","Loved every steps and moves ","keep up the good work 👍","hats off to you guys.","really very Very delicious ","Thanks fr making","the video and atlast it's up","Awesome video! Absolutely","hopefully.","Speechless","It's that good.","Well Done","Oh my my beautiful clarification","so sweet .","Good way of making people understand","Your videos really help.","Your depth and understanding is commendable...you are doing a great job..stay blessed","Very very helpful, thank you","Thanks for the effort.","i really apperciate your wonderful explanation","thank you for your research on topic.....respect....!!!!!!","Very informative","Actually , your voice soothes mind","Thank you for your time on the research and explain on this topic. Impressive !","Thanks a lot to You !!","ur way of explaining issues is quiet different. So easy","Extremely good brief explanation","great explaination thank you for your efforts","Wow, it was an amazing explanation","Quite insightful","Thank you very much .. U gav me exactly what i was looking for","thanks fr making me understand so nicely.","These are so informative and clearing out all basic confusions","Hello... I am following all your videos","Thanks you so much for creating my interest on studies","I am so thankful to you for providing such information","I appreciate your method to avail us such information.","you are just wonderful... thank you so much.","Thankyou so much for the great great great explanation","Great job ...really I watched your video so carefully and honestly........ Thank you","Well Done, very informative video with all details. keep it up brother","feeling blessed to see your videos. Love.","Very well explained, made easy to understand,, Thank you so much","This video is awesome and thanks for it.","One of the best content video available for this issue!","Thanks a tone for making such efforts.","Truly liked this","Nicely presented, this lecture made clear understanding !","Every concept explained in a very lucid way.Great great great video","u always make amazing videos","Thank you so much ji","You are a good, knowledged person..... We have been learning from your brain, thank you for the efforts..","This is very interesting knowledge for me..I think all people. Thanks.","Very well explained, thank you","Thanks mate u have great knolwedge sharing skills","U make everything really easy to understand","u have cleared our whole concept regarding the issue thanks a lot for this","ur learning journey fruitful day by day","Excellent explaination and superb sequence selection.","No one can explain with this conviction , thank you","keep the work going","Very informative lecture","Awesome video... searching for such type of knowledgeable video","I really like your video very much","u r great I like so much this video","I am happy that your good knowledge","Very nice video. Very clear and detailed explanation. Thank you for this","The video is really explanatory. Very good work","Incredibly you shared the knowledge and view","Very informative and helpful video. Please keep it up","Could you please provide more of this type video","Very interesting and informative","Very interesting and informative","Your narrative version is imppecable...too good explaination","nice analysis keep it up","Thanks . Well explained","Point to point... thank you so much","This video is so good and easy to understand","Thank you ..... for giving this video","Superrrrrrrb. thanks for making this type of marvelous video.keep it up","Very good lecture,Thanks for sharing knowledge.","I salute your dedication .. great video...","You explain it very coherently thanks.","Your videos are very informative... Thanks","Very informative and neutral view good job","Excellent.Thankyou","Explained very clear ...thank you.","I'm extremely thankful for these amazing videos that u make","Very informative..keep them going","Very informative & explained in a lucid manner.","very detailed explanation for a very complex topic","Fantastic video good knowledge provided by you hats off to you","nice video with full of information and understandable.","One of the best video of study","Thanxs for giving such a nice knowledge.","wonderful explanation...","very nice explanation... doubts cleared","Well explained, most of the topics covered lucidly.","Interestingly ending the topic for peaceful resolution is appreciated.","Very beutifully explained .Hatts off....Great....","Fantastic,nicely explained.","Thanks for best Presentation.","Brilliant job dear","The video was very informative","Very well described . Thanks","Very nice video ....clear understanding of the topic..","Very informative video. Hats off to you.","You are doing a tremendous job.","appreciate your efforts your narrating is best","great source of information.","very good knowledge","thanks for the video, very informative for all of us….","Excellent...cleared all the doubts","amazing course superb way of explaining things Impressive voice","nice love you all members please keep it up ????","very informative","fantastic explaining gestures u have!!!! made me fall for your content!!! bestie for future love to get in touch with ur positivity","really awesome","thank you","Superb","Great!","so...nice","good knowledge","interesting","Thank you so much Ma'am","its very usefull","fine , it is good for gk","Thank you so much mam this is really great explain","Great job! thank you","Good work","It's very useful","it's a fantastic initiative......for learners.","realy it is more useful..","excellent teaching skill and the way is very interesting for understanding ,good job","beautiful presentation. enjoying the new approach to learning. thank you","it's always good to know this things thankyou please continue.","Thanks alot mam.... Unbelievable things I came to know","ur voice...wowwww","Very nice piece of information. Its Amazing !!","interesting .. good teaching...","awesome video, very interesting","wonderfully explained..!","Thanks good info","wow... amazing teaching","quite interesting","Mind blowing.....","interesting...","Gr8 JOB!","perfectly explained . very clear..👍","it's beneficial for us way it taught make good","Wonderful","Very nicely explained... Please keep enriching our knowledge with this daily trivia plan..!!!","cool...","interesting thank for the knowledge","Excellent....","awesome","knowledge is the door of the oppertunity to something get new","wow its really amazing","its so great","excellent!, ur pronunciation and teaching method are so good..... when watching this i really enjoyed.","it is wonderful....","thanks a lot","awesome graphics , awesome presentation.","Information as well as presentation both were superb. Thanks","Just wow..","love the the way u teach","I would like. please continue this course. thanks again.","amazing","Nice lactur","Excellent Explain.","I like the way u learn bcoz it's Very easy to understand nd interesting also thanks keep Guiding","Thank you so much","some point but describe easily all..best way I think it's lajawab..have. a good day..","I started today only. but I am like addicted I kept on going","Your voice made me to love the reading and learning the comoplex concepts in crystal clear .","I hv never commented till date, but must praise ur way of eliminating options n getting answers.... Superb man! N yes ur voice is the best i hv ever heard","What a voice !!!","Amazing explanation.thanks :-)","U r so talented., I just can't believe u know so many facts.. Are u a cimputed or an encyclopedia","Explanation is good","Believe me you are a genius......!!!","love ur explanation n you voice too","lovely, what an explanation.Boring things even become easier in this way","way you explain it's great and your voice so innocent..","Awesome explanation!!!","I like the sound of ur accent","Superb .. no words... Brilliant 😊","Ur voice !! And obviously very good video. Thumbs up to your dedication for helping us","thanks alot , it will really help me","great job","Bdw good explanation though..","What a voice 😍","Got to know how we have to look into a question and element the wrong one's.. thanks you","what are the points one must note or study","it's a great technique","Very informative video","wow ! thanks","great work","thank you so much....","Your way of explaining is too good to leave","Nice","Great, more helpful","really useful","very nice","you really have a nice voice","Outstanding pure worth to watch this video","Good job ...","too good","Nice","Thank you so much please aisi video or banaye","Nice explanation with logic ...","more usefull information","your voice sounds like experiance guy","your voice is too good....","Voice 👌👌","Wonderful explanation...","Ur superb","wow, I need these types of video more.","great analysis...waiting for next videos..thanks","brilliant!!👌","Nice explaination !","awesome video","u hav an amazing voice ....just makes me do study hard .","u explains amazingly amazing........","Nicely explained. ...........","Super teaching","Thank you very much.....","Pleasant voice 👍👍👍","It make lot of sense...","thank you ! please help with other sections also.","This was great , I mean seriously the best !","excellent clarification","Great explanation with clear pronunciation.","good","Awesome buddy","thnx .. keep up the good work","thankyou","Your voice very sweet and english is very perfect wao nice","plz makes more videos on this... Plz..","Thank you very much for a wonderful and clear explanation. Btw your voice is very pleasant. Everyone gets addicted to your voice.","Ur way of explaining things is really good..","pure explanation","Yeh !! Thanks","Great Effort ... Thanku!!!","Plz bring more such types of analysation","Blessed with mesmerizing voice","thanks please upload some more videos of same","Gud job ya","It's easyyyyy","Thank you more update","Nicely explained and Oh My God..the voice..amazing bro.... keep it up...need more videos","Superb I'm speechless","THANK You! So much , helping us with your great idea, Now i understand!! Really helpful!","Shaandaar explanation Thanks","Amazing..... :)","you are a gem... 😊😊","thank you . its really helpful","u r absolutely marvelous....","perfect","Your all videos are outstanding","great explanation....... i learnt how to related different things to reach destinations........... thankyou","this is brilliant keep it coming !","Gr8","One of the Best analysis I have ever seen .. n what a charismatic voice !! Too good","explaning it in less time.. is also beneficial for us thank for it....","gud job..appreciations...","I have seen all your videos. They are amazing. This is something that reached my expectations after a lot of ground work.","Excellent work . Thank you so much. Please do more videos covering all the subjects. Thank you :)","Awesome ...gr8 job ur1 hlping lot of students...","ur nailed it bro",", i wish i would be as knowledgeble as u r. U analysed it very well n ur voice made me to listen it.","Thank you so much for the great explanation and ideas that you are giving us. May God continue to bless you for your good work.","This is free 'therapy' to me... Cheers - keep up","nice explanation... it's very clear","Excellent","I think I have nothing to say about this vid bcoz people have already stolen all the words which I want to say Thanks for the wonderful explanation","Perfect explanations thank you","Grt","thanks for sharing such info as it helps students.","the way you speak... .....Simply awesome","plz u make more video bcz u analysis with all point","you're so smart.","What a voice.. Simply adorable... And very well explained","Nice strategies to solve","Thank you so much for your conspicuous video.. You have such a clarity of thought in handling the questions..","Impresive","nice work r","Ur voice dear so soothing. Thank you for the lesson","I was AMAZED by your Great Explanation and voice","Woahhhh....!!!!","thanks a lot","Muze bahot Pasand Aya video....Mai bhi Kuch banna chahti hu...","I liked the way , how you pronounced","You are very good ...thanks for putting enormous efforts for us","Wow.... I don't have words to explain your excellency ... Thank you so much","Very very very very nyc explanation","you are osssome.","Veryyyyy intelligent ....... plz make more videos like this ...very helpful.","There is something special in your voice... that's very motivating...☺","please make more video for other topics too...","osm approach.....","Very accurate explanations.!! We would like to see more papers solved. Thank you","👍👍👍👍 knowelegeble","thanks","Dhnyawad 🙏","Excellent","Ghazab explanation.!","Very good explanation ..... Plz gve ur conct Nmbr","Good job","wonderful.......Thanks",", please upload other topics analysis","I m in love wd ur the way of communication","Very nicely explained ..Thank you","Soooooooooo gud....😘😍","Gud explanation.. Thank a lot","your analysis is very much useful..actually, is paving path ...awesome","what a voice....","expecting more videos from you ,thank u","Very Thankful to you , nice explanation to each and every question.......,......","Hi and thankss for uploading this video. Although I would request you to upload more video","thanks a lot !! thump up !!","Thanks a lot g....","Thank you this information..","fan ban gaya, thnq","awesome ji thank you so much","Very useful for future","mujhe to bhut help mili thnks wonderfull aise hi lecture provide kijiye","Please make for other topics also","Make similar video for other topics also","well explained bro","Thank you Guruji🙏🙏","Nice vdo","thankyou for guidance","Good explanation keep rocking","thanks a lot for making ma'am","Thank you so much for this contribution and for your precious time.","thanx a lot","thanks so much","NICE","👍😊 You're the best","Helpful","Mam you are just amazing","thank you very much! please do not stop making this in the mid way, try to continue","Very marvelous deed","I hope this course doesn't end abruptly....","It's going to be a great approach .","pls continue it for a life long","thank you plzzzzz continue🙏","The great initiative","that's amazing :-)","good one","not bad...","awsum","thank u so much ..","mind blowing","i honestly watched it out of plain curiosity.. loved it.. thankyou","I loved that and its beautiful","Wah, my favourite dish, thanx ","Exciting to see u","you are a reason to smile","God bless.","I am a big fan of your ","Lots of love and respect","how amazing you are","Thank you, thank you soooooooooo much.","impressive","Seems really good, and technical knowledge","it was made with so much love","genuinely so good ","Very crystal clear video good presentation thank you for sharing thank you so much...","Everyone want one simple thing.","Video is very informative","best ever ..","Thankyou verymuch indeed it will help us ! ","This one is informative ! Thanks a lot ","Too good information ! Thank you.","Thank you so much for your information","Thanks so much ","Thank you so much saw your videos","thanks for your all type work information ","Thank u so much  for your good infromation","Veryy good","Very Needful and Helpful topic. Thank you ","Nice video. Was really helpful. Thank you so much","Many thanks for this video","Thanka for sharing","Nyc information","Tqs for sharing information","Tysm... very useful...","Good information","Thanku for information","Thank you....very informative....keep up the good work","Very helpful ","your are great","Super spech","really you are very honest nd great person","for helping always","Great s u r very helpful","But nice video","thank you very much","Thank u.. it's working","So beautiful video………. I like you","This commens for thank you","Wow nice","Nice information 🤝👍 like ","that's a great ","super information 👌👍","Thanks again","you are great","very Good work","Thanks। Best। Information।","Nice information  👌👌👌👌👍","I will b thankful to u","So beautiful video","every video is very useful","Super Job","Nce great video","we all love you.","Thanks for your information","Nice video","Wow great","Very useful info…………","Keep working Amazing Video","founded interesting 2me.","Good video","Nice work","Wow I love this.","very very nice","It turned out awesome","Awsm","Super","Gjk","Nbccha","Wow so tasty and yummy","Hey! this is such good video, definitely jhakaas","Kaafi Rochak Sahi hai","Arre waah Sabse Nice !","Hey dude aapke sabhi Faadu posts hain.","Pyara video hai buddy! Mujhe bhi try karna hai","Looks elegant and gorgeous dude.","Aapke sabhi content Ati Super hai.","Oo teri! Sahi ! Cute videos !","inconceivablee","good, bsT","trul awsme","adVantage","Aap Sahi kaam karte ho! Sahi content!z","Sahi style","Hey yaar Jhakaas video","inspiRatiOnal","onsiderate, big-hearrted","ye vlog Sabse Beautiful hai.","forridablE","Ye aapka Ati Mast vlog hai.","Great background, good background music, so simple","perfect","Eagerly waaaiiitig for the next poSt in the seies! ❤❤️","your video is so delightful, undoubtedly jhakaas","Waah kya Good post banaya hai.","sympathetic, kiind","heeDful","Kaafi Faadu content banate hain aap","Know-It-AlL","Looks appealing and splendid dost.","lesssser, ancillarryy","Extra elegant dude.","pragmatiica","stellar","Bahut Madadgar Badhiya hai","dude Aapke sabhi posts Ati Badhiya hai.","Shabaash! Zordar ! मस्त vlogs !","softhearrred","Yo! wow! this is so interesting","That face tHou.","cosiderate, keen","Hey! loved your music, definitely awesome","aiabllE","Great Trail! 👌👌👌👌","deligh,, riish","Shaandar content hai dude! Maa kasam!","benefial","superb, excelllet","Hey! this is such awesome style, unquestionably jhakaas","fantastIc wrk","Sahi style , Main ise zaroor try karunga yaar","rarre","Outstandingly classic friend.","Wow! 😍","Hey! truly entertaining framing, superb!","astounds","uiilityy","esstImmable","greatharted","dlightful","Aapke videos mujhe bohot Khoobsoorat lagte hain! Pyare!","friEndly","bannnner","kInd, ociiiable","remedial","Great presentation, good video filter, so excellent","mythos","Yo! bravo! yaar this is so delightful","wonderooous","roousng","outstanding","ssplEnndifooous","oooperatie","superb, remaarkbe","SSSmarty--Pants","Kaafi Taaza Khoobsoorat hai dude","enormoous","Hey! liked your work, truly beautiful","Extra engaging vlog dude.","Shaandar video hai dude! Mujhe bhi try karna hai","would beEnefit","your video is so interesting, truly delightful","Looks pyara and gorgeous.","Hey! truly excellent script, bravo!","Arre waah! Sundar ! Dhansu content !","Good post , Aap se hamesha naya seekhne milta hai","just teerrrifi","Hey! this is such amazing style, surely good","Arre waah dude Sabse बहुत सुन्दर","yaar ye vlog Kaafi Sahi hai.","Hey yaar Kadak video","Thrrapeutic","Aap Badhiya kaam karte ho Dost! Badhiya post!","excellent and excellent way of preparing food!!","Looks excellent! Thanks for this meal!!","Hii this is Unique way of trying out new Dish! OMG","Thanks a ton From when did I start finding preparing dish so brilliant .","Yo people!! excellent vlog!","The Vlog is Mostly cool and Excellent!","Simple way of Baking Vlog","dear!! I'm definitely going to try this amazing meal today","Killing it!!! It is certainly easy .","Heya this is awesome!!! Thanks for sharing this","Hey there Great dish! Mindblowing!!","folks!! I'm definitely going to try this yummy recipe today.","Looks delicious! Thanks for this.","I am really impressed by this vlog!! Mindblowing .","Hii , This is honestly unique , Out of this world!","This video is really yummy , Killing it","cool one there! Eagerly waiting for your next dish .","Heya! This looks so quick! Thanks for this meal","Yo!!! I'll be making this dish today","Hey guys Great post!!! Commendable!!","Heyy!!! I'm soo excited to prepare this video!","Yo! I am looking forward to such more easy post!!","Heya! This looks so amazing! Thanks for this vlog!!","I am absolutely impressed by this post!! Keep it going!!","Heya there , Can you please upload more such delicious trail","Hii this is so tasty!!! More video please","This post is honestly delicious , Out of this world","Thanks for sharing this! It is honestly quick!!","awesome and awesome way of cooking food!!","there!!! I'm definitely going to try this delicious video today","cool one guys! Eagerly waiting for your next vlog!","Hey!! I am looking forward to such more delicious video","Hii guys!! unique post","Heyy , This is really awesome , You are a genius!!","Are all the ingredients easy to find?","Hello this is quick!! Thank You!","Hey!! I'm soo excited to prepare this post .","Thank You From when did I start finding preparing video so unique","Yo people Great post!!! Commendable .","Hi!!! This looks so delicious!!! Thanks for this vlog","Killing it! It is honestly amazing!!","Heyy people!!! easy dish","Yo folks Great dish , Mindblowing!","Hii I'm going to try this unique meal today!","This is certainly the best trail I saw today!!! Thanks for sharing this!","Heyy this is so amazing!! More trail please!!","Oooh!! You are delightful when it comes to preparing food","Hi guys! Can you please upload more such awesome trail!!","This trail is quick , I can't compliment you enough!","I'm definitely going to try this simple recipe today!","folks!!! I'm definitely going to try this simple meal today","Hi , This is honestly awesome , Thank You!!","sssurprise, sttttrge","woondroousl","terrrifying","glamorous","hepffulness","Yo this is delicious! Keep it going!","excellent one dear , Eagerly waiting for your next video .","Pyara post , Mazaa aa gya! dude","buddy Aapke sabhi posts Bahut Sundar hai.","Waah! Pyare ! Todu posts !","herisSh","Fun. So informative.","skilllful","fronTline","granD","dude! your video is so jhakaas, unquestionably shandaar","Hey dear Khoobsoorat video","Extra educational vlog dude.","tenderhearted","insttrRrummmntal","righthhAndd","Aspiirrre","Beuteous","cooerattivee","healthy","Hii people!! This is absolutely marvelous!!","superb!!! incredible!!! Let's not forget your style is incredible .","informative trail!!! appreciate the way you captured it!!! Sharing with my friends","awesome text! This is so amazing! Pleasing to my eyes!","Hii! This is the most informative place that I have ever seen!;)!!","kudos, I admire your style and travel stories! certainly. awesome!","Heyy!!! I love your post!!! It is so unique and marvelous to watch!","Yo!! I love this text so much!! I want to get to this location right away","amazing! Please make more vlogs! They're really provide a lot of insight.","superb!! It's really beautiful!! You are a genius!!","helpful Videography! love the way you captured it! Sharing with my friends!","superb!! This is the best way to enjoy life!! you are certainly cool in so many ways","Treller You are the cool travel style creator","Hi!!! Your text is so elegant!!! Could you please give more details about the cost of the trip!!","Hi This location is so incredible!!","Ohh! I appreciate your style and travel stories! truly elegant","Hey You are the most brilliant travel trail creator","Hi!!! I love this trail so much!!! This is mindblowing","Ohh!!! It's really elegant!!! I want to get to this location right away .","Oooh people!!! I want to get to this location right away!","Heyy!! Your trail is so awesome!! Could you please give more details about the cost of the trip!","Ohh , awesome , Let's not forget your style is awesome!!","people!!! This is mindblowing!!! How did you find this incredible place?","Nice , This is the best way to enjoy life, you are truly awesome in so many ways","Nice! Everything makes this destination so amazing","Treller You are the brilliant travel Ideas creator","beautiful trail!! This is so amazing","Hii!! I love your blog!! It is so unique and awesome to watch!","cool post , This is so amazing, You are a genius ","Hi people!! This is really informative!!","bravo, I admire your style and travel stories! honestly helpful!","beautiful post! This is so amazing! This is mindblowing!","Superb!! It's really elegant!! You are a genius!","Yaay! I like your style and travel stories! undoubtedly informative!","Wow!!! This is the best way to enjoy life!!! you are undoubtedly awesome in so many ways!","Yo people!! marvelous trail!! This is so amazing!","Ohh!! I want to get to this location right away!!","wow, I Salute your style and travel stories! honestly cool!","Hey!! I love your post!! It is so unique and cool to watch!","bravo!!! awesome!!! Let's not forget your style is awesome","Hii! I love this blog so much! You are a genius","Hello people! This is absolutely beautiful!","wow.. It's really brilliant... ;)","incredible trail! This is so amazing! You are a genius","Oooh! informative! Let's not forget your style is informative","bravo , It's really informative , Pleasing to my eyes .","Amazing people!!! Pleasing to my eyes .","Yo people!!! This is undoubtedly incredible!!!","Awww.. It's really good... ;)","Yaay , It's really awesome , Pleasing to my eyes .","Heyy people!! This is definitely amazing!!","amazing blog! This is so amazing! You are a genius .","Wow! time to apply for leave ;)!!","Hii people!! incredible post!! This is so amazing","Yo , I love your text , It is so unique and amazing to watch!","OMG! Pleasing to my eyes!","Superb , Marvelous , Let's not forget your style is Marvelous","Hi You are the most Marvelous travel trail creator!","Super people!! Pleasing to my eyes .","Ohh , It's really elegant , ;)!!","Superb , informative , Let's not forget your style is informative!","Hi! I love your blog! It is so unique and awesome to watch!","Yaay, I love your style and travel stories! really amazing!","marvelous post , This is so amazing, This is mindblowing!","awesome blog!!! This is so amazing!!! ) .","Gjb","Hii","Nice","Hiu","Pain killer eyes","Whooo","Very nice","Hlo","Super duper","awesome vlog dear!! finding for many as such","Thanks a ton , wanting for more trails from you","Hey! congrats!","Hey! loved your editing, undoubtedly jhakaas","Extra handy video frame dost","honestly excellent post guys , Out of this world!","Heyyy! bravo! buddy this is so amazing","iiformal, eligHt","dear!! Keep it going!! Best vlog on this issue so far","This is helpful work dude.","Hey! this is such good vlog, definitely shandaar","love it!! Thanks!!","Great concept, so helpful","I really adore your posts dear , Out of this world","Hey! loved your video, positively useful","Hello simple video guys!!! Keep it up!!","Looks incredible and badhiya friend.","Hii , wanting for more posts from you,","Nice , quick , dear!","Hey! absolutely beautiful work, wow!","Looks appealing and pyara yaar.","Extra cool edit style friend.","Hi! congrats! dude this is so detailed","Great edits, so engaging","Hey! this is such good vlog, certainly shandaar","Highly delightful presentation style friend.","Great concept, good vlog duration, so gorgeous","Heyyy! bravo! buddy this is so engaging","Hey! positively gorgeous style, waah!","Looks interesting and handy yaar.","Hey! enjoyed your video, unquestionably beautiful","dude! your video is so beautiful, unquestionably detailed","Hugely engaging dost.","Hey! this is such good, surely jhakaas","Great edit style, good vlog, so fresh","incredible dude.","Extra acha video frame dude.","Looks engaging and amazing dost.","dude! your video is so gorgeous, unquestionably jhakaas","Extra shandaar edits dude.","Hey! liked your style, unquestionably delightful","Great presentation style, good vlog editing, so instructional","Hey! this is such good vlog, truly awesome","dude! your work is so splendid, surely good","That's splendid and interesting dost.","Hiya! waah! dude this is so fresh","Hey! loved your vlog, honestly detailed","Hey! really interesting delivery, superb!","Looks educational and constructive yaar.","Outstandingly cool friend.","dude! your work is so interesting, certainly jhakaas","Hiya! wow! buddy this is so beautiful","Hey! this is such cool vlog, undoubtedly splendid","Incredible edit friend.","Hugely helpful title friend.","dude! your video is so sahi, unquestionably cool","Truly beneficial yaar.","Hey! this is such good framing, really badhiya","Looks educational and minimal dude.","Hey! loved your style, absolutely elegant","Great concept, good vlog filter, so incredible","Delightful video yaar.","Hey! loved your editing, certainly shandaar","Hey! this is such awesome content, definitely excellent","So bhadiya and interesting dude.","Great concept, good vlog duration, so incredible","Hi! waah! dear this is so shandaar","dude! your video is so brilliant, unquestionably awesome","Hey! really cool content, waah!","Hiya! wow! yaar this is so detailed","Hey! loved your video, surely entertaining","Hey! this is such beautiful script, surely delightful","Hugely incredible notification friend.","ude! your video is so good, positively amazing","Looks engaging and simple dost.","Elegant vlog style friend.","Hey! absolutely good, congrats!","Hey! liked your content, undoubtedly cool","Hey! this is such awesome video, truly detailed","Highly amazing friend.","dude! your video is so cool, surely awesome","This is detailed and delightful dost.","Outstandingly thought out! It makes me do this...","Hey! liked your work, honestly detailed","Hey! this is such awesome delivery, certainly engaging","Vastly shandaar friend.","Looks fun and simple dude.","dude! your video is so useful, absolutely good","Hey! really helpful framing, waah!","Hey! loved your content, unquestionably beautiful","Extra classic style yaar.","Looks instructional and splendid dost.","Immensely handy yaar.","Hey! this is such beautiful framing, really smart","dude! your video is so amazing, really cool","Great edits, good blur, so simple","Hey! dude this is so detailed you are so entertaining","Hey! absolutely gorgeous script, waah!","Great editing, good vlog, so detailed","Heyyy! superb! yaar this is so detailed","Hey! this is such good vlog, really cool","Hey! adore your script, absolutely amazing","Hey! really entertaining script, bravo!","Hugely simple presentation yaar.","Looks detailed and excellent friend.","dude! your video is so engaging, really splendid","Great edit style, good title, so simple","Highly appealing friend.","Extra shandaar presentation dost.","Hey! this is such awesome vlog, unquestionably detailed","Hey! loved your work, really delightful","Hey! really brilliant script, waah!","Looks constructive and amazing friend.","dude! your video is so engaging, undoubtedly awesome","Hi! waah! buddy this is so brilliant","Hey! this is such awesome vlog, honestly jhakaas","Extra amazing ","Looks excellent and educational dude.","Great background, good title, so engaging","super cool!!!!","Truly bhadiya.","Hey!this is so awesome you are so detailed","Hey! loved your video, truly badhiya","your video is so cool, certainly splendid","Superb!! brilliant folks Keep it going!","Superb , brilliant , people!!","really excellent!! Looking forward to more such excellent trails","Yaay!! brilliant people","folks really beautiful Trail, Thanks!","OMG!! unique!! guys","Heya!! Damn engaging vlog .","I honestly like your videos dear!! Keep it going .","Hello!! Damn brilliant vlog!!","mad trail dear! Out of this world","like this trail! brilliant one people! Thank You!!","Keep it going!","I really like how you create post!!","Heyy people! What made you create a vlog on this issue?","Hello brilliant video folks!!! Mindblowing!!","wanting for more posts from you!! Thanks a ton!","people love it!!! Mindblowing","finding for more posts from you, Thanks","Thanks a ton!","like this video! unique one there! Keep it up!","Hello!! Damn beautiful vlog!!","Amazing!!! beautiful guys ","Hello!! Damn delightful vlog!!","Yo dear , What made you create a vlog on this issue?","Superb , simple","The most quick post so far, Killing it .","Super!! cool people Thanks a ton!!","I honestly like your posts dear! Thank You!!","folks absolutely unique Trail, Thanks a ton!","Heya!! Damn engaging vlog!!","people like it!!! Thank You!!","Hii excellent trail people!!! Out of this world .","unique trail folks!!! Killing it .","Yaay!! cool!! guys!","Heyy! Damn amazing video!!","wanting for more trails from you! Thanks a ton .","love this vlog , amazing one guys , Mindblowing .","people absolutely brilliant Trail, Mindblowing","Superb!!! incredible people","The most quick post so far, Out of this world .","honestly mad!! Looking forward to more such mad trails","Yaay!!! quick there","Hello! Damn unique vlog!","Nice! unique folks Keep it going","Thank You","I absolutely like your posts folks!!! Keep it going","Amazing!!! unique dear Out of this world!","Oooh , engaging , folks .","The most incredible vlog so far!! Keep it up","Hello , finding for more videos from you,","Wow!!! mad dear","finding for more vlogs from you!!! Commendable .","Hello!! Damn brilliant video!!","I certainly like your posts there! Commendable","Ohh! amazing people Killing it","Heyy beautiful post dear! Thanks a ton!","waiting for more posts from you! Mindblowing!","certainly engaging!! Looking forward to more such engaging trails","Nice , beautiful , guys!!","guys honestly quick Trail! Killing it .","Hi! Damn simple trail!","The most cool post so far!!! Thanks","Hi!!! Damn cool video","adore this, simple one dear , Killing it .","like this post , incredible one folks , Commendable!!","cool trail guys!! Thank You!!","unique trail folks!!! Mindblowing!!","Hi , wanting for more from you,","Yaay! engaging people!","Hey , Damn delightful,","folks honestly engaging !!! Out of this world!!","Yo unique video guys , Mindblowing","I really adore your posts folks! Mindblowing .","Yaay!! delightful!! there .","brilliant trail folks!!! Thanks a ton!","The most delightful post so far!! Thank You!","Hello excellent vlog there , Keep it up!!","there really simple Trail, Thanks a ton!!","Heya!! Damn entertaining!!","Yaay! simple dear!","Yaay!!! unique guys Commendable!","brilliant trail folks , Keep it up","like this post , excellent one there , Out of this world!!","there!! Keep it up!","Heyy!!! Damn entertaining vlog","certainly engaging!! Looking forward to more such engaging","there like it!! Thanks a ton!!","The most simple vlog so far! Thank You .","Wow , beautiful folks Killing it .","people love it!!! Keep it up .","Hello!! looking for more from you!!","I honestly adore your videos dear , Thanks a ton!","there really unique!! Keep it going!","Hello!!! Damn amazing vlog!!","Amazing! quick folks Thanks","Hey!!! Damn awesome vlog .","Hii , vlog ,","Mindblowing!","Yaay , quick dear Commendable .","OMG! excellent","adore this video , excellent one guys , Out of this world!","Yaay!!! beautiful guys!!","incredible  people! Keep it up!","beautiful  there!!! Keep it up!!","there really brilliant! Commendable!!","Hii! waiting for more videos from you!","Ohh!! beautiful!! guys!","like this post!!! engaging one folks!!! Thanks a ton","Hello awesome vlog people!! Out of this world","Amazing , engaging folks .","The most awesome so far!! Keep it going","honestly unique , Looking forward to more such unique","Wow , cool there Thanks","Killing it .","there really simple","Yo people!! What made you create a vlog on this issue?","The most excellent video so far, Out of this world","Hey brilliant post folks!!! Thanks a ton .","I certainly adore","Hello , Damn unique video!!","Hi! Damn simple post!","The most delightful video so far!! Thank You!","love it! Keep it up","Thanks a ton","people certainly awesome","I really love your vlogs folks! Thanks a ton .","Heya!! Damn beautiful video!!","good feeing, advantaagee","helpmate","aaziing, astounninnng","heavenlyyY","Elegant concept dost.","So pyara and strong dost.","Hii! superb! yaar this is so amazing","dude! your video is so beautiful, positively shandaar","Hey! this is such cool framing, certainly badhiya","Hey! loved your video, absolutely useful","Extra badhiya dost.","Great background, good vlog, so appealing","Hey! honestly shandaar content, superb!","Hey! this is such good content, truly engaging","Hiya! wow! dear this is so badhiya","dude! your video is so sahi, absolutely smart","Looks gorgeous and engaging friend.","Highly acha presentation friend.","honestly helpful","Extra interesting dude.","absolutely incredible","so instructional","Hugely excellent dost.","Hey! loved your work, unquestionably informative","dude! your work is so fun, definitely beautiful","Hey! wow! dude this is so jhakaas","Hey! truly pyara content, waah!","Yo! kudos! dear this is so gorgeous","dude! your video is so shandaar, undoubtedly beautiful","Looks interesting and fun dost.","Hey! this is such beautiful","Great concept, good video, so helpful","Hey! adore your video, honestly awesome","Looks amazing and educational yaar.","good vlog","Hey! really beautiful style, superb!","dude! your video is so interesting, definitely cool","Hey! this is such good content, truly fun","cool","Hiya! wow! buddy this is so fun","Extra appealing yaar.","Hey! really pyara framing, bravo!","Hiya! superb! buddy this is so fresh","Hey! liked your script, absolutely beautiful","Immensely pyara dude.","certainly gorgeous","Looks fresh and appealing dost.","Extra bhadiya presentation style dost.","dude! your work is so awesome, certainly gorgeous","Incredibly thought out! Please stop!","Great , good vlog topic, so amazing","Hey! this is such cool style, really incredible","Great , good editing, so graceful","Highly shandaar presentation dost.","Hey! truly entertaining video, kudos!","Cool video yaar.","Hii! congrats! dude this is so detailed","Hey! loved your delivery, surely excellent","Useful. So strong.","Looks instructional and fresh friend.","dude! your video is so sahi, honestly beautiful","Hey! loved your vlog, certainly fresh","Hey! this is such good framing, unquestionably engaging","dude! your video is so good, undoubtedly jhakaas","So beneficial and informative friend.","Hi! dude this is so elegant you are so good","Great , good video, so badhiya","Hey! honestly shandaar video, waah!","dude! your video is so sahi, positively incredible","Extra delightful concept dost.","handy","Yo! kudos! dear this is so good","So elegant and beneficial dude.","Hey! loved your music, definitely fun","Really cool yaar.","Hey! this is such good music, surely entertaining","Hey! absolutely cool video, bravo!","Constructive topic dude.","Truly constructive friend.","Hugely delightful vlog dude.","Amazing video frame friend.","Hey! superb! buddy this is so elegant","Heyyy! loved your script, certainly incredible","Looks badhiya and bhadiya dude.","Great style, good vlog presentation, so classic","Delightful. So instructional.","Hey! this is such jhakaas content, undoubtedly beautiful","dude! your video is so helpful, definitely splendid","Hey! certainly good style, superb!","Truly thought out! I think maa would love this.","honestly shandaar","kudos!","Great edit style, good style, so helpful","Instructional presentation dost.","Hey! loved your content, really delightful","Hii! bravo! dear this is so fun","dude! your video is so jhakaas, undoubtedly delightful","Hugely interesting vlog style dost.","Looks educational and useful dude.","Extra fun vlog dost.","dude! your video is so entertaining, unquestionably gorgeous","So amazing and instructional dost.","Hey! liked your work, really gorgeous","Amazing. So delightful.","Hey! really cool delivery, kudos!","Yoo! wow! buddy this is so awesome","positively amazing","Great notification, good blur, so engaging","Great concept, good vlog topic, so handy","So fresh and helpful dude.","Interesting! 😃","So nice","Wow","Super","ZHii","Nniiiiii.","I like it","So nice","I wish I ccould like Thhis twice","qualitty","Good vlog hai yaar!","Fantastiic 🙌","yaar Aapke sabhi content Ati Zordar hai.","forrrthcominGg","Sundar style , Aap se hamesha naya seekhne milta hai","teriying","Dost! Nice content hain aapke!","your video is so interesting, certainly awesome","Hey! this is such jhakaas vlog, certainly excellent","crcking","So fresh and engaging friend.","convenient way","Hey! dude this is so entertaining you are so fun","Hugely cool presentation yaar.","Hey! definitely badhiya content, congrats!","larger-thaan-lllife","Great editing, good vlog presentation, so educational","Vastly thought out! You are so inspiring!","Hey! liked your framing, truly jhakaas","Baap re! Zordar ! Bhokaal content !","surpise","outstandinG","ACcomplishhhment","Inccredddbbble 😍🙌","rally nice","Hl Yeah","awesomnS, gretess","necessary","Aap Shaandar kaam karte ho buddy! Shaandar video!","Sundar style hai","enthrallinggg","Aapke content mujhe bohot Perfect lagte hain! Khoobsoorat!","Kaafi मस्त Badhiya hai","Really bhadiya friend.","Hii yaar Jhakaas vlog","ye post Ati Khoobsoorat hai.","Dhansu video , Aap aise videos kaise banate ho","helpful prson","Kaafi Madadgar Sundar hai","genius","Aap Sahi kaam karte ho! Sahi video!","gooood, quality","Zabardast video hai! Ise share karna toh banta hai","good feLing","kinddd,, ttimely","Heyyy! this is so jhakaas you are so engaging","Hey! certainly entertaining editing, superb!","ye content Kaafi Faadu hai.","Easilly please","Hey! adore your, honestly cool","That's elegant and bhadiya dude.","Shabaash! Zordar ! Zabardast videos !","Yo Dost aapke sabhi Dhaansu content hain.","Fanasticcc thinG","very nicee","your video is so brilliant, really good","Shabaash Kaafi Good","great in here","Aapke content mujhe bohot Shaandar lagte hain! Sundar!","Hii Dost Sahi post","Hey! this is such cool work, unquestionably gorgeous","beattutiffful ","Extra engaging topic dude.","wonderu yeeear","advantage, good","besTtt exceptionl","Hi there!!! This is really the best meal that I've seen today!","Hey guys!! like this food post!!","Super! This food looks so tasty .","This food is absolutely excellent!!! adore it.","excellent vlog!! Nice one","Super! You are amazing when it comes to this folks","Looks cool! Thanks for this video!","You are brilliant when it comes to this!","excellent meal as usual!!! Mindblowing","Never stop doing what you're doing! You're cool! Thank You .","Hii! This is absolutely the best food trail I've seen!","delightful vlog!!! Commendable folks!!","Heya!! Love this","You should undoubtedly make more videos like this video , They're excellent .","Thanks!!","Yaay! You are unique when it comes to this guys!!","Heyy people! You are incredible when it comes to this","awesome! love it.","You should honestly make more videos like this post!! They're cool!","Oooh!! You are cool when it comes to this there!","I adore this so much.","engaging post! Thanks a ton people .","adore it!","Hey guys , You are unique when it comes to this!","I like this so much!","certainly excellent","adore it!!","Heya guys , adore this ","Commendable!!","Never stop doing what you're doing, You're amazing , Keep it going!!","that I've seen today! Wow","Yo people!!","You're engaging .","incredible vlog , Keep it going dear!!","honestly excellent","Superb!!! ","I cant wait to try this certainly","Thanks for sharing this!!","amazing .","This food is certainly awesome! adore it!","Keep it going there!","it comes to this dear .","unquestionably delicious","You're brilliant","I like this so much","Thanks a ton .","You're excellent!!","Never stop doing what you're doing!","Hii there!! You are brilliant when it comes to this","I've seen today! OMG","Hi!!! cool","Amazing!! You are unique when it comes to this guys!!","You're unique","that I've seen today.","ou're amazing!! Killing it .","delightful vlog! You are a genius dear","You should really make more videos like this trail , They're unique .","Mindblowing .","engaging way","Never stop doing what you're doing!!! You're amazing!!! Commendable","Amazing!! You are engaging when it comes to this there!","unique vlog! Keep it going dear!!","that I've seen today!! Superb!!","You're brilliant!!","that I've seen today!! Awesome","Hi!! amazing video","awesome! Thanks a ton!","such cool","excellent!!! love it","Looks cool , Thanks a ton!!","You're awesome!! Mindblowing!!","amazing way of trying!!! Keep it going","Oooh! You are awesome ","awesome!!! adore it!!","Nice!! Thanks for sharing this!!","Hii!!! awesome vlog .","Super! I","I adore this so much","You are excellent","awesome vlog! Out of this world dear","awesome , love it.","incredible post , You are a genius dear!","Nice one!!","Looks cool!!! Thanks for sharing this","Yo dear! You are awesome","delicious","excellent way of trying! Thanks a ton!!","adore this food post , You're unique!!","beaTutiFul","This is so coo! 😍😍","gooood, healthyyy","ACccomplissh","aleert,, careful","oved it ❤️️","brillliant","Looks constructive and simple yaar.","Hey! dude this is so fun you are so beautiful","This is useful work friend.","Great edit, good style, so instructional","Hey! really gorgeous delivery, waah!","Fun. So useful.","Hey! liked your video, undoubtedly elegant","Graceful style dude.","Looks constructive and instructional yaar.","interesting","Hey! truly delightful music, superb!","dude! your video is so delightful, undoubtedly badhiya","Hey! this is such good vlog, absolutely entertaining","Heyyy! wow! dude this is so pyara","so cool","Great video, good vlog duration, so strong","dude! your video is so pyara, undoubtedly good","Hugely fresh vlog dude.","Looks helpful and minimal dost.","Hugely excellent yaar.","Hey! adore your video, certainly good","Hey! this is such cool framing, honestly incredible","Hey! this is such awesome video, truly good","Highly fun title dude.","dude! your work is so fresh, positively entertaining","truly excellent","Looks incredible and elegant dude.","Hi! superb! dear this is so sahi","Hey! loved your delivery, definitely incredible","Incredibly thought out! Wow love it!","Hey! this is such good work, absolutely brilliant","Hey! honestly incredible vlog, kudos!","Hiya! congrats! dude this is so engaging","Immensely incredible vlog style dude.","bravo!","Hey! really entertaining script, congrats!","Hi! bravo! yaar this is so informative","Looks detailed and acha friend.","so useful","Great vlog style, good vlog topic, so beneficial","Hugely elegant friend.","dude! your vlog is so excellent, positively engaging","Acha background dude.","So badhiya and delightful dost.","Looks appealing and incredible friend.","Hey! loved your delivery, truly jhakaas","dude! your vlog is so cool, definitely engaging","so graceful","Bhadiya. So classic.","Hey! really fun framing, superb!","Hey! this is such cool","undoubtedly splendid","Hey! this is such good editing, truly splendid","Immensely educational notification dude.","Hey! adore your music, undoubtedly helpful","Hey! loved your delivery, undoubtedly amazing","Cool. So engaging.","Hey! truly engaging content, congrats!","Hugely simple friend.","Heyyy! bravo! buddy this is so interesting","Extra incredible video frame yaar.","dude! your work is so fun, surely entertaining","Heyyy! superb! yaar this is so fresh","Looks engaging and badhiya dude.","dude! your video is so helpful, definitely delightful","Extra excellent presentation yaar.","Hey! buddy this is so detailed you are so smart","Great concept, good video filter, so excellent","Instructional. So minimal.","Tremendously educational dude.","Hey! enjoyed your content, certainly shandaar","Hey! this is such good content, really splendid","Immensely bhadiya vlog dude.","Hey! really fresh script, superb!","Graceful title yaar.","Outstandingly appealing dost.","Hey! absolutely delightful content, superb!","Hey! loved your vlog, surely engaging","Great background, good vlog, so instructional","So shandaar and pyara dost.","Hey! dear this is so engaging you are so brilliant","Hey! this is such cool style, unquestionably engaging","Incredibly acha edits dost.","dude! your work is so shandaar, really fun","Great background, good vlog filter, so splendid","Watched your vlog. It's bhadiya dude.","Looks handy and bhadiya friend.","dude! your video is so interesting, really incredible","Hey! this is such cool script, honestly splendid","Looks interesting and beneficial","Hey! this is such cool vlog, surely amazing","this is such awesome work, undoubtedly fun","liked your vlog, truly brilliant","Heyyy! congrats! yaar this is so helpful","Looks appealing and amazing dude.","Great edit, good vlog pattern, so beneficial","Yo! congrats! dude this is so engaging","Classic. So graceful.","Hey! definitely incredible editing, bravo!","Hey! liked your work, truly awesome","Great presentation, good vlog title, so fresh","Outstandingly interesting dost.","Classic notification friend.","Detailed experience yaar","This experience is now in my wishlist.","waah!","Hey! really engaging ","dude! your work is so cool, definitely excellent","dude! your video is so incredible, absolutely cool","Background music. How do you do it?","Hey! loved your script, absolutely jhakaas","Hugely bhadiya editing dost.","presentation, so incredible","This is gorgeous and acha dude.","Gorgeous style yaar.","Hey! this is such awesome work, really brilliant","Heyyy! dear this is so helpful you are so brilliant","dude! your video is so awesome, truly jhakaas","Hey! this is such jhakaas editing, unquestionably incredible","Hi! wow! yaar this is so awesome","Hey! honestly incredible style, superb!","Hey! truly incredible framing, bravo!","dude! your work is so helpful, positively delightful","So fresh and amazing yaar.","Hey! liked your script, absolutely amazing","Immensely beneficial notification friend.","Outstandingly incredible presentation style yaar.","Great presentation style, good blur, so incredible","Hii! superb! dude this is so awesome","Great background, good background music, so engaging","dude! your video is so delightful, absolutely detailed","Looks minimal and incredible yaar.","Hey! really engaging delivery, waah!","Extra informative topic dost.","Hey! liked your vlog, undoubtedly incredible","Great , good vlog style, so helpful","Hey! this is such awesome music, surely amazing","Hey! dude this is so beautiful you are so brilliant","Hey! really engaging editing, congrats!","liked your script, absolutely splendid","Very excellent","Extra pyara presentation style","Acha. So badhiya.","Great concept, good vlog duration, so gorgeous","dude! your video is so awesome, undoubtedly gorgeous","Hey! this is such awesome vlog, really cool","Looks elegant and minimal","Interesting title","Fun edit style ","dude! your work is so jhakaas, unquestionably fun","Great title, good vlog title, so educational","Hey! absolutely elegant style, superb!","These are cool and pyara","Hey! buddy this is so sahi you are so beautiful","Extra detailed","Hey! this is such good video, certainly brilliant","Incredibly useful ","Hey! adore your editing, certainly jhakaas","Informative. So useful.","Gorgeous topic","Hey! certainly detailed framing, bravo!","Looks amazing and useful ","Great concept, good style, so helpful","Hey! loved your video, definitely pyara","dude! your video is so incredible, unquestionably good","Hey! this is such cool video, certainly entertaining","Heyyy! bravo! dude this is so elegant","Extra splendid experience","Extra helpful vlog","Hey! this is such good style, definitely beautiful","dude! your video is so elegant, unquestionably splendid","buddy Aapke sabhi vlogs Ek dum Mast hai.","Extra appealing","dear ye video Sabse Madadgar hai.","Cool style hai! Aap se hamesha naya seekhne milta hai","Aapke videos mujhe bohot Zordar lagte hain! Sundar dear!","Hey! this is such good editing, definitely shandaar","your video is so shandaar, truly amazing","Aap Sahi kaam karte ho Dost! Sahi vlog!","Looks gorgeous and simple dude.","Heyyy! waah! yaar this is so useful","Jhakaas vlog , Mujhe bhi try karna hai","Hey! really brilliant music, kudos!","dude ye video Ek dum Zabardast hai.","Hii next post kab aaega?","Zordar post hai dude! Yeh mere bahut kaam aaega","Aapke vlogs mujhe bohot Kadak lagte hain","Hey! yaar this is so elegant","wok of geeeniius","Aapke sabhi vlogs Sabse Todu hai.","You rreaaLllly look gorGeous in ttthis one","Extra badhiya notification","gud..❤️ 👏","This is so Doppe","Mast content , Mazaa aa gya!","Hi Shaandar video","Kep it goiinG!","Hii this is so excellent!! More video please .","Out of this world , It is absolutely quick!","Hello , This looks so easy , Thanks for this video!!","unique one guys","Hii this is Easy","Hi , This is certainly excellent , Mindblowing .","Hii guys Great trail!!! Thanks a ton","Killing it!","Mindblowing ","This is really the best post I saw today!! Killing it!!","Mindblowing!!! It is certainly quick!","Thanks a ton!!","honestly delicious ,","this video!!! Commendable","Yo people! quick video!!","unique and unique ","Hi this is so excellent","Sabse Bhokaal","amazing!!"]
    comment = Comment()
    userprofile = get_userprofile(user_id)
    comment.comment       = random.choice(comment_list)
    comment.comment_html  = random.choice(comment_list)
    comment.language_id   = userprofile[0].language
    comment.user_id       = user_id
    comment.topic_id      = topic_id
    comment.save()
    # topic = get_topic(topic_id)
    # # topic.update(comment_count = F('comment_count')+1)
    # topic.update(last_commented = timezone.now())
    # # userprofile.update(answer_count = F('answer_count')+1)
    # # add_bolo_score(user_id, 'reply_on_topic', comment)

def fix_follower(user_id):
    each_real_user = UserProfile.objects.get(user_id = user_id)
    follower_counter = each_real_user.follower_count
    real_follower_count = Follower.objects.filter(user_following_id = each_real_user.user_id, is_active = True).distinct('user_follower_id').count()
    follow_count = each_real_user.follow_count
    real_follow_count = Follower.objects.filter(user_follower_id = each_real_user.user_id, is_active = True).distinct('user_following_id').count()
    if follower_counter > real_follower_count:
        required_follower = follower_counter - real_follower_count
        print required_follower
        # user_ids = UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=get_redis_follower(each_real_user.user_id)).values_list('user_id',flat=True)[:required_follower]
        # for each_user_id in user_ids:
        #     status = action_follow(each_user_id, each_real_user.user_id)
        #     if status:
        #         required_follower-=1
        action_follow(each_real_user.user_id,required_follower)
    if not follow_count == real_follow_count  or not follower_counter == real_follower_count:
        real_follower_count = Follower.objects.filter(user_following_id = each_real_user.user_id, is_active = True).distinct('user_follower_id').count()
        real_follow_count = Follower.objects.filter(user_follower_id = each_real_user.user_id, is_active = True).distinct('user_following_id').count()
        UserProfile.objects.filter(pk=each_real_user.id).update(follower_count = real_follower_count,follow_count = real_follow_count)
        print "follower_counter: ",follower_counter,"\n","real_follower_count: ",real_follower_count,"\n","follow_count: ",follow_count,"\n","real_follow_count: ",real_follow_count,"\n"
#follow
def action_follow(user_id,no_of_follower):
    to_be_created_follow = []
    user_ids = UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=get_redis_follower(user_id)).values_list('user_id',flat=True)[:no_of_follower]
    for each_user_id in user_ids:
        my_dict={}
        my_dict['user_follower_id'] = each_user_id
        my_dict['user_following_id'] = user_id
        to_be_created_follow.append(my_dict)
    total_created=len(to_be_created_follow)
    aList = [Follower(**vals) for vals in to_be_created_follow]
    newly_bolo = Follower.objects.bulk_create(aList, batch_size=10000)
    print "total created",total_created
    get_redis_following(user_id)
    get_redis_follower(user_id)

# def action_follow(test_user_id,any_user_id):
#     follow,is_created = Follower.objects.get_or_create(user_follower_id = test_user_id,user_following_id=any_user_id)
#     if is_created:
#         userprofile = get_userprofile(test_user_id)
#         userprofile.update(follow_count = F('follow_count')+1)
#         update_redis_follower(any_user_id,test_user_id,True)
#         update_redis_following(test_user_id,any_user_id,True)
#         update_profile_counter(test_user_id,'follow_count',1, True)
#         return True

def get_topic(pk):
    return Topic.objects.filter(pk=pk)

def get_user(pk):
    return User.objects.get(pk=pk)

def get_userprofile(user_id):
    return UserProfile.objects.filter(user_id=user_id)


def add_to_history(user, score, action, action_object, is_removed):
    from forum.topic.models import BoloActionHistory
    try:
        history_obj = BoloActionHistory.objects.get( user = user, action_object_type=ContentType.objects.get_for_model(action_object), action_object_id = action_object.id, action = action )
    except Exception as e:
        print e
        history_obj = BoloActionHistory( user = user, action_object = action_object, action = action, score = score )
    history_obj.is_removed = is_removed
    history_obj.save()

def get_weight_object(key):
    try:
        return Weight.objects.get(features = key)
    except:
        return None

def get_weight(key):
    weights = Weight.objects.values('features','weight')
    for element in weights:
        if str(element.get('features').lower()) == str(key.lower()):
            return element.get('weight')
    return 0

def add_bolo_score(user_id, feature, action_object):
    score = get_weight(feature)
    if score > 0:
        userprofile = UserProfile.objects.filter(user_id = user_id)
        userprofile.update(bolo_score = F('bolo_score')+ int(score))
        weight_obj = get_weight_object(feature)
        if weight_obj:
            add_to_history(userprofile[0].user, score, get_weight_object(feature), action_object, False)
        if feature in ['create_topic','create_topic_en']:
            from forum.topic.models import Notification
            notification_type = '8'
            notify_owner = Notification.objects.create(for_user_id = user_id ,topic = action_object, \
                    notification_type=notification_type, user_id = user_id)

def get_list_dict_diff(list1,list2):
    final_list=[]
    if not list1 or not list2:
        return list1
    else:
        for each in list1:
            if not each in list2:
                final_list.append(each)
    return final_list

def find_set_diff(list_a, list_b, key_list):
    if not list_a or not list_b:
        return []
    
    df_a = pd.DataFrame(list_a, columns = key_list)
    df_b = pd.DataFrame(list_b, columns = key_list)
    set_diff = pd.concat([df_a, df_b, df_b]).drop_duplicates(keep = False)
    # print(set_diff.T.to_dict().values())
    return set_diff.T.to_dict().values()



