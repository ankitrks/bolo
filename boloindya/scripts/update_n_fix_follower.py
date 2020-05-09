# -*- coding: utf-8 -*-
from forum.topic.models import *
from django.contrib.auth.models import User
from forum.user.models import UserProfile,Follower
import random
from datetime import datetime, timedelta, date
from drf_spirit.utils import add_bolo_score
from forum.comment.models import Comment
from django.db.models import F,Q
from forum.user.utils.follow_redis import update_redis_follower,update_redis_following

def run():
    all_real_user_userprofile = UserProfile.objects.filter(is_test_user=False).filter(Q(follower_count__gt=0)|Q(follow_count__gt=0)).order_by('-follower_count','-follow_count')
    counter = 0
    max_user_required = 10000
    all_test_userprofile_id = UserProfile.objects.filter(is_test_user=True).values_list('user_id',flat=True)
    user_ids = list(all_test_userprofile_id)
    user_ids = random.sample(user_ids,max_user_required)
    for each_real_user in all_real_user_userprofile:
        print "##############",counter,'/',len(all_real_user_userprofile),"#################"
        follower_counter = each_real_user.follower_count
        real_follower_count = Follower.objects.filter(user_following_id=each_real_user.user.id,is_active=True).count()
        follow_count = each_real_user.follow_count
        real_follow_count = Follower.objects.filter(user_follower_id=each_real_user.user.id,is_active=True).count()
        counter+=1
        if follower_counter>real_follower_count:
            print "follower_counter: ",follower_counter,"\n","real_follower_count: ",real_follower_count,"\n","follow_count: ",follow_count,"\n","real_follow_count: ",real_follow_count,"\n"
            follower_counter = follower_counter-real_follower_count
            print follower_counter
            while(follower_counter):
                opt_action_user_id = random.choice(user_ids)
                status = action_follow(opt_action_user_id,each_real_user.user.id)
                if status:
                    follower_counter-=1
        if not follow_count == real_follow_count:
            UserProfile.objects.get(pk=each_real_user.id).update(follow_count=real_follow_count)

#follow
def action_follow(test_user_id,any_user_id):
    follow,is_created = Follower.objects.get_or_create(user_follower_id = any_user_id,user_following_id=test_user_id)
    if is_created:
        update_redis_following(any_user_id,test_user_id,True)
        update_redis_follower(test_user_id,any_user_id,True)

def get_topic(pk):
    return Topic.objects.get(pk=pk)

def get_user(pk):
    return User.objects.get(pk=pk)

def get_userprofile(user_id):
    return UserProfile.objects.get(user_id=user_id)