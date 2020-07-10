from redis_utils import *
from forum.user.models import VideoPlaytime, UserPay
from forum.topic.models import Topic, VBseen, Like, SocialShare
from forum.user.models import UserProfile, Follower
from forum.comment.models import Comment
from drf_spirit.utils import shorcountertopic, shortcounterprofile, short_time
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models import Sum
import calendar
from forum.user.utils.follow_redis import get_redis_follower, get_redis_following

def get_bolo_info_combined(user_id):
    current_month_data = get_current_month_bolo_info(user_id)['data']
    last_month_data = get_last_month_bolo_info(user_id)['data']
    lifetime_data = get_lifetime_bolo_info(user_id)['data']
    data_dict = {} 
    data_dict['current_month'] = current_month_data
    data_dict['last_month'] = last_month_data
    data_dict['lifetime_data'] = lifetime_data
    return data_dict


def get_current_month_bolo_info(user_id):
    '''
    It will provide the bolo info for the current month
    '''
    key = 'current_month_bolo_info:'+str(user_id)
    bolo_info = get_redis(key)
    if not bolo_info:
        bolo_info = get_user_bolo_info(user_id=user_id,month=datetime.now().month,year=datetime.now().year)
        set_redis(key,bolo_info, True)
    return bolo_info

def set_current_month_bolo_info(user_id):
    '''
    It will provide the bolo info for the current month
    '''
    key = 'current_month_bolo_info:'+str(user_id)
    bolo_info = get_user_bolo_info(user_id=user_id,month=datetime.now().month,year=datetime.now().year)
    set_redis(key,bolo_info, True)
    return bolo_info

def get_last_month_bolo_info(user_id):
    '''
    It will provide the bolo info for the previous month
    '''
    key = 'last_month_bolo_info:'+str(user_id)
    bolo_info = get_redis(key)
    if not bolo_info:
        if datetime.now().month == 1:
            bolo_info = get_user_bolo_info(user_id=user_id,month=12,year=datetime.now().year-1)
        else:
            bolo_info = get_user_bolo_info(user_id=user_id,month=datetime.now().month-1,year=datetime.now().year)
        set_redis(key,bolo_info, True)
    return bolo_info

def set_last_month_bolo_info(user_id):
    '''
    It will provide the bolo info for the previous month
    '''
    key = 'last_month_bolo_info:'+str(user_id)
    if datetime.now().month == 1:
        bolo_info = get_user_bolo_info(user_id=user_id,month=12,year=datetime.now().year-1)
    else:
        bolo_info = get_user_bolo_info(user_id=user_id,month=datetime.now().month-1,year=datetime.now().year)
    set_redis(key,bolo_info, True)
    return bolo_info


def get_lifetime_bolo_info(user_id):
    '''
    It will provide the bolo info for the lifetime
    '''
    key = 'lifetime_bolo_info:'+str(user_id)
    bolo_info = get_redis(key)
    if not bolo_info:
        bolo_info = get_user_bolo_info(user_id=user_id,month=None,year=None)
        set_redis(key,bolo_info, True)
    return bolo_info

def set_lifetime_bolo_info(user_id):
    key = 'lifetime_bolo_info:'+str(user_id)
    bolo_info = get_user_bolo_info(user_id=user_id,month=None,year=None)
    set_redis(key,bolo_info, True)
    return bolo_info

def get_referral_code_info(ref_code):
    referral_info = get_redis(ref_code)
    if not referral_info:
        code_obj = ReferralCode.objects.using('default').get(code__iexact = ref_code, is_active = True)
        data = {"ref_code_id":code_obj.id, "is_active":code_obj.is_active}
        set_redis(ref_code, data, False)
        return code_obj.id
    elif referral_info['is_active']:
        return referral_info['ref_code_id']
    else:
        return None

