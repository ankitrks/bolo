from drf_spirit.utils import calculate_encashable_details
from django.contrib.auth.models import User
def run():
	try:
		for each in User.objects.all():
			calculate_encashable_details(each)
			print each
	except Exception as e:
		print e