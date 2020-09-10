# -*- coding: utf-8 -*-
from forum.topic.models import *
from django.contrib.auth.models import User
from forum.user.models import UserProfile
from datetime import datetime, timedelta, date
from django.db.models import F,Q, Count
from forum.user.utils.follow_redis import *
from forum.topic.utils import *

def run():
    duplicate_userprofile = UserProfile.objects.exclude(Q(android_did = '')|Q(android_did__isnull=True)).values('android_did').annotate(Count('user_id')).filter(user_id__count__gt=1).order_by('-user_id__count')
    length_of_duplicate = len(duplicate_userprofile)
    print "total duplicate ocurrence:",length_of_duplicate
    counter = 1
    for each_duplicate_userprofile in duplicate_userprofile:
        try:
            print "##############",counter,'/',length_of_duplicate,"#################"
            counter+=1
            print each_duplicate_userprofile
            single_instance_duplicate = UserProfile.objects.filter(Q(mobile_no = '')|Q(mobile_no__isnull=True)).filter(Q(social_identifier = '')|Q(social_identifier__isnull=True)).filter(android_did= each_duplicate_userprofile['android_did']).values_list('user_id',flat=True).order_by('-id')
            print single_instance_duplicate
            base_user_id = single_instance_duplicate[0]
            duplicate_user_instance = single_instance_duplicate[1:]
            print base_user_id, duplicate_user_instance
            VBseen.objects.filter(user_id__in = duplicate_user_instance).update(user_id = base_user_id)
            set_redis_android_id(each_duplicate_userprofile['android_did'],base_user_id)
            for each_user_id in duplicate_user_instance:
                delete_redis("bi:vb_seen:"+str(each_user_id))
            delete_redis("bi:vb_seen:"+str(base_user_id))
            get_redis_vb_seen(base_user_id)
            UserProfile.objects.filter(user_id__in = duplicate_user_instance).update(android_did = 'duplicate_'+str(each_duplicate_userprofile['android_did']))
        except Exception as e:
            print e



