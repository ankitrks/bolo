# -*- coding: utf-8 -*-
from forum.topic.models import *
from django.contrib.auth.models import User
from forum.user.models import UserProfile,Follower
import random
from datetime import datetime, timedelta, date
# from drf_spirit.utils import add_bolo_score
from forum.comment.models import Comment
from django.apps import apps
from forum.user.models import UserProfile, Weight
from django.contrib.contenttypes.models import ContentType
import copy
import pandas as pd
import gc
import decimal
from forum.user.utils.follow_redis import get_redis_follower,update_redis_follower,get_redis_following,update_redis_following
from drf_spirit.utils import create_random_user
from forum.user.utils.bolo_redis import update_profile_counter

def run():
    counter_objects_created=0
    print "Start Time Eng_Engagment: ",datetime.now()
    now = datetime.now()
    last_n_days_post_ids = Topic.objects.filter(is_popular = True, popular_boosted_time__gte = now-timedelta(days=1), is_vb=True, is_removed=False, user__st__boosted_time__isnull=True).order_by('-date').values_list('id',flat=True)
    last_n_days_post_ids = list(last_n_days_post_ids)

    post_counter = 0
    for each_seen_id in last_n_days_post_ids:
        gc.collect()
        post_counter+=1
        already_vbseen=None
        print "#######################   ",post_counter,"/",len(last_n_days_post_ids),"      ##########################"
        try:
            print "before: views updation",datetime.now()
            each_seen = Topic.objects.get(pk=each_seen_id)
            if each_seen.is_popular:
                required_view_count = random.randrange(3000000,5000000)
            else:
                required_view_count = random.randrange(150000,500000)
            if required_view_count:
                multiplication_factor = decimal.Decimal(random.randrange(int(required_view_count/850),int(required_view_count/750)))
                print "i am boosted: ",multiplication_factor
            else:
                multiplication_factor = 1
                print "i am non popular: ",multiplication_factor
            if each_seen.date +timedelta(minutes=10) > now:
                number_seen = random.randrange(6,100)
            elif each_seen.date +timedelta(minutes=10) < now and each_seen.date +timedelta(minutes=30) > now and each_seen.view_count < int(100*multiplication_factor):
                number_seen = random.randrange(100,int(100*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(minutes=30) < now and each_seen.date +timedelta(hours=1) > now and each_seen.view_count < int(250*multiplication_factor):
                number_seen = random.randrange(1,int(250*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=1) < now and each_seen.date +timedelta(hours=2) > now and each_seen.view_count < int(500*multiplication_factor):
                number_seen = random.randrange(1,int(500*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=3) < now and each_seen.view_count < int(750*multiplication_factor):
                number_seen = random.randrange(1,int(750*multiplication_factor)-each_seen.view_count)
            else:
                number_seen = 0
            i = 0
            print number_seen
            if number_seen:
                Topic.objects.filter(pk=each_seen_id).update(view_count = F('view_count')+number_seen)
                FVBseen.objects.create(topic_id = each_seen_id, view_count = number_seen)
                profile_updation = UserProfile.objects.filter(user = Topic.objects.get(pk=each_seen_id).user).update(own_vb_view_count = F('own_vb_view_count')+number_seen, view_count = F('view_count')+number_seen)
                update_profile_counter(Topic.objects.get(pk=each_seen_id).user_id,'view_count',number_seen,True)
            print "after: views updation",datetime.now()
            print "total created: ", number_seen
        except Exception as e:
            print e
        try:
            print "before: like creation",datetime.now()
            check_like(each_seen_id)
            print "after: like creation",datetime.now()
        except Exception as e:
            print e

        try:
            print "before: share creation",datetime.now()
            check_share(each_seen_id)
            print "after: share creation",datetime.now()
        except Exception as e:
            print e
        try:
            print "before: follower creation",datetime.now()
            check_follower(each_seen_id)
            print "after: follower creation",datetime.now()
        except Exception as e:
            print e
        
            


def check_like(topic_id):
    already_like=None
    now = datetime.now()
    each_like = Topic.objects.get(pk=topic_id)
    if each_like.is_popular:
        required_like = random.randrange(1000000,2000000)
    else:
        required_like = random.randrange(20000,50000)
    if required_like:
        multiplication_factor = decimal.Decimal(random.randrange(int(required_like/300),int(required_like/250)))
        print "i am boosted: ",multiplication_factor
    else:
        multiplication_factor = 1

    if each_like.date < now and each_like.date +timedelta(hours=1) > now and each_like.likes_count < int(220*multiplication_factor):
        number_like = random.randrange(1,int(220*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=1) < now and each_like.date +timedelta(hours=2) > now and each_like.likes_count < int(240*multiplication_factor):
        number_like = random.randrange(1,int(240*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=2.5) < now and each_like.date +timedelta(hours=3) > now and each_like.likes_count < int(245*multiplication_factor):
        number_like = random.randrange(1,int(245*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=3) < now and each_like.likes_count < int(250*multiplication_factor):
        number_like = random.randrange(1,int(250*multiplication_factor)-each_like.likes_count)
    else:
        number_like = 0

    print number_like,"number_like"
    if number_like:
        Topic.objects.filter(pk=topic_id).update(likes_count = F('likes_count')+number_like)
        FLike.objects.create(topic_id = topic_id, like_count = number_like)
        print "like given"


def check_follower(topic_id):
    now = datetime.now()
    topic = Topic.objects.get(pk=topic_id)
    user = topic.user
    userprofile = user.st
    if userprofile.is_superstar:
        multiplication_factor = decimal.Decimal(random.randrange(2500,3000))/100
        print "i am superstar: ",multiplication_factor
    elif userprofile.is_popular and not userprofile.is_superstar:
        multiplication_factor = decimal.Decimal(random.randrange(240,750))/100
        print "i am popular: ",multiplication_factor
    elif not userprofile.is_popular and not userprofile.is_superstar:
        multiplication_factor = decimal.Decimal(random.randrange(100,240))/100
        print "i am normal: ",multiplication_factor
    else:
        multiplication_factor = 1

    if topic.date +timedelta(minutes=10) > now:
        required_follower = random.randrange(0,2)
    elif topic.date +timedelta(minutes=10) < now and topic.date +timedelta(minutes=30) > now and userprofile.follower_count < int(50*multiplication_factor):
        required_follower = random.randrange(1,int(50*multiplication_factor)-userprofile.follower_count)
    elif topic.date +timedelta(minutes=30) < now and topic.date +timedelta(hours=2) > now and userprofile.follower_count < int(100*multiplication_factor):
        required_follower = random.randrange(1,int(100*multiplication_factor)-userprofile.follower_count)
    elif topic.date +timedelta(hours=2) < now and topic.date +timedelta(hours=4) > now and userprofile.follower_count < int(200*multiplication_factor):
        required_follower = random.randrange(1,int(200*multiplication_factor)-userprofile.follower_count)
    elif topic.date +timedelta(hours=4) < now and topic.date +timedelta(hours=6) > now and userprofile.follower_count < int(300*multiplication_factor):
        required_follower = random.randrange(1,int(300*multiplication_factor)-userprofile.follower_count)
    elif topic.date +timedelta(hours=6) < now and topic.date +timedelta(hours=8) > now and userprofile.follower_count < int(400*multiplication_factor):
        required_follower = random.randrange(1,int(400*multiplication_factor)-userprofile.follower_count)
    else:
        required_follower = 1

    follower_counter = 0
    all_test_userprofile_id = UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=get_redis_follower(user.id)).values_list('user_id',flat=True)[:required_follower]
    if len(all_test_userprofile_id) < required_follower:
        print 'user_created:',required_follower-len(all_test_userprofile_id)
        create_random_user(required_follower-len(all_test_userprofile_id))
        all_test_userprofile_id = UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=get_redis_follower(user.id)).values_list('user_id',flat=True)[:required_follower]
    user_ids = list(all_test_userprofile_id)
    to_be_created_follow = []
    for each_user_id in user_ids:
        my_dict={}
        my_dict['user_follower_id'] = each_user_id
        my_dict['user_following_id'] = userprofile.user_id
        to_be_created_follow.append(my_dict)
    total_created=len(to_be_created_follow)
    aList = [Follower(**vals) for vals in to_be_created_follow]
    newly_bolo = Follower.objects.bulk_create(aList, batch_size=10000)
    print total_created
    score = get_weight('followed')
    UserProfile.objects.filter(pk=userprofile.id).update(follower_count=F('follower_count')+total_created,bolo_score=F('bolo_score')+(score*total_created))
    get_redis_following(userprofile.user_id)
    get_redis_follower(userprofile.user_id)
    update_profile_counter(userprofile.user_id,'follower_count',total_created, True)

def check_share(topic_id):
    now = datetime.now()
    single_topic = Topic.objects.get(pk= topic_id)
    topic = get_topic(topic_id)
    if single_topic.is_popular:
        required_whatsapp_count = random.randrange(250000,500000)
        required_other_share = random.randrange(100000,200000)
    else:
        required_whatsapp_count = random.randrange(5000,10000)
        required_other_share = random.randrange(1000,5000)

    whatsapp_multiplication_factor = 1
    other_multiplication_factor = 1
    if required_whatsapp_count:
        whatsapp_multiplication_factor = decimal.Decimal(random.randrange(int(required_whatsapp_count/500),int(required_whatsapp_count/250)))
    if required_other_share:
        other_multiplication_factor = decimal.Decimal(random.randrange(int(required_other_share/500),int(required_other_share/250)))

    try:
        if single_topic.date +timedelta(minutes=10) > now:
            whatsapp_share_count = random.randrange(6,100)
        elif single_topic.date +timedelta(minutes=10) < now and single_topic.date +timedelta(minutes=30) > now and single_topic.whatsapp_share_count < int(100*whatsapp_multiplication_factor):
            whatsapp_share_count = random.randrange(100,int(100*whatsapp_multiplication_factor)-single_topic.whatsapp_share_count)
        elif single_topic.date +timedelta(minutes=30) < now and single_topic.date +timedelta(hours=1) > now and single_topic.whatsapp_share_count < int(150*whatsapp_multiplication_factor):
            whatsapp_share_count = random.randrange(1,int(150*whatsapp_multiplication_factor)-single_topic.whatsapp_share_count)
        elif single_topic.date +timedelta(hours=1) < now and single_topic.date +timedelta(hours=2) > now and single_topic.whatsapp_share_count < int(200*whatsapp_multiplication_factor):
            whatsapp_share_count = random.randrange(1,int(200*whatsapp_multiplication_factor)-single_topic.whatsapp_share_count)
        elif single_topic.date +timedelta(hours=3) < now and single_topic.whatsapp_share_count < int(250*whatsapp_multiplication_factor):
            whatsapp_share_count = random.randrange(1,int(250*whatsapp_multiplication_factor)-single_topic.whatsapp_share_count)
        else:
            whatsapp_share_count = 0
    except:
        whatsapp_share_count = 0

    try:
        if single_topic.date +timedelta(minutes=10) > now:
            other_share_count = random.randrange(6,100)
        elif single_topic.date +timedelta(minutes=10) < now and single_topic.date +timedelta(minutes=30) > now and single_topic.whatsapp_share_count < int(100*other_multiplication_factor):
            other_share_count = random.randrange(100,int(100*other_multiplication_factor)-single_topic.other_share_count)
        elif single_topic.date +timedelta(minutes=30) < now and single_topic.date +timedelta(hours=1) > now and single_topic.whatsapp_share_count < int(150*other_multiplication_factor):
            other_share_count = random.randrange(1,int(150*other_multiplication_factor)-single_topic.other_share_count)
        elif single_topic.date +timedelta(hours=1) < now and single_topic.date +timedelta(hours=2) > now and single_topic.whatsapp_share_count < int(200*other_multiplication_factor):
            other_share_count = random.randrange(1,int(200*other_multiplication_factor)-single_topic.other_share_count)
        elif single_topic.date +timedelta(hours=3) < now and single_topic.whatsapp_share_count < int(250*other_multiplication_factor):
            other_share_count = random.randrange(1,int(250*other_multiplication_factor)-single_topic.other_share_count)
        else:
            other_share_count = 0
    except:
        other_share_count = 0

    if whatsapp_share_count:
        topic.update(whatsapp_share_count = F('whatsapp_share_count')+whatsapp_share_count)
    if other_share_count:
        topic.update(other_share_count = F('other_share_count')+other_share_count)
    if whatsapp_share_count+other_share_count:
        topic.update(total_share_count = F('total_share_count')+whatsapp_share_count+other_share_count)
    

#like
def action_like(user_id,topic_id):
    liked,is_created = Like.objects.get_or_create(topic_id = topic_id ,user_id = user_id)
    if is_created:
        topic = get_topic(topic_id)
        topic.update(likes_count=F('likes_count')+1)
        userprofile = get_userprofile(user_id).update(like_count = F('like_count')+1)
        add_bolo_score(user_id, 'liked', topic[0])

#seen
def action_seen(user_id,topic_id):
    topic = get_topic(topic_id)
    vbseen = VBseen.objects.filter(user_id = user_id,topic_id = topic_id)
    if not vbseen:
        vbseen = VBseen.objects.create(user_id = user_id,topic_id = topic_id)
        add_bolo_score(topic[0].user.id, 'vb_view', vbseen)
    else:
       vbseen = VBseen.objects.create(user_id = user_id,topic_id = topic_id)
    topic.update(view_count = F('view_count')+1)
    userprofile = get_userprofile(topic[0].user.id).update(view_count = F('view_count')+1,own_vb_view_count = F('own_vb_view_count')+1)

#follow
def action_follow(test_user_id,any_user_id):
    follow,is_created = Follower.objects.get_or_create(user_follower_id = test_user_id,user_following_id=any_user_id)
    userprofile = get_userprofile(test_user_id)
    followed_user = get_userprofile(any_user_id)
    if is_created:
        # add_bolo_score(test_user_id, 'follow', userprofile[0])
        add_bolo_score(any_user_id, 'followed', followed_user[0])
        userprofile.update(follow_count = F('follow_count')+1)
        followed_user.update(follower_count = F('follower_count')+1)
        update_redis_following(test_user_id,any_user_id,True)
        update_redis_follower(any_user_id,test_user_id,True)
        return True
    return False

#share
def action_share(user_id, topic_id):
    share_type =['facebook_share','whatsapp_share','linkedin_share','twitter_share']
    share_on = random.choice(share_type)
    userprofile = get_userprofile(user_id)
    topic = get_topic(topic_id)
    if share_on == 'facebook_share':
        # shared = SocialShare.objects.create(topic = topic[0],user_id = user_id,share_type = '0')
        topic.update(facebook_share_count = F('facebook_share_count')+1 )  
        topic.update(total_share_count = F('total_share_count')+1)
        # add_bolo_score(user_id, 'facebook_share', topic[0])
        userprofile.update(share_count = F('share_count')+1)
    elif share_on == 'whatsapp_share':
        # shared = SocialShare.objects.create(topic = topic[0],user_id = user_id,share_type = '1')
        topic.update(whatsapp_share_count = F('whatsapp_share_count')+1)
        topic.update(total_share_count = F('total_share_count')+1)
        # add_bolo_score(user_id, 'whatsapp_share', topic[0])
        userprofile.update(share_count = F('share_count')+1)
    elif share_on == 'linkedin_share':
        # shared = SocialShare.objects.create(topic = topic[0],user_id = user_id,share_type = '2')
        topic.update(linkedin_share_count = F('linkedin_share_count')+1)
        topic.update(total_share_count = F('total_share_count')+1)
        # add_bolo_score(user_id, 'linkedin_share', topic[0])
        userprofile.update(share_count = F('share_count')+1)
    elif share_on == 'twitter_share':
        # shared = SocialShare.objects.create(topic = topic[0],user_id = user_id,share_type = '3')
        topic.update(twitter_share_count = F('twitter_share_count')+1)
        topic.update(total_share_count = F('total_share_count')+1)
        # add_bolo_score(user_id, 'twitter_share', topic[0])
        userprofile.update(share_count = F('share_count')+1)

#comment like
def action_comment_like(user_id,comment):
    liked,is_created = Like.objects.get_or_create(comment = comment ,user_id = user_id)
    if is_created:
        comment.likes_count = F('likes_count')+1
        comment.save()
        add_bolo_score(user_id, 'liked', comment)
        userprofile = get_userprofile(user_id)
        userprofile.update(like_count = F('like_count')+1)


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
        userprofile = UserProfile.objects.get(user_id = user_id)
        userprofile.bolo_score+= int(score)
        userprofile.save()
        weight_obj = get_weight_object(feature)
        if weight_obj:
            add_to_history(userprofile.user, score, get_weight_object(feature), action_object, False)
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