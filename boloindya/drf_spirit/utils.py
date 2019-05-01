
from django.apps import apps
from forum.user.models import UserProfile, Weight

def get_weight(key):
	weights = Weight.objects.values('features','weight')
	for element in weights:
		if str(element.get('features').lower()) == str(key.lower()):
			return element.get('weight')

def add_bolo_score(user_id,feature):
	score = get_weight(feature)
	userprofile = UserProfile.objects.get(user_id = user_id)
	userprofile.bolo_score+= int(score)
	userprofile.save()

from django.utils.timezone import utc
from django.utils import timezone
from django.utils.timezone import is_aware, utc

import time
from datetime import datetime, timedelta, date

TIME_STRINGS = {
    'year': '%dy',
    'month': '%dM',
    'day': '%dd',
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
            
            return TIME_STRINGS[name] % count
        elif delta.seconds == 0:
            return 'now'
        elif delta.seconds < 60:
            return "%ds" % delta.seconds
        elif delta.seconds // 60 < 60:
            count = delta.seconds // 60
            return "%dm" % count
        else:
            count = delta.seconds // 60 // 60
            return "%dh" % count
    
    # For future strings, we return now
    return 'now'
