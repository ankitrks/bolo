from django.apps import apps
import calendar
from datetime import datetime
from django.conf import settings
import urllib2
import re
import random, string
from django.db.models import F,Q
from redis_utils import *
import time

language_options = (
    ('0', "All"),
    ('1', "English"),
    ('2', "Hindi"),
    ('3', "Tamil"),
    ('4', "Telugu"),
    ('5', "Bengali"),
    ('6', "Kannada"),
    ('7', "Malayalam"),
    ('8', "Gujarati"),
    ('9', "Marathi"),
    ('10', "Punjabi"),
    ('11', "Odia"),
    ('12', "Bhojpuri"),
    ('13', "Haryanvi"),
    ('14', "Sinhala"),

)

month_choices=(
    (1, "January"),
    (2, "Feburary"),
    (3, "Macrh"),
    (4, "April"),
    (5, "May"),
    (6, "June"),
    (7, "July"),
    (8, "August"),
    (9, "September"),
    (10, "October"),
    (11, "November"),
    (12, "December"),
)

salary_choices = (
    ('1', "Less than 20000"),
    ('2', "20000 - 40000"),
    ('3', "40000 - 60000"),
    ('4', "Greater than 60000"),
)

state_language={'Andaman & Nicobar Islands':'Bengali','Andhra Pradesh':'Telugu','Arunachal Pradesh':'Nishi','Assam':'Assamese','Bihar':'Hindi','Chandigarh':'Hindi','Chhattisgarh':'Hindi','Dadra & Nagar Haveli':'Hindi','Daman & Diu':'Gujarati','Delhi':'Hindi','Goa':'Konkani','Gujarat':'Gujarati','Haryana':'Hindi','Himachal Pradesh':'Hindi','Jammu and Kashmir':'Kashmiri','Jharkhand':'Hindi','Karnataka':'Kannada','Kerala':'Malayalam','Lakshadweep':'Malayalam','Madhya Pradesh':'Hindi','Maharashtra':'Marathi','Manipur':'Manipuri','Meghalaya':'Kashi','Mizoram':'Mizo','Nagaland':'Naga Languages','Odisha':'Oriya','Puducherry':'Tamil','Punjab':'Punjabi','Rajasthan':'Hindi','Sikkim':'Nepali','Tamil Nadu':'Tamil','Telangana':'Telugu','Tripura':'Bengali','Uttar Pradesh':'Hindi','Uttarakhand':'Hindi','West Bengal':'Bengali'}

def add_to_history(user, score, action, action_object, is_removed):
    from forum.topic.models import BoloActionHistory
    try:
        from django.contrib.contenttypes.models import ContentType
        history_obj = BoloActionHistory.objects.get( user = user, action_object_type=ContentType.objects.get_for_model(action_object), action_object_id = action_object.id, action = action )
    except Exception as e:
        print e
        history_obj = BoloActionHistory( user = user, action_object = action_object, action_id = action.id, score = score )
    history_obj.is_removed = is_removed
    history_obj.save()

def get_weight_object(key):
    from forum.user.models import Weight
    try:
        return Weight.objects.get(features = key)
    except:
        return None

def get_weight(key):
    from forum.user.models import Weight
    weights = Weight.objects.values('features','weight')
    for element in weights:
        if str(element.get('features').lower()) == str(key.lower()):
            return element.get('weight')
    return 0

def add_bolo_score(user_id, feature, action_object):
    from forum.user.models import UserProfile
    score = get_weight(feature)
    if score >0:
        userprofile = UserProfile.objects.filter(user_id = user_id)
        userprofile.update(bolo_score = F('bolo_score')+int(score))
        weight_obj = get_weight_object(feature)
        if weight_obj:
            add_to_history(userprofile[0].user, score, get_weight_object(feature), action_object, False)
        if feature in ['create_topic','create_topic_en']:
            from forum.topic.models import Notification
            notification_type = '8'
            # if admin_action_type == 'no_monetize':
            #     notification_type = '8'
            notify_owner = Notification.objects.create(for_user_id = user_id ,topic = action_object, \
                    notification_type=notification_type, user_id = user_id)

