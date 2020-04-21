from jarvis.models import FCMDevice, UserCountNotification
from drf_spirit.utils import language_options
from forum.category.models import Category
from forum.topic.models import Topic, VBseen
from datetime import datetime, timedelta
import json

def run():	
	print('running')
	category = Category.objects.filter(parent__isnull=False)
	all_obj=FCMDevice.objects.filter(is_uninstalled=False)

	#all user group
	try:
		user=UserCountNotification.objects.get(language='0', user_group='0', category__isnull=True)
		user.no_of_user=all_obj.count()
		user.save()
	except Exception as e:
		user=UserCountNotification()
		user.user_group='0'
		user.no_of_user=all_obj.count()
		user.save()
	print('all user group')

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

	print('install and never sign up')

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

	print('Never Created A Video')
	#Never Seen a Video
	filter_list=VBseen.objects.distinct('user__pk').values_list('user__pk', flat=True)
	device_seen=all_obj.filter(user__isnull=False).exclude(user__pk__in=topics)
	try:
		user=UserCountNotification.objects.get(language='0', user_group='3')
		user.fcm_users=json.dumps(list(device_seen.values_list('id', flat=True)))
		user.no_of_user=device_seen.count()
		user.save()
	except:
		user=UserCountNotification()
		user.user_group='3'
		user.no_of_user=device_seen.count()
		user.fcm_users=json.dumps(list(device_seen.values_list('id', flat=True)))
		user.save()

	print('Never Seen a Video')
	#Signed up but no opening of app since 24 hours
	hours_ago=datetime.now()-timedelta(days=1) 
	device_seen_24_hour=all_obj.filter(user__isnull=False).exclude(start_time__gt=hours_ago)
	try:
		user=UserCountNotification.objects.get(language='0', user_group='4')
		user.fcm_users=json.dumps(list(device_seen_24_hour.values_list('id', flat=True)))
		user.no_of_user=device_seen_24_hour.count()
		user.save()
	except:
		user=UserCountNotification()
		user.user_group='4'
		user.no_of_user=device_seen_24_hour.count()
		user.fcm_users=json.dumps(list(device_seen_24_hour.values_list('id', flat=True)))
		user.save()

	print('Signed up but no opening of app since 72 hours')
	#Signed up but no opening of app since 72 hours
	hours_ago=datetime.now()-timedelta(days=2) 
	device_seen_72_hour=all_obj.filter(user__isnull=False).exclude(start_time__gt=hours_ago)
	try:
		user=UserCountNotification.objects.get(language='0', user_group='5')
		user.fcm_users=json.dumps(list(device_seen_72_hour.values_list('id', flat=True)))
		user.no_of_user=device_seen_72_hour.count()
		user.save()
	except:
		user=UserCountNotification()
		user.user_group='5'
		user.no_of_user=device_seen_72_hour.count()
		user.fcm_users=json.dumps(list(device_seen_72_hour.values_list('id', flat=True)))
		user.save()
	        
	print('Signed up but no opening of app since 24 hours')
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
		print(each_category.title)

	print('All Category')
	for each in language_options:
		if each[0] != '0':
			print('language ' + each[1])
			lang_ids=all_obj.filter(user__st__language=each[0])
			try:
				user=UserCountNotification.objects.get(language=each[0], user_group='0', category__isnull=True)
				user.fcm_users=json.dumps(list(lang_ids.values_list('id', flat=True)))
				user.no_of_user=lang_ids.count()
				user.save()
			except:
				user=UserCountNotification()
				user.user_group='0'
				user.language=each[0]
				user.fcm_users=json.dumps(list(lang_ids.values_list('id', flat=True)))
				user.no_of_user=lang_ids.count()
				user.save()
			for each_category in category:	
				print(each_category.title + ' - ' +each[1])
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
			try:
				user=UserCountNotification.objects.get(language=each[0], user_group='6')
				filter_list=device.filter(user__st__language=each[0])
				user.fcm_users=json.dumps(list(filter_list.values_list('id', flat=True)))
				user.no_of_user=filter_list.count()
				user.save()
			except:
				user=UserCountNotification()
				user.language=each[0]
				user.user_group='6'
				filter_list=device.filter(user__st__language=each[0])
				user.no_of_user=filter_list.count()
				user.fcm_users=json.dumps(list(filter_list.values_list('id', flat=True)))
				user.save()
			try:
				filter_list=device_seen.filter(user__st__language=each[0])
				user=UserCountNotification.objects.get(language=each[0], user_group='3')
				user.fcm_users=json.dumps(list(filter_list.values_list('id', flat=True)))
				user.no_of_user=device_seen.count()
				user.save()
			except:
				user=UserCountNotification()
				filter_list=device_seen.filter(user__st__language=each[0])
				user.user_group='3'
				user.language=each[0]
				user.no_of_user=filter_list.count()
				user.fcm_users=json.dumps(list(filter_list.values_list('id', flat=True)))
				user.save()
			try:
				user=UserCountNotification.objects.get(language=each[0], user_group='4')
				filter_list=device_seen_24_hour.filter(user__st__language=each[0])
				user.fcm_users=json.dumps(list(filter_list.values_list('id', flat=True)))
				user.no_of_user=filter_list.count()
				user.save()
			except:
				user=UserCountNotification()
				user.user_group='4'
				user.language=each[0]
				filter_list=device_seen_24_hour.filter(user__st__language=each[0])
				user.no_of_user=filter_list.count()
				user.fcm_users=json.dumps(list(filter_list.values_list('id', flat=True)))
				user.save()
			try:
				user=UserCountNotification.objects.get(language=each[0], user_group='5')
				filter_list=device_seen_72_hour.filter(user__st__language=each[0])
				user.fcm_users=json.dumps(list(filter_list.values_list('id', flat=True)))
				user.no_of_user=filter_list.count()
				user.save()
			except:
				user=UserCountNotification()
				user.user_group='5'
				user.language=each[0]
				filter_list=device_seen_72_hour.filter(user__st__language=each[0])
				user.no_of_user=filter_list.count()
				user.fcm_users=json.dumps(list(filter_list.values_list('id', flat=True)))
				user.save()
	print('done')




