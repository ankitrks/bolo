from django.contrib.auth.models import User
from forum.user.models import UserProfile
from drf_spirit.utils import check_or_create_user_pay

def run():
    for each_user in UserProfile.objects.filter(is_test_user=False).order_by('-vb_count'):
    	check_or_create_user_pay(each_user.user.id)