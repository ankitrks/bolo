from jarvis.models import PushNotification
from datetime import datetime, timedelta

def run():
	today=datetime.now()
	push=PushNotification.objects.filter(is_scheduled=True, is_executed=False, is_removed=False, scheduled_time__lte=today)
	if push:
		print(push)