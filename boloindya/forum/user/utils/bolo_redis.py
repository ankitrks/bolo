from redis_utils import *
from forum.user.models import VideoPlaytime, UserPay, OldMonthInsightData, MonthWiseFplaytime
from forum.topic.models import Topic, VBseen, Like, SocialShare, FVBseen, FLike
from forum.user.models import UserProfile, Follower
from forum.comment.models import Comment
from drf_spirit.utils import shorcountertopic, shortcounterprofile, short_time
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.db.models import Sum
import calendar
from forum.user.utils.follow_redis import get_redis_follower, get_redis_following
from forum.user.models import ReferralCode
from django.conf import settings
n = 30

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
    key = "refcode:" + str(ref_code)
    referral_info = get_redis(key)
    if not referral_info:
        code_obj = ReferralCode.objects.using('default').get(code__iexact = ref_code, is_active = True)
        data = {"ref_code_id":code_obj.id, "is_active":code_obj.is_active}
        set_redis(key, data, False)
        return code_obj.id
    elif referral_info['is_active']:
        return referral_info['ref_code_id']
    else:
        return None

def get_user_bolo_info(user_id,month=None,year=None):
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
        fplaytime = 0
        user = User.objects.get(pk=user_id)
        if month and year:
            days = calendar.monthrange(int(year),int(month))[1]
            start_date = datetime.strptime('01-'+str(month)+'-'+str(year), "%d-%m-%Y")
            end_date = datetime.strptime(str(days)+'-'+str(month)+'-'+str(year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
            if datetime.now() > end_date + timedelta(days=2) and not datetime.now().month == start_date.month:
                try:
                    insight_obj = OldMonthInsightData.objects.get(user_id = user_id , for_month = start_date.month, for_year = start_date.year)
                    return json.loads(insight_obj.insight_data)
                except:
                    pass

        if not start_date or not end_date:
            total_video = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user.id) 
            #total_video_id = list(Topic.objects.filter(is_vb = True, user_id=user.id) .values_list('pk',flat=True))
            total_video_id = list(total_video.values_list('pk',flat=True))
            real_like_count = Like.objects.filter(topic_id__in = total_video_id, is_active = True).count()
            fake_like_count = FLike.objects.filter(topic_id__in = total_video_id).aggregate(Sum('like_count'))
            if fake_like_count.has_key('like_count__sum') and fake_like_count['like_count__sum']:
                fake_like_count = fake_like_count['like_count__sum']
            else:
                fake_like_count = 0
            total_like_count = real_like_count + fake_like_count
            total_comment_count = Comment.objects.filter(topic_id__in = total_video_id, is_removed = False).count()
            all_pay = UserPay.objects.filter( user_id=user.id, is_active=True)
            all_play_time = VideoPlaytime.objects.filter(video_id__in = total_video_id).aggregate(Sum('playtime'))
            if all_play_time.has_key('playtime__sum') and all_play_time['playtime__sum']:
                video_playtime = all_play_time['playtime__sum']

            fplaytime = get_fplaytime(user_id,start_date,end_date,0,0)
            video_playtime+=fplaytime
            real_view_count = VBseen.objects.filter(topic_id__in = total_video_id).count()
            fake_view_count = FVBseen.objects.filter(topic_id__in = total_video_id).aggregate(Sum('view_count'))
            if fake_view_count.has_key('view_count__sum') and fake_view_count['view_count__sum']:
                fake_view_count = fake_view_count['view_count__sum']
            else:
                fake_view_count = 0
            total_view_count = real_view_count + fake_view_count
           
        else:
            total_video = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user.id, date__gte=start_date, date__lte=end_date)
            total_video_id = list(Topic.objects.filter(is_vb = True, user_id=user.id, is_removed=False).values_list('pk',flat=True))
            # total_video_id = list(total_video.values_list('pk',flat=True))
            total_like_count = Like.objects.filter(topic_id__in = total_video_id, is_active = True, created_at__gte=start_date, created_at__lte=end_date).count()
            real_like_count = Like.objects.filter(topic_id__in = total_video_id, created_at__gte=start_date, created_at__lte=end_date).count()
            fake_like_count = FLike.objects.filter(topic_id__in = total_video_id, created_at__gte=start_date, created_at__lte=end_date).aggregate(Sum('like_count'))
            if fake_like_count.has_key('like_count__sum') and fake_like_count['like_count__sum']:
                fake_like_count = fake_like_count['like_count__sum']
            else:
                fake_like_count = 0
            total_like_count = real_like_count + fake_like_count
            total_comment_count = Comment.objects.filter(topic_id__in = total_video_id, is_removed = False, date__gte=start_date, date__lte=end_date).count()
            all_pay = UserPay.objects.filter( user_id=user.id, is_active=True,for_month__gte=start_date.month,for_month__lte=start_date.month,\
                for_year__gte=start_date.year,for_year__lte=start_date.year)
            all_play_time = VideoPlaytime.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date,video_id__in = total_video_id).aggregate(Sum('playtime'))
            if all_play_time.has_key('playtime__sum') and all_play_time['playtime__sum']:
                video_playtime = all_play_time['playtime__sum'] 

            real_view_count = VBseen.objects.filter(topic_id__in = total_video_id, created_at__gte=start_date, created_at__lte=end_date).count()
            fake_view_count = FVBseen.objects.filter(topic_id__in = total_video_id, created_at__gte=start_date, created_at__lte=end_date).aggregate(Sum('view_count'))
            if fake_view_count.has_key('view_count__sum') and fake_view_count['view_count__sum']:
                fake_view_count = fake_view_count['view_count__sum']
            else:
                fake_view_count = 0
            fplaytime = get_fplaytime(user_id,start_date,end_date,fake_view_count,video_playtime)
            video_playtime+=fplaytime
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
        if start_date and end_date:
            if datetime.now() > end_date + timedelta(days=2) and not datetime.now().month == start_date.month:
                insight_obj, is_created = OldMonthInsightData.objects.get_or_create(user_id = user_id , for_month = start_date.month, for_year = start_date.year)
                if is_created:
                    insight_obj.insight_data = json.dumps(data)
                    insight_obj.save()
        return data
    except Exception as e:
        print e
        return {'total_video_count' : 0, \
                        'total_view_count':'0','total_comment_count':'0',\
                        'total_like_count':'0','total_share_count':'0',\
                        'total_earn':0,'video_playtime':'0 seconds','spent_time':'0 seconds',\
                        'bolo_score':shortcounterprofile(0)}

