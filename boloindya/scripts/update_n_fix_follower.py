# -*- coding: utf-8 -*-
from forum.topic.models import *
from django.contrib.auth.models import User
from forum.user.models import UserProfile,Follower
import random
from datetime import datetime, timedelta, date
from drf_spirit.utils import add_bolo_score
from forum.comment.models import Comment
from django.db.models import F,Q
from forum.user.utils.follow_redis import update_redis_follower,update_redis_following, get_redis_follower
from forum.user.utils.bolo_redis import update_profile_counter

def run():
    default_batch_size = 10000
    j=0
    counter = 1
    my_counter = 1
    no_of_elemnts = UserProfile.objects.filter(is_test_user=False).order_by('-follower_count','-follow_count').count()
    while(j*default_batch_size<no_of_elemnts):
        j+=1
        entries_to_created = []
        print "start time:", datetime.now()
        all_real_user_userprofile = UserProfile.objects.filter(is_test_user=False).order_by('-follower_count','-follow_count')[j*default_batch_size:default_batch_size*(j+1)]
        for each_real_user in all_real_user_userprofile:
            print "##############",counter,'/',no_of_elemnts,"#################"
            counter+=1
            follower_counter = each_real_user.follower_count
            real_follower_count = Follower.objects.filter(user_following_id = each_real_user.user.id, is_active = True).count()
            follow_count = each_real_user.follow_count
            real_follow_count = Follower.objects.filter(user_follower_id = each_real_user.user.id, is_active = True).count()
            if follower_counter > real_follower_count:
                required_follower = follower_counter - real_follower_count
                print required_follower
                user_ids = UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=get_redis_follower(each_real_user.user.id)).values_list('user_id',flat=True)[:required_follower]
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
        print "end time:", datetime.now()
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