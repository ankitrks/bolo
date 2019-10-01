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
    if feature in['create_topic','create_topic_en']:
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
    # if feature == 'create_topic':
    #     from forum.topic.models import Notification
    #     notification_type = '7'
    #     if admin_action_type == 'no_monetize':
    #         notification_type = '8'
    #     notify_owner = Notification.objects.create(for_user_id = user_id ,topic = action_object, \
    #             notification_type=notification_type, user_id = user_id)

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





