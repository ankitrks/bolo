from forum.user.utils.bolo_redis import update_userprofile_all_counter
from forum.user.models import UserProfile

def run():
    for each_user_id in UserProfile.objects.filter(vb_count__gt=0).order_by('-is_business','-is_superstar','-is_popular','-vb_count').values_list('user_id', flat=True):
        try:
            update_userprofile_all_counter(each_user_id)
        except Exception as e:
            print e