def reduce_bolo_score(user_id, feature, action_object, admin_action_type=''):
    from forum.user.models import UserProfile
    score = get_weight(feature)
    userprofile = UserProfile.objects.filter(user_id = user_id)
    if userprofile[0].bolo_score < 95:
        userprofile.update(bolo_score = 95)
    else:
        userprofile.update(bolo_score= F('bolo_score')-int(score))
    weight_obj = get_weight_object(feature)
    if weight_obj:
        add_to_history(userprofile[0].user, score, get_weight_object(feature), action_object, True)
    if feature in ['create_topic','create_topic_en']:
        from forum.topic.models import Notification
        notification_type = '7'
        if admin_action_type == 'no_monetize':
            notification_type = '9'
        notify_owner = Notification.objects.create(for_user_id = user_id ,topic = action_object, \
                notification_type=notification_type, user_id = user_id)

from django.utils.timezone import utc
from django.utils import timezone
from django.utils.timezone import is_aware, utc

import time
from datetime import datetime, timedelta, date

TIME_STRINGS = {
    'year': '%d year',
    'month': '%d month',
    'day': '%d day',
}
TIME_STRINGS_SECOND = {
    'year': '%d years',
    'month': '%d months',
    'day': '%d days',
}

TIMESINCE_CHUNKS = (
    (60 * 60 * 24 * 365, 'year'),
    (60 * 60 * 24 * 30, 'month'),
    (60 * 60 * 24, 'day'),
)

def shortnaturaltime(value, now_time=None):
    now = datetime.now(utc if is_aware(value) else None) if not now_time else now_time

    if value < now:
        delta = now - value
        if delta.days != 0:
            since = delta.days * 24 * 60 * 60 + delta.seconds
            for i, (seconds, name) in enumerate(TIMESINCE_CHUNKS):
                count = since // seconds
                if count != 0:
                    break
            if count <=1:
                return TIME_STRINGS[name] % count
            
            return TIME_STRINGS_SECOND[name] % count
        elif delta.seconds == 0:
            return 'now'
        elif delta.seconds < 60:
            if delta.seconds <= 1:
                return "%d second" % delta.seconds
            return "%d seconds" % delta.seconds
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            if count <= 1:
                return  "%d minute" % count
            return "%d minutes" % count
        else:
            count = delta.seconds // 60 // 60
            if count <= 1:
                return  "%d hour" % count
            return "%d hours" % count
    
    # For future strings, we return now
    return 'now'

def short_time(value):
    if value<60:
        return str(value)+" seconds"

    elif value>60 and value<3600:
        minute_value = value/float(60.0)
        rounded = int(round(minute_value,1)) if round(minute_value,1).is_integer() else round(minute_value,1)
        return str(rounded)+" minutes"
    elif value>3600:
        hour_value = value/float(3600.0)
        rounded = int(round(hour_value,1)) if round(hour_value,1).is_integer() else round(hour_value,1)
        if rounded > 999:
            rounded = shorcountertopic(rounded)+' hours'
            return rounded
        return str(rounded)+" hours"

def shortcounterprofile(counter):
    counter = int(counter)
    if counter>10000 and counter < 999999:
        return str(int(round(counter/1000.0, 1)) if round(counter/1000.0, 1).is_integer() else round(counter/1000.0, 1))+' K'
    elif counter >= 999999:
        return str(int(round(counter/1000000.0, 1)) if (round(counter/1000000.0, 1)).is_integer() else (round(counter/1000000.0, 1)))+' M'
    else:
        return counter



def shorcountertopic(counter):
    counter = int(counter)
    if counter >= 1000 and counter < 999999:
        return str(int(round(counter/1000.0, 1)) if round(counter/1000.0, 1).is_integer() else round(counter/1000.0, 1))+' K'
    elif counter >= 999999:
        return str(int(round(counter/1000000.0, 1)) if (round(counter/1000000.0, 1)).is_integer() else (round(counter/1000000.0, 1)))+' M'
    else:
        return str(counter)

