from django.contrib.auth.models import User
from drf_spirit.utils import check_or_create_user_pay

def run():
    for each_user in User.objects.filter(st__is_test_user=False):
    	check_or_create_user_pay(each_user.id)