def get_fplaytime(user_id, start_date=None, end_date=None, fake_view_count=0,playtime=0):
    #hard date afterwards this logic is used
    if start_date and start_date >= datetime(2020,7,1):
        mwfplaytime,is_created = MonthWiseFplaytime.objects.get_or_create(user_id= user_id,for_month=start_date.month, for_year = start_date.year)
        fplaytime = int(fake_view_count*settings.FTIME_PLAY)
        if playtime < settings.FPLAYTIME_LIMIT and end_date + timedelta(days=1) >= datetime.now():
            mwfplaytime.fplaytime = fplaytime
            mwfplaytime.save()
        return mwfplaytime.fplaytime
    elif not start_date:
        all_fplaytime = MonthWiseFplaytime.objects.filter(user_id= user_id).aggregate(Sum('fplaytime'))
        if all_fplaytime.has_key('fplaytime__sum') and all_fplaytime['fplaytime__sum']:
            fplaytime = all_fplaytime['fplaytime__sum']
        else:
            fplaytime = 0
        return fplaytime
    else:
        return 0

def set_current_month_insight_video_info(user_id, add):
    key = 'current_month_bolo_info:'+str(user_id)
    bolo_info = get_current_month_bolo_info(user_id)
    bolo_info['total_video_count'] = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user_id,date__month=datetime.now().month).count()
    real_view_count = VBseen.objects.filter(topic__user_id = user_id, topic__is_removed = False, created_at__month=datetime.now().month).count()
    fake_view_count = FVBseen.objects.filter(topic__user_id = user_id, topic__is_removed = False, created_at__month=datetime.now().month).aggregate(Sum('view_count'))
    if fake_view_count.has_key('view_count__sum') and fake_view_count['view_count__sum']:
        fake_view_count = fake_view_count['view_count__sum']
    else:
        fake_view_count = 0
    # print real_view_count, fake_view_count
    total_view_count = real_view_count + fake_view_count
    bolo_info['total_view_count'] = shorcountertopic(total_view_count)
    set_redis(key,bolo_info, True)
    return bolo_info