def calculate_encashable_details(user):
    try:
        from forum.payment.models import PaymentCycle,EncashableDetail,PaymentInfo
        from forum.topic.models import BoloActionHistory
        from forum.user.models import UserProfile, Weight
        now = datetime.now().date()
        is_in_cycle = False
        i=0
        payment_cycle = PaymentCycle.objects.all().first()
        start_date = payment_cycle.duration_start_date
        if payment_cycle.duration_type == '1':
            end_date = start_date + timedelta(days=payment_cycle.duration_period)
        elif payment_cycle.duration_type == '2':
            end_date = start_date + timedelta(days=payment_cycle.duration_period*7)
        elif payment_cycle.duration_type == '3':
            end_date = start_date + timedelta(days=payment_cycle.duration_period*30)
        elif payment_cycle.duration_type == '4':
            end_date = start_date + timedelta(days=payment_cycle.duration_period*365)
        while not is_in_cycle:
            if payment_cycle.duration_type == '1':
                start_date = payment_cycle.duration_start_date + timedelta(days=i*payment_cycle.duration_period)
                end_date = start_date + timedelta(days=payment_cycle.duration_period)
            elif payment_cycle.duration_type == '2':
                start_date = payment_cycle.duration_start_date + timedelta(days=i*payment_cycle.duration_period*7)
                end_date = start_date + timedelta(days=payment_cycle.duration_period*7)
            elif payment_cycle.duration_type == '3':
                start_date = payment_cycle.duration_start_date + timedelta(days=i*payment_cycle.duration_period*30)
                end_date = start_date + timedelta(days=payment_cycle.duration_period*30)
            elif payment_cycle.duration_type == '4':
                start_date = payment_cycle.duration_start_date + timedelta(days=i*payment_cycle.duration_period*365)
                end_date = start_date + timedelta(days=payment_cycle.duration_period*365)
            i+=1
            if now > start_date and now <= end_date:
                is_in_cycle = True
        enchashable_detail,is_created = EncashableDetail.objects.get_or_create(user=user,duration_start_date = start_date,duration_end_date = end_date)
        if is_created:
            cycle_count = EncashableDetail.objects.filter(user = user).count()
            enchashable_detail.encashable_cycle = str(start_date)+ ' - '+str(end_date)
        all_bolo_action = BoloActionHistory.objects.filter(user = user,created_at__gt = start_date,created_at__lte=end_date,action__is_monetize=True,is_removed=False)
        total_bolo_score_in_this_cycle = 0
        all_weights = Weight.objects.filter(is_monetize = True)
        bolo_details = {}
        total_money = 0
        is_eligible_for_encash = False
        for each_bolo_weight in all_weights:
            score = 0
            all_action_bolo_score = all_bolo_action.filter(action = each_bolo_weight)
            if all_action_bolo_score:
                for each_all_action_bolo_score in all_action_bolo_score:
                    score+= each_all_action_bolo_score.score
            if score and score>=each_bolo_weight.bolo_score:
                bolo_money = (score/each_bolo_weight.bolo_score)*each_bolo_weight.equivalent_INR
                each_action_dict = {'bolo_score':score,'bolo_money':bolo_money}
                total_money+=bolo_money
                if each_bolo_weight.features=='create_topic':
                    is_eligible_for_encash = True
            else:
                each_action_dict = {'bolo_score':score,'bolo_money':0}

            bolo_details[each_bolo_weight.features] = each_action_dict
        enchashable_detail.bolo_score_details = str(bolo_details)
        for each_bolo in all_bolo_action:
            total_bolo_score_in_this_cycle += each_bolo.score
        userprofile = UserProfile.objects.filter(user = user)
        userprofile.update(encashable_bolo_score = total_bolo_score_in_this_cycle)
        all_bolo_action.update(enchashable_detail = enchashable_detail)
        enchashable_detail.bolo_score_earned = total_bolo_score_in_this_cycle
        enchashable_detail.equivalent_INR = total_money
        enchashable_detail.is_eligible_for_encash = is_eligible_for_encash
        enchashable_detail.save()
        non_eligible_bolo_score = BoloActionHistory.objects.filter(created_at__lte = start_date - timedelta(days=(end_date-start_date).days),is_encashed=False)
        non_eligible_bolo_score.update(is_eligible_for_encash = False)
        old_encash = EncashableDetail.objects.filter(user=user,duration_end_date__lte = start_date - timedelta(days=(end_date-start_date).days))
        old_encash.update(is_expired = True)
    except Exception as e:
         print e



