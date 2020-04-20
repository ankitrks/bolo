from jarvis.models import FCMDevice, UserCountNotification
from drf_spirit.utils import language_options
from forum.category.models import Category
from forum.topic.models import Topic
import json

def run():	
	category = Category.objects.filter(parent__isnull=False)
	all_obj=FCMDevice.objects.filter(is_uninstalled=False)

	#all user group
	try:
		user=UserCountNotification.objects.get(language='0', user_group='0', category__isnull=True)
		user.no_of_user=all_obj.count()
		user.save()
	except:
		user=UserCountNotification()
		user.user_group='0'
		user.no_of_user=all_obj.count()
		user.save()

	#install and never sign up 	
	try:
		user=UserCountNotification.objects.get(language='0', user_group='2')
		user.no_of_user=all_obj.filter(user__isnull=True).count()
		user.save()
	except:
		user=UserCountNotification()
		user.user_group='2'
		user.no_of_user=all_obj.filter(user__isnull=True).count()
		user.save()

	#Never Created A Video 
	topics=Topic.objects.filter(is_vb=True).order_by('-user__pk').distinct('user').values_list('user__pk', flat=True)
	device=all_obj.filter(user__isnull=False).exclude(user__pk__in=topics)
	try:
		user=UserCountNotification.objects.get(language='0', user_group='6')
		user.fcm_users=json.dumps(list(device.values_list('id', flat=True)))
		user.no_of_user=device.count()
		user.save()
	except:
		user=UserCountNotification()
		user.user_group='6'
		user.no_of_user=device.count()
		user.fcm_users=json.dumps(list(device.values_list('id', flat=True)))
		user.save()



	for each_category in category:	
		cate_ids=all_obj.filter(user__st__sub_category=each_category)
		try:
			user=UserCountNotification.objects.get(language='0', category=each_category)
			user.fcm_users=json.dumps(list(cate_ids.values_list('id', flat=True)))
			user.no_of_user=cate_ids.count()
			user.save()
		except:
			user=UserCountNotification()
			user.language='0'
			user.fcm_users=json.dumps(list(cate_ids.values_list('id', flat=True)))
			user.category=each_category
			user.no_of_user=cate_ids.count()
			user.save()
		print(each_category, cate_ids.count())
		print(cate_ids.values_list('pk', flat=True))
	for each in language_options:
		if each[0] != '0':
			lang_ids=all_obj.filter(user__st__language=each[0])
			try:
				user=UserCountNotification.objects.get(language=each[0])
				user.fcm_users=json.dumps(list(lang_ids.values_list('id', flat=True)))
				user.no_of_user=lang_ids.count()
				user.save()
			except:
				user=UserCountNotification()
				user.language=each[0]
				user.fcm_users=json.dumps(list(lang_ids.values_list('id', flat=True)))
				user.no_of_user=lang_ids.count()
				user.save()
			print(each, lang_ids.count())
			print(lang_ids.values_list('pk', flat=True))
			for each_category in category:	
				cate_ids=lang_ids.filter(user__st__sub_category=each_category)
				try:
					user=UserCountNotification.objects.get(language=each[0], category=each_category)
					user.fcm_users=json.dumps(list(cate_ids.values_list('id', flat=True)))
					user.no_of_user=cate_ids.count()
					user.save()
				except:
					user=UserCountNotification()
					user.language=each[0]
					user.fcm_users=json.dumps(list(cate_ids.values_list('id', flat=True)))
					user.category=each_category
					user.no_of_user=cate_ids.count()
					user.save()
				print(each_category, cate_ids.count())
				print(cate_ids.values_list('pk', flat=True))
			try:
				user=UserCountNotification.objects.get(language=each[0], user_group='6')
				user.fcm_users=json.dumps(list(device.filter(user__st__language=each[0]).values_list('id', flat=True)))
				user.no_of_user=device.count()
				user.save()
			except:
				user=UserCountNotification()
				user.language=each[0]
				user.user_group='6'
				user.no_of_user=device.count()
				user.fcm_users=json.dumps(list(device.filter(user__st__language=each[0]).values_list('id', flat=True)))
                user.save()


