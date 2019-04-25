
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