def get_user_bolo_info(user_id,month=None,year=None):
    """
    post:
        Required Parameters
        start_date = request.POST.get('start_date', None)
        end_date = request.POST.get('end_date',None)
        month = request.POST.get('month', None)
        year = request.POST.get('year',None)
    """
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
            total_video = Topic.objects.filter(is_vb = True,is_removed=False,user=user)
            #total_video_id = list(Topic.objects.filter(is_vb = True,user=user).values_list('pk',flat=True))
            total_video_id = list(total_video.values_list('pk',flat=True))
            all_pay = UserPay.objects.filter(user=user,is_active=True)
            top_3_videos = Topic.objects.filter(is_vb = True,is_removed=False,user=user).order_by('-view_count')[:3]
            video_playtime = user.st.total_vb_playtime
            for each_vb in total_video:
                total_view_count+=each_vb.view_count
                total_like_count+=each_vb.likes_count
                total_comment_count+=each_vb.comment_count
                total_share_count+=each_vb.total_share_count
        else:
            total_video = Topic.objects.filter(is_vb = True,is_removed=False,user=user,date__gte=start_date, date__lte=end_date)
            total_video_id = list(Topic.objects.filter(is_vb = True,user=user,is_removed=False).values_list('pk',flat=True))
            # total_video_id = list(total_video.values_list('pk',flat=True))
            all_pay = UserPay.objects.filter(user=user,is_active=True,for_month__gte=start_date.month,for_month__lte=start_date.month,\
                for_year__gte=start_date.year,for_year__lte=start_date.year)
            top_3_videos = Topic.objects.filter(is_vb = True,is_removed=False,user=user,date__gte=start_date, date__lte=end_date).order_by('-view_count')[:3]
            all_play_time = VideoPlaytime.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date,videoid__in = total_video_id).aggregate(Sum('playtime'))
            if all_play_time.has_key('playtime__sum') and all_play_time['playtime__sum']:
                video_playtime = all_play_time['playtime__sum']

            for each_vb in total_video:
                total_view_count+=each_vb.view_count
                total_like_count+=each_vb.likes_count
                total_comment_count+=each_vb.comment_count
                total_share_count+=each_vb.total_share_count
            if total_video_count.count() == 0 and total_video_id:
                total_view_count = VBseen.objects.filter(created_at__gte = start_date, created_at__lte = end_date, topic__user_id = user.id).count()
            # exclude_video_id = total_video.values_list('pk',flat=True)
            # total_view_count += VBseen.objects.filter(created_at__gte = start_date, created_at__lte = end_date, topic__user = user).exclude(topic_id__in = exclude_video_id).count()
            # total_like_count += Like.objects.filter(created_at__gte = start_date, created_at__lte = end_date, topic__user = user).exclude(topic_id__in = exclude_video_id).count()
            # total_comment_count += Comment.objects.filter(date__gte = start_date, date__lte = end_date, topic__user = user).exclude(topic_id__in = exclude_video_id).count()
            # total_share_count += SocialShare.objects.filter(created_at__gte = start_date, created_at__lte = end_date, topic__user = user).exclude(topic_id__in = exclude_video_id).count()

        for each_pay in all_pay:
            total_earn+=each_pay.amount_pay
        total_video_count = total_video.count()
        monetised_video_count = total_video.filter(is_monetized = True).count()
        unmonetizd_video_count= total_video.filter(is_monetized = False,is_moderated = True).count()
        left_for_moderation = total_video.filter(is_moderated = False).count()        
        total_view_count = shorcountertopic(total_view_count)
        total_comment_count = shorcountertopic(total_comment_count)
        total_like_count = shorcountertopic(total_like_count)
        total_share_count = shorcountertopic(total_share_count)
        video_playtime = short_time(video_playtime)
        return {'last_updated':datetime.now(),'total_video_count' : total_video_count, \
                        'monetised_video_count':monetised_video_count, 'total_view_count':total_view_count,'total_comment_count':total_comment_count,\
                        'total_like_count':total_like_count,'total_share_count':total_share_count,'left_for_moderation':left_for_moderation,\
                        'total_earn':total_earn,'video_playtime':video_playtime,'spent_time':spent_time,\
                        'top_3_videos':TopicSerializer(top_3_videos,many=True, \
                            context={'last_updated': None,\
                            'is_expand': True}).data,'unmonetizd_video_count':unmonetizd_video_count,\
                        'bolo_score':shortcounterprofile(user.st.bolo_score)}
    except Exception as e:
        print e
        return {'last_updated':datetime.now(),'total_video_count' : 0, \
                        'monetised_video_count':0, 'total_view_count':'0','total_comment_count':'0',\
                        'total_like_count':'0','total_share_count':'0','left_for_moderation':0,\
                        'total_earn':0,'video_playtime':'0 seconds','spent_time':'0 seconds',\
                        'top_3_videos':None,'unmonetizd_video_count':0,\
                        'bolo_score':shortcounterprofile(0)}




def get_userprofile_counter(user_id):
    '''
    It will provide follower count, following count, views count and video count
    '''
    key = 'userprofile_counter:'+str(user_id)
    userprofile_counter = get_redis(key)
    if not userprofile_counter:
        userprofile_counter = get_profile_counter(user_id)
        set_redis(key,userprofile_counter, True)
    return userprofile_counter

def get_userprofile_counter_inside(user_id):
    '''
    It will provide follower count, following count, views count and video count
    '''
    is_not_calulcated = True
    key = 'userprofile_counter:'+str(user_id)
    userprofile_counter = get_redis(key)
    if not userprofile_counter:
        userprofile_counter = get_profile_counter(user_id)
        is_not_calulcated = False
        set_redis(key,userprofile_counter, True)
    return userprofile_counter, is_not_calulcated

def get_profile_counter(user_id):
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
    all_vb = Topic.objects.filter(user_id = user_id , is_vb = True, is_removed = False )
    all_seen = all_vb.aggregate(Sum('view_count'))
    if all_seen.has_key('view_count__sum') and all_seen['view_count__sum']:
        view_count = all_seen['view_count__sum']
    else:
        view_count = 0

    #total videl
    video_count = all_vb.count()
    return {'follower_count':real_follower_count, 'follow_count': real_follow_count ,'view_count': view_count, 'video_count':video_count, 'last_updated': datetime.now()}

def update_profile_counter(user_id, action, value, add = True):
    # action = ['follower_count','follow_count','video_count','view_count']
    userprofile_counter, is_not_calulcated = get_userprofile_counter_inside(user_id)
    if is_not_calulcated:
        if add:
            userprofile_counter[action]+=value
        else:
            userprofile_counter[action]-=value
        userprofile_counter['last_updated'] = datetime.now()
        key = 'userprofile_counter:'+str(user_id)
        set_redis(key,userprofile_counter, True)
    if action == 'video_count':
        set_current_month_bolo_info(user_id)
        set_lifetime_bolo_info(user_id)




