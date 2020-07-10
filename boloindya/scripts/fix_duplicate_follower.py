# -*- coding: utf-8 -*-
from forum.topic.models import *
from django.contrib.auth.models import User
from forum.user.models import UserProfile,Follower
import random
from datetime import datetime, timedelta, date
from drf_spirit.utils import add_bolo_score
from forum.comment.models import Comment
from django.db.models import F,Q, Count
from forum.user.utils.follow_redis import get_redis_follower, update_redis_follower,update_redis_following
from forum.user.utils.bolo_redis import update_profile_counter

def run():
    duplicate_follower = Follower.objects.filter(is_active = True).values('user_follower_id','user_following_id').annotate(Count('id')).filter(id__count__gt=1)
    print duplicate_follower
    counter = 0
    my_counter = 1
    max_user_required = 10000
    for each_duplicate_follower in duplicate_follower:
        print "##############",counter,'/',len(duplicate_follower),"#################"
        counter+=1
        print each_duplicate_follower
        single_instance_duplicate = Follower.objects.filter(user_following_id= each_duplicate_follower['user_following_id'], user_follower_id= each_duplicate_follower['user_follower_id'],is_active = True).values_list('pk',flat=True).order_by('id')
        print single_instance_duplicate
        base_follow = single_instance_duplicate[0]
        duplicate_follow_instance = single_instance_duplicate[1:]
        Follower.objects.filter(pk__in=duplicate_follow_instance).update(is_active=False)

        each_real_user = UserProfile.objects.get(user_id = each_duplicate_follower['user_following_id'])
        follower_counter = each_real_user.follower_count
        real_follower_count = Follower.objects.filter(user_following_id = each_real_user.user.id, is_active = True).distinct('user_follower_id').count()
        follow_count = each_real_user.follow_count
        real_follow_count = Follower.objects.filter(user_follower_id = each_real_user.user.id, is_active = True).distinct('user_following_id').count()
        counter+=1
        if follower_counter > real_follower_count:
            required_follower = follower_counter - real_follower_count
            user_ids = UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=get_redis_follower(each_duplicate_follower['user_following_id'])).values_list('user_id',flat=True)[:required_follower]
            print required_follower
            while(required_follower):
                opt_action_user_id = random.choice(user_ids)
                status = action_follow(opt_action_user_id, each_real_user.user.id)
                if status:
                    required_follower-=1

        if not follow_count == real_follow_count  or not follower_counter == real_follower_count:
            follower_count = Follower.objects.filter(user_following_id = each_real_user.user.id, is_active = True).count()
            follow_count = Follower.objects.filter(user_follower_id = each_real_user.user.id, is_active = True).count()
            UserProfile.objects.filter(pk=each_real_user.id).update(follower_count = follower_count,follow_count = follow_count)
            print my_counter
            print "follower_counter: ",follower_counter,"\n","real_follower_count: ",real_follower_count,"\n","follow_count: ",follow_count,"\n","real_follow_count: ",real_follow_count,"\n"
            my_counter+=1



#follow
def action_follow(test_user_id,any_user_id):
    follow,is_created = Follower.objects.get_or_create(user_follower_id = test_user_id,user_following_id=any_user_id)
    if is_created:
        userprofile = get_userprofile(test_user_id)
        userprofile.update(follow_count = F('follow_count')+1)
        update_redis_follower(any_user_id,test_user_id,True)
        update_redis_following(test_user_id,any_user_id,True)
        update_profile_counter(test_user_id,'follow_count',1, True)
        return True

def get_topic(pk):
    return Topic.objects.get(pk=pk)

def get_user(pk):
    return User.objects.get(pk=pk)

def get_userprofile(user_id):
    return UserProfile.objects.filter(user_id=user_id)