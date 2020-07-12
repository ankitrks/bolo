from forum.user.utils.bolo_redis import get_userprofile_counter
from forum.user.models import UserProfile

def run():
	for each_user_id in UserProfile.objects.filter(vb_count__gt=0).values_list('user_id', flat=True):
		print each_user_id
		get_userprofile_counter(each_user_id)