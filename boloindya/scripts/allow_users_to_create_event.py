from forum.user.models import UserProfile

def run(*args):
	try:
		if args:
			user_ids = args[0].split("=")[-1].split(',')
			UserProfile.objects.filter(pk__in=user_ids).update(is_event_creator=True)
			print("done")
	except Exception as e:
		print(e)