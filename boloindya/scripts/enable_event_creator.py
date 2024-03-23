from forum.user.models import UserProfile
from django.conf import settings

class EnableEventCreator:
	def __init__(self, min_follower_count):
		self.min_follower_count = min_follower_count

	def start(self):
		print("start")
		userprofile = UserProfile.objects.filter(is_event_creator=False,follower_count__gte=self.min_follower_count).update(is_event_creator=True)
		print("done")

def run():
	EnableEventCreator(settings.MIN_FOLLOWER_COUNT_FOR_EVENT_CREATOR).start()