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
    all_test_userprofile_id = UserProfile.objects.filter(is_test_user=True).values_list('user_id',flat=True)
    user_ids = list(all_test_userprofile_id)
    user_ids = random.sample(user_ids,10000)
    action_type =['comment','like','seen','follow','share','comment_like']
    opt_action = random.choice(action_type)
    now = datetime.now()
    last_n_days_post_ids = Topic.objects.filter(is_vb=True,is_removed=False,date__gte=now-timedelta(days=1),user__st__boosted_time__isnull=False).order_by('-date').values_list('id',flat=True)
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
            if each_seen.user.st.boost_views_count:
                multiplication_factor = decimal.Decimal(random.randrange(int(each_seen.user.st.boost_views_count/850),int(each_seen.user.st.boost_views_count/750)))
                print "i am boosted: ",multiplication_factor
            else:
                multiplication_factor = 1
                print "i am non popular: ",multiplication_factor
            print "adab",(100*multiplication_factor)-each_seen.view_count,each_seen.view_count
            if each_seen.date +timedelta(minutes=10) > now:
                number_seen = random.randrange(6,100)
            elif each_seen.date +timedelta(minutes=10) < now and each_seen.date +timedelta(minutes=30) > now and each_seen.view_count < int(100*multiplication_factor):
                number_seen = random.randrange(100,int(100*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(minutes=30) < now and each_seen.date +timedelta(hours=2) > now and each_seen.view_count < int(200*multiplication_factor):
                number_seen = random.randrange(1,int(200*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=2) < now and each_seen.date +timedelta(hours=4) > now and each_seen.view_count < int(250*multiplication_factor):
                number_seen = random.randrange(1,int(250*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=4) < now and each_seen.date +timedelta(hours=6) > now and each_seen.view_count < int(300*multiplication_factor):
                number_seen = random.randrange(1,int(300*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=6) < now and each_seen.date +timedelta(hours=8) > now and each_seen.view_count < int(350*multiplication_factor):
                number_seen = random.randrange(1,int(350*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=10) < now and each_seen.date +timedelta(hours=12) > now and each_seen.view_count < int(400*multiplication_factor):
                number_seen = random.randrange(1,int(400*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=12) < now and each_seen.date +timedelta(hours=14) > now and each_seen.view_count < int(450*multiplication_factor):
                number_seen = random.randrange(1,int(450*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=14) < now and each_seen.date +timedelta(hours=16) > now and each_seen.view_count < int(500*multiplication_factor):
                number_seen = random.randrange(1,int(500*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=16) < now and each_seen.date +timedelta(hours=18) > now and each_seen.view_count < int(550*multiplication_factor):
                number_seen = random.randrange(1,int(550*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=18) < now and each_seen.date +timedelta(hours=19) > now and each_seen.view_count < int(600*multiplication_factor):
                number_seen = random.randrange(1,int(600*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=19) < now and each_seen.date +timedelta(hours=20) > now and each_seen.view_count < int(650*multiplication_factor):
                number_seen = random.randrange(1,int(650*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=20) < now and each_seen.date +timedelta(hours=21) > now and each_seen.view_count < int(700*multiplication_factor):
                number_seen = random.randrange(1,int(700*multiplication_factor)-each_seen.view_count)
            elif each_seen.date +timedelta(hours=21) < now and each_seen.view_count < int(750*multiplication_factor):
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
            check_like(each_seen_id,user_ids)
            print "after: like creation",datetime.now()
        except Exception as e:
            print e
    try:
        increase_follower = UserProfile.objects.filter(user__st__boosted_time__isnull=False).values_list('user_id',flat=True)
        for each_user_id in increase_follower:
            print "before: follower creation",datetime.now()
            try:
                check_follower(each_user_id)
            except:
                pass
            print "after: follower creation",datetime.now()
    except Exception as e:
        print e
            


def check_like(topic_id,user_ids):
    already_like=None
    now = datetime.now()
    each_like = Topic.objects.get(pk=topic_id)
    already_like = list(Like.objects.filter(topic_id = topic_id).values('user_id','topic_id'))
    already_like_user = []
    for each_like_dict in already_like:
        already_like_user.append(each_like_dict['user_id'])
    user_want_like=[]
    new_vb_like =[]
    to_be_created_bolo=[]
    notific_dic= []
    if each_like.user.st.boost_like_count:
        multiplication_factor = decimal.Decimal(random.randrange(int(each_like.user.st.boost_like_count/300),int(each_like.user.st.boost_like_count/250)))
        print "i am boosted: ",multiplication_factor
    else:
        multiplication_factor = 1

        print "hoadoaod", multiplication_factor
    if each_like.date +timedelta(minutes=10) > now:
        number_like = random.randrange(6,20)
    elif each_like.date +timedelta(minutes=10) < now and each_like.date +timedelta(minutes=30) > now and each_like.likes_count < int(40*multiplication_factor):
        number_like = random.randrange(40,int(40*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(minutes=30) < now and each_like.date +timedelta(hours=2) > now and each_like.likes_count < int(60*multiplication_factor):
        number_like = random.randrange(1,int(60*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=2) < now and each_like.date +timedelta(hours=4) > now and each_like.likes_count < int(80*multiplication_factor):
        number_like = random.randrange(1,int(80*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=4) < now and each_like.date +timedelta(hours=6) > now and each_like.likes_count < int(100*multiplication_factor):
        number_like = random.randrange(1,int(100*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=6) < now and each_like.date +timedelta(hours=8) > now and each_like.likes_count < int(120*multiplication_factor):
        number_like = random.randrange(1,int(120*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=10) < now and each_like.date +timedelta(hours=12) > now and each_like.likes_count < int(140*multiplication_factor):
        number_like = random.randrange(1,int(140*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=12) < now and each_like.date +timedelta(hours=14) > now and each_like.likes_count < int(160*multiplication_factor):
        number_like = random.randrange(1,int(160*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=14) < now and each_like.date +timedelta(hours=16) > now and each_like.likes_count < int(180*multiplication_factor):
        number_like = random.randrange(1,int(180*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=16) < now and each_like.date +timedelta(hours=18) > now and each_like.likes_count < int(200*multiplication_factor):
        number_like = random.randrange(1,int(200*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=18) < now and each_like.date +timedelta(hours=19) > now and each_like.likes_count < int(220*multiplication_factor):
        number_like = random.randrange(1,int(220*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=19) < now and each_like.date +timedelta(hours=20) > now and each_like.likes_count < int(240*multiplication_factor):
        number_like = random.randrange(1,int(240*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=20) < now and each_like.date +timedelta(hours=21) > now and each_like.likes_count < int(245*multiplication_factor):
        number_like = random.randrange(1,int(245*multiplication_factor)-each_like.likes_count)
    elif each_like.date +timedelta(hours=21) < now and each_like.likes_count < int(250*multiplication_factor):
        number_like = random.randrange(1,int(250*multiplication_factor)-each_like.likes_count)
    else:
        number_like = 1

    user_ids = list(UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=already_like_user).values_list('user_id',flat=True)[:number_like])
    i = 0
    for each_id in user_ids:
        user_want_like.append({'user_id':each_id,'topic_id':topic_id})
    # while i < number_like:
    #     try:
    #         opt_action_user_id = random.choice(user_ids)
    #         user_want_like.append({'user_id':opt_action_user_id,'topic_id':topic_id})
    #         i += 1
    #     except:
    #         pass
    print number_like,"number_like"
    if user_want_like:
        score = get_weight('liked')
        vb_like_type = ContentType.objects.get(app_label='forum_topic', model='like')
        new_vb_like = find_set_diff(user_want_like,already_like,['user_id','topic_id'])
        if new_vb_like:
            aList = [Like(**vals) for vals in new_vb_like]
            newly_created = Like.objects.bulk_create(aList, batch_size=10000)
            Topic.objects.filter(pk=topic_id).update(likes_count = F('likes_count')+len(new_vb_like))
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
            for each in notific_dic:
                each['topic_id']=each['action_object_id']
                del each['action_object_id']
                each['topic_type']=vb_like_type
                each['for_user_id']=each_like.user.id
                each['notification_type']='5'
            aList = [Notification(**vals) for vals in notific_dic]
            notify = Notification.objects.bulk_create(aList)
            aList=None
            print "notfic completed"


def check_follower(user_id):
    try:
        now = datetime.now()
        userprofile = UserProfile.objects.get(user_id = user_id)
        if userprofile.boost_follow_count:
            multiplication_factor = decimal.Decimal(random.randrange(int(userprofile.boost_follow_count/450),int(userprofile.boost_follow_count/400)))
            print "i am boosted: ", multiplication_factor
        else:
            multiplication_factor = 1
        if userprofile.boost_span:
            boost_span = userprofile.boost_span
        else:
            boost_span = 24
        if userprofile.boosted_time + timedelta(hours=boost_span) > datetime.now()-timedelta(hours=1):
            time_passed = (datetime.now() - userprofile.boosted_time).total_seconds()/3600
            if time_passed > boost_span:
                time_passed = boost_span
            multiplication_factor = int(multiplication_factor*decimal.Decimal(boost_span)/boost_span)
            if userprofile.follower_count < int(400*multiplication_factor):
                required_follower = random.randrange(1,int(400*multiplication_factor)-userprofile.follower_count)
            else:
                required_follower = 1
            print required_follower
            follower_counter = 0
            all_test_userprofile_id = UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=get_redis_follower(userprofile.user.id)).values_list('user_id',flat=True)[:required_follower]
            if len(all_test_userprofile_id) < required_follower:
                create_random_user(required_follower-len(all_test_userprofile_id))
                all_test_userprofile_id = UserProfile.objects.filter(is_test_user=True).exclude(user_id__in=get_redis_follower(userprofile.user.id)).values_list('user_id',flat=True)[:required_follower]
            user_ids = list(all_test_userprofile_id)
            # for each_user_id in user_ids:
            #     status = action_follow(each_user_id,userprofile.user.id)
            #     if status:
            #         follower_counter+=1
            to_be_created_follow = []
            score = get_weight('followed')
            for each_user_id in user_ids:
                my_dict={}
                my_dict['user_follower_id'] = each_user_id
                my_dict['user_following_id'] = userprofile.user_id
                to_be_created_follow.append(my_dict)
            total_created=len(to_be_created_follow)
            aList = [Follower(**vals) for vals in to_be_created_follow]
            newly_bolo = Follower.objects.bulk_create(aList, batch_size=10000)
            print total_created
            UserProfile.objects.filter(pk=userprofile.id).update(follower_count=F('follower_count')+total_created,bolo_score=F('bolo_score')+(score*total_created))
            get_redis_following(userprofile.user_id)
            get_redis_follower(userprofile.user_id)
            update_profile_counter(userprofile.user_id,'follower_count',total_created, True)
    except Exception as e:
        print e



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