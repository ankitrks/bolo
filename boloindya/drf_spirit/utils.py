from django.apps import apps
from forum.user.models import UserProfile, Weight


def add_to_history(user, score, action, action_object, is_removed):
    from forum.topic.models import BoloActionHistory
    try:
        history_obj = BoloActionHistory.objects.get( user = user, action_object = action_object, action = action )
    except:
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
    userprofile = UserProfile.objects.get(user_id = user_id)
    userprofile.bolo_score+= int(score)
    userprofile.save()
    weight_obj = get_weight_object(feature)
    if weight_obj:
        add_to_history(userprofile.user, score, get_weight_object(feature), action_object, False)
    if feature in ['create_topic','create_topic_en']:
        from forum.topic.models import Notification
        notification_type = '8'
        # if admin_action_type == 'no_monetize':
        #     notification_type = '8'
        notify_owner = Notification.objects.create(for_user_id = user_id ,topic = action_object, \
                notification_type=notification_type, user_id = user_id)

def reduce_bolo_score(user_id, feature, action_object, admin_action_type=''):
    score = get_weight(feature)
    userprofile = UserProfile.objects.get(user_id = user_id)
    userprofile.bolo_score-= int(score)
    if userprofile.bolo_score < 95:
        userprofile.bolo_score = 95
    userprofile.save()
    weight_obj = get_weight_object(feature)
    if weight_obj:
        add_to_history(userprofile.user, score, get_weight_object(feature), action_object, True)
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

def shortcounterprofile(counter):
    counter = int(counter)
    if counter>10000 and counter< 99999:
        return str(counter/1000.0)[:4]+'K'
    else:
        return counter



def shorcountertopic(counter):
    counter = int(counter)
    if counter>1000 and counter< 9999:
        return str(counter/1000.0)[:3]+'K'
    elif counter >9999:
        return str(counter/1000.0)[:4]+'K'
    else:
        return counter

def calculate_encashable_details(user):
    try:
        from forum.payment.models import PaymentCycle,EncashableDetail,PaymentInfo
        from forum.topic.models import BoloActionHistory
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
        userprofile = UserProfile.objects.get(user = user)
        userprofile.encashable_bolo_score = total_bolo_score_in_this_cycle
        userprofile.save()
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









