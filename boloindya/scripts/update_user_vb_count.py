from forum.topic.models import Topic
from forum.user.models import UserProfile
from datetime import datetime

def run():
    today_users = list(Topic.objects.filter(is_removed = False, is_vb = True)\
            .filter(date__date = datetime.today().date()).values_list('user__id', flat = True))
    for profile in UserProfile.objects.filter(user__id__in = today_users):
        users_count = Topic.objects.filter(is_removed = False, is_vb = True).filter(user = profile.user).count()
        if profile.vb_count != users_count:
            profile.vb_count = users_count
            profile.save()