def set_lifetime_insight_video_info(user_id, add):
    lifetime_key = 'lifetime_bolo_info:'+str(user_id)
    bolo_info = get_lifetime_bolo_info(user_id)
    bolo_info['total_video_count'] = Topic.objects.filter(is_vb = True,is_removed=False, user_id=user_id).count()
    real_view_count = VBseen.objects.filter(topic__user_id = user_id,topic__is_removed = False ).count()
    fake_view_count = FVBseen.objects.filter(topic__user_id = user_id, topic__is_removed = False).aggregate(Sum('view_count'))
    if fake_view_count.has_key('view_count__sum') and fake_view_count['view_count__sum']:
        fake_view_count = fake_view_count['view_count__sum']
    else:
        fake_view_count = 0
    # print real_view_count, fake_view_count
    total_view_count = real_view_count + fake_view_count
    bolo_info['total_view_count'] = shorcountertopic(total_view_count)
    userprofile_counter, is_calulcated = get_userprofile_counter_inside(user_id)
    if not is_calulcated:
        userprofile_counter['view_count'] = total_view_count
        userprofile_counter['last_updated'] = datetime.now()
        key = 'userprofile_counter:'+str(user_id)
        set_redis(key,userprofile_counter, True)
    set_redis(lifetime_key,bolo_info, True)
    return bolo_info

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
    is_calulcated = False
    key = 'userprofile_counter:'+str(user_id)
    userprofile_counter = get_redis(key)
    if not userprofile_counter:
        userprofile_counter = get_profile_counter(user_id)
        is_calulcated = True
        set_redis(key,userprofile_counter, True)
    return userprofile_counter, is_calulcated

def set_userprofile_counter(user_id):
    '''
    It will provide follower count, following count, views count and video count
    '''
    key = 'userprofile_counter:'+str(user_id)
    userprofile_counter = get_profile_counter(user_id)
    set_redis(key,userprofile_counter, True)
    return userprofile_counter

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
    total_video_id = list(Topic.objects.filter(is_vb = True,is_removed=False, user_id=user_id).values_list('pk',flat=True))
    real_view_count = VBseen.objects.filter(topic_id__in = total_video_id).count()
    fake_view_count = FVBseen.objects.filter(topic_id__in = total_video_id).aggregate(Sum('view_count'))
    if fake_view_count.has_key('view_count__sum') and fake_view_count['view_count__sum']:
        fake_view_count = fake_view_count['view_count__sum']
    else:
        fake_view_count = 0
    # print real_view_count, fake_view_count
    view_count = real_view_count + fake_view_count
    #total video
    video_count = len(total_video_id)
    return {'follower_count':real_follower_count, 'follow_count': real_follow_count ,'view_count': view_count, 'video_count':video_count, 'last_updated': datetime.now()}

def update_profile_counter(user_id, action, value, add = True):
    # action = ['follower_count','follow_count','video_count','view_count']
    # print user_id, action, value, add
    userprofile_counter, is_calulcated = get_userprofile_counter_inside(user_id)

    if not is_calulcated:
        if add:
            userprofile_counter[action]+=value
        else:
            userprofile_counter[action]-=value
        userprofile_counter['last_updated'] = datetime.now()
        key = 'userprofile_counter:'+str(user_id)
        set_redis(key,userprofile_counter, True)

    if action in ['video_count','view_count']:
        update_userprofile_all_counter(user_id)

    return True

def update_userprofile_all_counter(user_id):
    set_current_month_bolo_info(user_id)
    set_lifetime_bolo_info(user_id)
    set_userprofile_counter(user_id)