def check_or_create_user_pay(user_id,start_date='01-04-2019'):
    from forum.topic.models import BoloActionHistory,Topic
    from forum.user.models import UserPay,Weight
    from django.contrib.auth.models import User
    user = User.objects.get(pk=user_id)
    start_date = datetime.strptime(start_date, "%d-%m-%Y")
    days = calendar.monthrange(int(start_date.year),int(start_date.month))[1]
    end_date = datetime.strptime(str(days)+'-'+str(start_date.month)+'-'+str(start_date.year)+' 23:59:59', "%d-%m-%Y %H:%M:%S")
    current_datetime = datetime.now()
    user_pay = UserPay.objects.filter(user=user,for_month=start_date.month)
    print "tIme Duration:",str(start_date),"----",str(end_date)
    # is_evaluated = True if user_pay and user_pay[0].is_evaluated else False
    language_bifurcation = []
    bolo_bifurcation = []
    total_video = Topic.objects.filter(is_vb = True,is_removed=False,user=user,date__gte=start_date, date__lte=end_date)
    total_video_count = total_video.count()
    if total_video_count>0:
        bolo_action_history = BoloActionHistory.objects.filter(user=user,created_at__gte=start_date,created_at__lte=end_date,is_removed=False)
        monetised_video_count = total_video.filter(is_monetized = True).count()
        left_for_moderation = total_video.filter(is_moderated = False).count()
        total_view_count=0
        total_like_count=0
        total_comment_count = 0
        total_share_count = 0
        for each_vb in total_video:
            total_view_count+=each_vb.view_count
            total_like_count+=each_vb.likes_count
            total_comment_count+=each_vb.comment_count
            total_share_count+=each_vb.total_share_count
        total_bolo_score=0
        for each_bolo in bolo_action_history:
            total_bolo_score+=each_bolo.score
        print 'total_video',total_video_count
        user_pay,is_created = UserPay.objects.get_or_create(user_id = user_id,for_year=start_date.year,for_month=start_date.month)
        # if not user_pay.is_evaluated:
        user_pay.total_video_created=total_video_count
        user_pay.total_monetized_video=monetised_video_count
        user_pay.left_for_moderation=left_for_moderation
        user_pay.total_like=total_like_count
        user_pay.total_comment=total_comment_count
        user_pay.total_view=total_view_count
        user_pay.total_share=total_share_count
        user_pay.total_bolo_score_earned=total_bolo_score
        # user_pay = UserPay.objects.create(user_id = user_id,for_year=start_date.year,for_month=start_date.month,total_video_created=total_video_count,total_monetized_video=monetised_video_count,\
        #     left_for_moderation=left_for_moderation,total_like=total_like_count,total_comment=total_comment_count,total_view=total_view_count,\
        #     total_share=total_share_count,total_bolo_score_earned=total_bolo_score)
        for each_language in language_options:
            lang_count = total_video.filter(language_id=each_language[0]).count()
            language_bifurcation.append({'language':each_language[1],'video_count':lang_count})
        for each_weight in Weight.objects.all():
            if each_weight.weight>0:
                single_action_bolo = bolo_action_history.filter(action=each_weight)
                total_single_action_score=0
                for each_action in single_action_bolo:
                    total_single_action_score+=each_action.score
                bolo_bifurcation.append({'feature':each_weight.features,'bolo_score':total_single_action_score})
        user_pay.videos_in_language = str(language_bifurcation)
        user_pay.bolo_bifurcation = str(bolo_bifurcation)
        # if current_datetime > end_date:
        #     user_pay.is_evaluated=True
        user_pay.save()
        # print user_pay.__dict__
    if current_datetime > end_date:
        if end_date.month==12:
            year = str(end_date.year+1)
            check_or_create_user_pay(user_id,'01-01-'+year)
        else:
            month = str(end_date.month+1)
            check_or_create_user_pay(user_id,'01-'+month+'-'+str(end_date.year))
    return True


def solr_object_to_db_object(sqs):
    result = []
    if len(sqs) != 0:
        for each in sqs:
            result.append(each.object)
    return result

def solr_userprofile_object_to_db_object(sqs):
    result = []
    if len(sqs) != 0:
        for each in sqs:
            result.append(each.object.user)
    return result

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

def get_paginated_data(data_list,page_size,page=None, offset = None):
    if not page:
        page = 1

    if offset:
        data_list = data_list[offset:]

    paginator = Paginator(data_list,page_size)
    # set_redis('paginator',paginator)
    try:
        paginated_data = paginator.page(page)
    except PageNotAnInteger:# If page is not an integer, deliver first page.
        paginated_data = paginator.page(1)
    except EmptyPage:       # If page is out of range (e.g. 9999), deliver last page of results.
        paginated_data = []

    return paginated_data,paginator.num_pages

