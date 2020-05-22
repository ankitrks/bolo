# -*- coding: utf-8 -*-

from redis_utils import *
from forum.user.models import Follower, UserProfile


def get_redis_follower(user_id):
    '''
    It will provede the list of all the user id of users who followed ther user i.e user_id  <--(follow)-- other_user
    '''
    key = 'follower:'+str(user_id)
    follower_list = get_redis(key)
    if not follower_list:
        follower_list = list(Follower.objects.filter(user_following_id=user_id,is_active=True).distinct('user_follower_id').values_list('user_follower_id',flat=True))
        set_redis(key,follower_list)
    len_follower_list = len(follower_list)
    follower_count = UserProfile.objects.get(user_id=user_id).follower_count
    #print type(len_follower_list),type(follower_count)
    if not follower_count == len_follower_list:
        #print "insdied"
        follower_list = list(Follower.objects.filter(user_following_id=user_id,is_active=True).distinct('user_follower_id').values_list('user_follower_id',flat=True))
        set_redis(key,follower_list)
    return follower_list


def update_redis_follower(user_id,user_follower_id,append):
    key = 'follower:'+str(user_id)
    follower_list = get_redis(key)
    if not follower_list:
        follower_list = list(Follower.objects.filter(user_following_id=user_id,is_active=True).distinct('user_follower_id').values_list('user_follower_id',flat=True))
    if append:
        if int(user_follower_id) not in follower_list:
            follower_list.append(int(user_follower_id))
    else:
        if int(user_follower_id) in follower_list:
            follower_list.remove(int(user_follower_id))
    set_redis(key,follower_list)


def get_redis_following(user_id):
    '''
    It will provede the list of all the user id of users whom are followed by user i.e user_id --(follow)--> other_user
    '''
    key = 'following:'+str(user_id)
    following_list = get_redis(key)
    if not following_list:
        following_list = list(Follower.objects.filter(user_follower_id=user_id,is_active=True).distinct('user_following_id').values_list('user_following_id',flat=True))
        set_redis(key,following_list)
    len_following_list = len(following_list)
    follow_count = UserProfile.objects.get(user_id=user_id).follow_count
    print len_following_list,follow_count
    if not follow_count == len_following_list:
        following_list = list(Follower.objects.filter(user_follower_id=user_id,is_active=True).distinct('user_following_id').values_list('user_following_id',flat=True))
        set_redis(key,following_list)
    return following_list

def update_redis_following(user_id,user_following_id,append):
    key = 'following:'+str(user_id)
    following_list = get_redis(key)
    if not following_list:
        following_list = list(Follower.objects.filter(user_follower_id=user_id, is_active=True).distinct('user_following_id').values_list('user_following_id',flat=True))
    if append:
        if int(user_following_id) not in following_list:
            following_list.append(int(user_following_id))
    else:
        if int(user_following_id) in following_list:
            following_list.remove(int(user_following_id))
    set_redis(key,following_list)
