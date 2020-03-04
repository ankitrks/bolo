# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from redis_utils import *
from .models import Follower


def get_redis_follower(user_id):
    key = 'follower:'+str(user_id)
    follower_list = get_redis(key)
    if not follower_list:
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
    key = 'following:'+str(user_id)
    following_list = get_redis(key)
    if not following_list:
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