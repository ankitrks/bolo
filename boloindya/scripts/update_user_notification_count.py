from jarvis.models import FCMDevice
from drf_spirit.utils import language_options
from forum.category.models import Category

def run():	
	category = Category.objects.filter(parent__isnull=False)
	for each in language_options:
		lang_ids=FCMDevice.objects.filter(is_uninstalled=False, user__st__language=each)
		for each_category in category:	
			cate_ids=lang_ids.filter(user__st__sub_category=each_category)