import random

def random_string(length=10):
    valid_letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
    return ''.join((random.choice(valid_letters) for i in xrange(length)))

def generate_refer_earn_code():
    from forum.user.models import ReferralCode
    my_code = random_string()
    referal_code = ReferralCode.objects.filter(code__iexact=my_code)
    if referal_code:
        my_code = generate_refer_earn_code()
    return my_code

def get_ranked_topics(user_id,page,filter_dict,exclude_dict,sort_by='-vb_score',q_filter=None):
    from forum.topic.models import Topic
    from forum.topic.utils import get_redis_vb_seen
    if not page:
        page = 1
    page_size = settings.REST_FRAMEWORK['PAGE_SIZE']
    filter_dict['is_removed']=False
    filter_dict['is_vb']=True
    if filter_dict.has_key('language_id'):
        filter_dict['language_id'] = "'" + filter_dict['language_id'] + "'" # need to send language id AS '2' and not 2 (explicitly typecast).
    topics = []
    all_seen_vb = []

    if user_id:
        all_seen_vb = get_redis_vb_seen(user_id)
        exclude_dict['pk__in'] = all_seen_vb
    queryset = Topic.objects.filter(**filter_dict).exclude(**exclude_dict)
    if q_filter:
        queryset = queryset.filter(q_filter)

    raw_query = queryset.query.__str__().split('ORDER BY')[0]
    raw_query += ' AND ' + str(page) + ' = (SELECT COUNT(DISTINCT vb_score) FROM forum_topic_topic S1 WHERE "forum_topic_topic".vb_score <= S1.vb_score AND \
            S1.user_id = "forum_topic_topic".user_id) order by "forum_topic_topic".' + sort_by.replace('-', '') + ' desc \
            limit ' + str(page_size)
    non_seen_post = list( Topic.objects.raw(raw_query) )
    non_seen_post_count = len(non_seen_post)

    all_seen_post = []
    if not page*page_size < non_seen_post_count:
        all_seen_page = int((page*page_size - non_seen_post_count)/page_size)
        all_seen_post = Topic.objects.filter(**filter_dict).filter(pk__in=all_seen_vb)[all_seen_page*page_size:page_size*(all_seen_page+1)+1]
    topics = non_seen_post + list(all_seen_post)
    return topics

def check_url(file_path):
    try:
        u = urllib2.urlopen(str(file_path))
        return "200"
    except Exception as e:
        print e,file_path
        return "403"

def get_modified_url(old_url,new_url_domain):
    if old_url:
        regex= '((?:(https?|s?ftp):\\/\\/)?(?:(?:[A-Z0-9][A-Z0-9-]{0,61}[A-Z0-9]\\.)+)(com|net|org|eu))'
        find_urls_in_string = re.compile(regex, re.IGNORECASE)
        url = find_urls_in_string.search(old_url)
        return str(old_url.replace(str(url.group()), new_url_domain))

import random, string
def get_random_username():
    x = 'bi'+''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(10))
    x = x.lower()
    # x = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(16))
    try:
        user = User.objects.get(username=x)
        return get_random_username()
    except:
        return x

def create_random_user(no_of_user=0):
        from forum.user.models import DUser
        users_data = DUser.objects.filter(is_used=False)[:no_of_user]
        languages = language_options
        for each_user_data in users_data:
            name = each_user_data.name
            username = get_random_username(name.replace(' ','_'))
            gender = each_user_data.gender
            language = random.choice(languages)[0]
            status = create_user(name,username,gender,language)
            each_user_data.is_used = True
            each_user_data.save()

def create_user(name,username,gender,language):
    from django.contrib.auth.models import User
    from forum.user.models import UserProfile
    if not 'yyyy' in name:
        try:
            try:
                user = User.objects.create(username = username)
            except:
                user = User.objects.create(username = get_random_username(username))
            userprofile = UserProfile.objects.filter(user = user).update(**{'name':name,'language':language,'gender':gender,'is_test_user':True})
            return True
        except Exception as e:
            print e
            return False

def set_android_logs_info(value):
    key = "android_logs:" + str(datetime.now()).replace(' ', '')
    set_redis(key, value, False)

def set_sync_dump_info(value):
    key = "sync_dump:" + str(datetime.now()).replace(' ', '')
    set_redis(key, value, False)
