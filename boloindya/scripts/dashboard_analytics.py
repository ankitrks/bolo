# -*- coding: utf-8 -*-

from forum.user.models import AndroidLogs, VideoPlaytime, VideoCompleteRate, UserAppTimeSpend, ReferralCodeUsed, UserProfile
from drf_spirit.models import UserJarvisDump, UserLogStatistics, ActivityTimeSpend, VideoDetails,UserTimeRecord, UserVideoTypeDetails
from forum.topic.models import Topic, BoloActionHistory
from jarvis.models import FCMDevice
from django.db.models import Count
import time
import ast 
from django.http import JsonResponse
from drf_spirit.utils import language_options
import ast 
from dateutil import parser
import re
import datetime
from dateutil import rrule
from datetime import datetime, timedelta
import os 
import csv
import pytz 
import pandas as pd 
import dateutil.parser 
from django.db.models import Q
from django.db.models import Count, F, Value
local_tz = pytz.timezone("Asia/Kolkata")
import sys
import django
import random
from datetime import datetime
from calendar import monthrange
from jarvis.models import DashboardMetrics
from drf_spirit.utils import language_options
from django.db.models.functions import TruncDate, TruncHour


from datetime import timedelta
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )
from jarvis.models import DashboardMetrics, DashboardMetricsJarvis

language_string = list(language_options)
language_map = []
for (a,b) in language_string:
	language_map.append(str(b))

def print_dict(curr_dict):
	for key, val in curr_dict.items():
		print("key+val:", key, val)

def put_share_data():

	metrics = '3'
	metrics_slab = ''

	today = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
	start_date = today + timedelta(days = -1)

	day_month_year_dict = dict()
	try:
		all_data = UserVideoTypeDetails.objects.filter(timestamp__gt = start_date)
		for item in all_data:
			if(str(item.video_type) == 'shared'):
				curr_videoid = item.videoid 
				curr_month = item.timestamp.month 
				curr_year = item.timestamp.year
				curr_day = item.timestamp.day 
				curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day)
				#print(curr_date)

				if(curr_date not in day_month_year_dict):
					day_month_year_dict[curr_date] = []
					day_month_year_dict[curr_date].append(curr_videoid)
				else:
					day_month_year_dict[curr_date].append(curr_videoid)	

		#print(day_month_year_dict)						
		for key, val in day_month_year_dict.items():
			datetime_key = parser.parse(key)
			week_no = datetime_key.isocalendar()[1]
			curr_year = datetime_key.year 
			if(curr_year == 2020):
				week_no+=52
			if(curr_year == 2019 and week_no == 1):
				week_no = 52

			
			save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = key, week_no = week_no)
			if(created):
				print(metrics, metrics_slab, week_no, len(val))
				save_obj.count = len(val)
				save_obj.save()
			else:
				print(metrics, metrics_slab, week_no, len(val))
				save_obj.count = len(val)
				save_obj.save()	
	except Exception as e:
		print("Exception in Share data", e.message)			


def put_installs_data():
	end_date = 	datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
	start_date = end_date + timedelta(days=-2)

	try:
		#Calculate number of installs which have empty or None android_id
		empty_android_id_counts = ReferralCodeUsed.objects.filter(Q(created_at__gte=start_date, created_at__lte=end_date) & (Q(android_id='') | Q(android_id=None)))\
			.annotate(date=TruncDate('created_at'))\
			.values('date').order_by('date')\
			.annotate(total=Count('id'))

		#Calculate number of distinct non-empty android_id on a particular day
		non_empty_counts = ReferralCodeUsed.objects.filter(created_at__gte=start_date, created_at__lte=end_date)\
			.annotate(date=TruncDate('created_at'))\
			.values('date')\
			.order_by('date')\
			.annotate(total=Count('android_id', distinct=True))

		
		dict_empty_id_count = {}
		for each_day in empty_android_id_counts:
			dict_empty_id_count[each_day.get('date')] = each_day.get('total')
				

		#Sum up the count for installs having empty and non-empty ids
		total_install_count = {}
		for each_day in non_empty_counts:
			total_install_count[each_day.get('date')] = each_day.get('total')
			empty_id_count = dict_empty_id_count.get(each_day.get('date'))
			if empty_id_count:
				total_install_count[each_day.get('date')] += empty_id_count

		for current_day in total_install_count:
			week_no = current_day.isocalendar()[1]
			curr_year = current_day.year 
			if(curr_year == 2020):
				week_no+=52
			if(curr_year == 2019 and week_no == 1):
				week_no = 52

			save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = '5', metrics_slab = '6', date = current_day, week_no = week_no)
			save_obj.count = total_install_count[current_day]
			save_obj.save()
	except Exception as e:
		print("Exception in Installs data", e.message)					
						

def put_video_views_analytics():
	try:
		today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
		start_date = today + timedelta(days = -2)	
		end_date = today
		for dt in rrule.rrule(rrule.DAILY, dtstart= start_date, until= today):

			curr_day = dt.day 
			curr_month = dt.month 
			curr_year = dt.year
			all_data = AndroidLogs.objects.filter(log_type = 'click2play', created_at__day= curr_day, created_at__month= curr_month, created_at__year= curr_year)
			user_view_dict = []
			for item in all_data:
				try:
					log_data = ast.literal_eval(item.logs)
					for each in log_data:
						curr_state = each['state']
						if('StartPlaying' in curr_state):
							user_view_dict.append(each['video_byte_id'])
				except Exception as e:
					pass			

			#print(dt, len(user_view_dict),len(user_view_dict))
			week_no = dt.isocalendar()[1]
			curr_year = dt.year 
			str_date = str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day)
			if(curr_year == 2020):
				week_no+=52
			if(curr_year == 2019 and week_no == 1):
				week_no = 52		

				
			metrics = '1'
			metrics_slab = ''
			save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_date, week_no = week_no)
			if(created):
				print(metrics, metrics_slab, str_date, week_no, len(user_view_dict))
				save_obj.count = len(user_view_dict)
				save_obj.save()
			else:
				print(metrics, metrics_slab, str_date, week_no, len(user_view_dict))
				save_obj.count = len(user_view_dict)
				save_obj.save()	
	except Exception as e:
		print("Error in Video Views", e.message)			



def put_videos_created():
	try:
		today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
		start_date = today + timedelta(days = -2)

		day_month_year_dict = dict()
		all_data = Topic.objects.filter(date__gt = start_date)
		for item in all_data:
			curr_month = item.date.month 
			curr_year = item.date.year
			curr_day = item.date.day 
			curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day)
			curr_videoid = item.id
			print(curr_videoid)

			if(curr_date in day_month_year_dict):
				day_month_year_dict[curr_date].append(curr_videoid)
			else:
				day_month_year_dict[curr_date] = []
				day_month_year_dict[curr_date].append(curr_videoid)

		
		#print(len(day_month_year_dict))
		for key, val in day_month_year_dict.items():
			datetime_key = parser.parse(key)
			week_no = datetime_key.isocalendar()[1]
			curr_year = datetime_key.year 
			if(curr_year == 2020):
				week_no+=52
			if(curr_year == 2019 and week_no == 1):
				week_no = 52

			metrics = '0'
			metrics_slab = ''
			#print(metrics, metrics_slab, key, week_no, len(val))
			save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = key, week_no = week_no)
			if(created):
				print(metrics, metrics_slab, key, week_no, len(val))
				save_obj.count = len(val)
				save_obj.save()
			else:
				print(metrics, metrics_slab, key, week_no, len(val))
				save_obj.count = len(val)
				save_obj.save()
	except Exception as e:
		print("Error in videos created", e.message)			

		# save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = key, week_no = week_no)
		# if(created):
		# 	print(metrics, metrics_slab, key, week_no, len(val))
		# 	save_obj.count = len(val)
		# 	save_obj.save()


# put new video creators with lang filter
def put_video_creators_analytics_lang():


	today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	metrics = '4'
	start_date = today + timedelta(days = -2)
	end_date = today
	for dt in rrule.rrule(rrule.DAILY, dtstart = start_date, until = end_date):
		curr_day = dt.day 
		curr_month = dt.month
		curr_year = dt.year
		all_data = Topic.objects.filter(is_vb=True, date__day = curr_day, date__month = curr_month, date__year = curr_year).values('user', 'language_id', 'm2mcategory').annotate(vb_count=Count('pk', 'language_id')).order_by('-vb_count', 'language_id')
		#print(len(all_data))

		for item in all_data:
			userid = str(item['user'])
			language_id = str(item['language_id'])
			if(language_id in language_map):
				language_id = str(language_map.index(language_id))

			user_details = UserProfile.objects.get(user = userid)
			date_joined = user_details.user.date_joined
			
			if(item['m2mcategory']!=None): 
				tot_vb_count = int(item['vb_count'])
				category_id = int(item['m2mcategory'])
				str_date = str(date_joined.year) + "-" + str(date_joined.month) + "-" + str(date_joined.day)
				datetime_key = parser.parse(str_date)
				week_no = datetime_key.isocalendar()[1]
				curr_year_dt = datetime_key.year 
				if(curr_year_dt == 2020):
					week_no+=52
				if(curr_year_dt == 2019 and week_no == 1):
					week_no = 52

				#print(metrics, datetime_key, week_no, category_id, language_id)
					
				if(tot_vb_count>=60):
					metrics_slab = '2'
					save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = language_id, category_id = category_id)
					if(created):
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj.count = 1
						save_obj.save()
					else:
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj.count = F('count') + 1
						save_obj.save()

					save_obj_all, created_all = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = '0', category_id = category_id)
					if(created_all):
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj_all.count = 1
						save_obj_all.save()
					else:
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj_all.count = F('count') + 1
						save_obj_all.save()		

				if(tot_vb_count>=25 and tot_vb_count<=59):
					metrics_slab = '1'
					save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = language_id, category_id = category_id)
					if(created):
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj.count = 1
						save_obj.save()
					else:
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj.count = F('count') + 1
						save_obj.save()

					save_obj_all, created_all = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = '0', category_id = category_id)
					if(created_all):
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj_all.count = 1
						save_obj_all.save()
					else:
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj_all.count = F('count') + 1
						save_obj_all.save()			

				if(tot_vb_count>=5 and tot_vb_count<25):
					metrics_slab = '0'
					save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = language_id, category_id = category_id)
					if(created):
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj.count = 1
						save_obj.save()
					else:
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj.count = F('count') + 1
						save_obj.save()

					save_obj_all, created_all = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = '0', category_id = category_id)
					if(created_all):
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj_all.count = 1
						save_obj_all.save()
					else:
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj_all.count = F('count') + 1
						save_obj_all.save()

				if(tot_vb_count<5):
					metrics_slab = '9'
					save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = language_id, category_id = category_id)
					if(created):
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj.count = 1
						save_obj.save()
					else:
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj.count = F('count') + 1
						save_obj.save()

					save_obj_all, created_all = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = '0', category_id = category_id)
					if(created_all):
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj_all.count = 1
						save_obj_all.save()
					else:
						print(metrics, metrics_slab, datetime_key, week_no, 1)
						save_obj_all.count = F('count') + 1
						save_obj_all.save()			


# this function is not being used anymore, please do not edit this function and call it anywhere
def put_video_creators_analytics():

	today = datetime.now()
	start_date = today + timedelta(days = -150)

	slab_0_dict = dict()
	slab_1_dict = dict()
	slab_2_dict = dict()
	slab_3_dict = dict()

	all_data = Topic.objects.filter(is_vb=True, date__gt = start_date).values('user').annotate(vb_count=Count('pk')).order_by('-vb_count')
	print(len(all_data))
	for item in all_data:
		user_vb_count = int(item['vb_count'])
		user_id = item['user']
		user_details = UserProfile.objects.get(user = user_id)
		date_joined = user_details.user.date_joined
		curr_year = date_joined.year 
		curr_month = date_joined.month 
		curr_day = date_joined.day
		str_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day) 
		if(user_vb_count>=60):
			if(str_date in slab_3_dict):
				slab_3_dict[str_date].append(user_id)
			else:
				slab_3_dict[str_date] = []
				slab_3_dict[str_date].append(user_id)
		if(user_vb_count>=25 and user_vb_count<=59):
			if(str_date in slab_2_dict):
				slab_2_dict[str_date].append(user_id)
			else:
				slab_2_dict[str_date] = []
				slab_2_dict[str_date].append(user_id)
		if(user_vb_count>=5 and user_vb_count<=24):
			if(str_date in slab_1_dict):
				slab_1_dict[str_date].append(user_id)
			else:
				slab_1_dict[str_date] = []
				slab_1_dict[str_date].append(user_id)
		if(user_vb_count>0 and user_vb_count<5):
			if(str_date in slab_0_dict):
				slab_0_dict[str_date].append(user_id)
			else:
				slab_0_dict[str_date] = []
				slab_0_dict[str_date].append(user_id)	


	print(len(slab_1_dict), len(slab_2_dict), len(slab_3_dict), len(slab_0_dict))
	
	for key, val in slab_0_dict.items():
		datetime_key = parser.parse(key)
		week_no = datetime_key.isocalendar()[1]
		curr_year = datetime_key.year 
		if(curr_year == 2020):
			week_no+=52
		if(curr_year == 2019 and week_no == 1):
			week_no = 52

		metrics = '4'
		metrics_slab = ''

		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, datetime_key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()
		else:
			print(metrics, metrics_slab, datetime_key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()	


	for key, val in slab_1_dict.items():
		datetime_key = parser.parse(key)
		week_no = datetime_key.isocalendar()[1]
		curr_year = datetime_key.year
		if(curr_year == 2020):
			week_no+=52
		if(curr_year == 2019 and week_no == 1):
			week_no = 52

		metrics = '4'
		metrics_slab = '0'
		
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, datetime_key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()
		else:
			print(metrics, metrics_slab, datetime_key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()	


	for key, val in slab_2_dict.items():
		datetime_key = parser.parse(key)
		week_no = datetime_key.isocalendar()[1]
		curr_year = datetime_key.year 
		if(curr_year == 2020):
			week_no+=52
		if(curr_year == 2019 and week_no == 1):
			week_no = 52

		metrics = '4'
		metrics_slab = '1'
		

		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, datetime_key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()
		else:
			print(metrics, metrics_slab, datetime_key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()


	for key, val in slab_3_dict.items():
		datetime_key = parser.parse(key)
		week_no = datetime_key.isocalendar()[1]
		curr_year = datetime_key.year 
		if(curr_year == 2020):
			week_no+=52
		if(curr_year == 2019 and week_no == 1):
			week_no = 52

		metrics = '4'
		metrics_slab = '2'
		
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, datetime_key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()	
		else:
			print(metrics, metrics_slab, datetime_key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()			


def put_dau_data():
	try:
		end_date = 	datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
		start_date = end_date + timedelta(days=-2)

		for dt in rrule.rrule(rrule.DAILY, dtstart= start_date, until= end_date):
			#print(dt)
			curr_day = dt.day 
			curr_month = dt.month 
			curr_year = dt.year 
			str_curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day)

			null_data = ReferralCodeUsed.objects.filter((Q(android_id=None) | Q(android_id = '')) &  Q(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year))
			all_data = ReferralCodeUsed.objects.filter(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year)
			user_not_null_data = all_data.exclude(Q(android_id=None) | Q(android_id = '')).values_list('android_id', flat=True).distinct()

			id_list_2 = AndroidLogs.objects.filter(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year).values_list('user__pk', flat=True).distinct()
			id_list_3 = FCMDevice.objects.filter(user__pk__in = id_list_2).values_list('dev_id', flat = True).distinct()
			clist = set(list(id_list_3) + list(user_not_null_data))
			dau_count = len(clist) + null_data.count()

			week_no = dt.isocalendar()[1]
			if(curr_year == 2020):
				week_no+=52
			if(curr_year == 2019 and week_no == 1):
				week_no = 52

			metrics = '6'
			metrics_slab = ''
			
			save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_curr_date, week_no = week_no)
			save_obj.count = dau_count
			save_obj.save()
			print(metrics, str_curr_date, week_no, dau_count)
	except Exception as e:
		print("Error in dau calculation", e.message)


def put_mau_data():
	try:
		dt = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=-2)

		curr_month = dt.month
		curr_year = dt.year
		str_curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(01)
		
		null_data = ReferralCodeUsed.objects.filter((Q(android_id=None) | Q(android_id = '')) &  Q(created_at__month = curr_month, created_at__year = curr_year))
		all_data = ReferralCodeUsed.objects.filter(created_at__month = curr_month, created_at__year = curr_year)
		user_not_null_data = all_data.exclude(Q(android_id=None) | Q(android_id = '')).values_list('android_id', flat=True).distinct()

		id_list_2 = AndroidLogs.objects.filter(created_at__month = curr_month, created_at__year = curr_year).values_list('user__pk', flat=True).distinct()
		id_list_3 = FCMDevice.objects.filter(user__pk__in = id_list_2).values_list('dev_id', flat = True).distinct()
		clist = set(list(id_list_3) + list(user_not_null_data))
		mau_count = len(clist) + null_data.count()

		metrics = '8'
		metrics_slab = ''
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_curr_date)
		save_obj.count=mau_count
		save_obj.save()
		print(metrics, metrics_slab, str_curr_date, mau_count)
	except Exception as e:
		print("Error in Mau calculation", e.message)


# put daily combo view of (user, vid) to be put in daily records
def put_uniq_views_analytics():

	today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	start_date = today + timedelta(days = -2)	
	end_date = today
	for dt in rrule.rrule(rrule.DAILY, dtstart= start_date, until= today):
		#print(dt)
		curr_day = dt.day 
		curr_month = dt.month 
		curr_year = dt.year 
		str_date = str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day)
		all_data = AndroidLogs.objects.filter(log_type = 'click2play', created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year)
		print("len of logs", len(all_data))
		user_vid_mapping = dict()				# dict storing (user, vid) mapping for the day 
		for item in all_data:
			try:
				log_data = ast.literal_eval(item.logs)
				curr_userid = item.user_id 
				for each in log_data:
					curr_state = each['state']
					if('StartPlaying' in curr_state):
						if(curr_userid in user_vid_mapping):
							user_vid_mapping[curr_userid].append(each['video_byte_id'])
						else:
							user_vid_mapping[curr_userid] = []
							user_vid_mapping[curr_userid].append(each['video_byte_id'])					

			except Exception as e:
				pass

		tot_uniq_uvb_view_count = 0		
		for key, val in user_vid_mapping.items():
			tot_uniq_uvb_view_count+=len(set(val))

		week_no = dt.isocalendar()[1]
		curr_year = dt.year 
		str_date = str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day)
		if(curr_year == 2020):
			week_no+=52
		if(curr_year == 2019 and week_no == 1):
			week_no = 52

		
		metrics = '7'
		metrics_slab = ''
		print(metrics, metrics_slab, str_date, week_no, tot_uniq_uvb_view_count)	

		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_date, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, str_date, week_no, tot_uniq_uvb_view_count)
			save_obj.count = tot_uniq_uvb_view_count
			save_obj.save()
		else:
			print(metrics, metrics_slab, str_date, week_no, tot_uniq_uvb_view_count)	
			save_obj.count = tot_uniq_uvb_view_count
			save_obj.save()	

								
def put_total_video_creators():


	today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	start_date = today + timedelta(days = -2)
	end_date = today
	for dt in rrule.rrule(rrule.DAILY, dtstart = start_date, until = today):
		language_dict = dict()
		for item in language_options:
			language_dict[item[0]] = 0

		curr_day = dt.day 
		curr_month = dt.month 
		curr_year = dt.year
		str_date = str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day)
		all_data = Topic.objects.filter(is_vb = True, date__day = curr_day, date__month = curr_month, date__year = curr_year).values('user', 'pk', 'language_id', 'm2mcategory').order_by('user') 
		#print(len(all_data))
		for item in all_data:
			video_id = str(item['pk'])
			language_id = str(item['language_id'])
			userid = str(item['user'])
			if(item['m2mcategory']!=None):
				category_id = int(item['m2mcategory'])

				if(language_id in language_map):
					language_id = str(language_map.index(language_id))
					language_dict[language_id]+=1
					language_dict['0']+=1
				else:
					language_dict[language_id]+=1
					language_dict['0']+=1


				#print(language_dict)
				datetime_key = parser.parse(str_date)
				week_no = datetime_key.isocalendar()[1]
				curr_year_dt = datetime_key.year 
				if(curr_year_dt == 2020):
					week_no+=52
				if(curr_year_dt == 2019 and week_no == 1):
					week_no = 52

				metrics = '9'
				metrics_slab = ''

				save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_date, week_no = week_no, metrics_language_options = language_id, category_id = category_id)
				if(created):
					print(metrics, metrics_slab, str_date, week_no, language_id, category_id)
					save_obj.count = 1
					save_obj.save()
				else:
					print(metrics, metrics_slab, str_date, week_no, language_id, category_id)
					save_obj.count = F('count') + 1
					save_obj.save()

				save_obj_all, created_all = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_date, week_no = week_no, metrics_language_options = '0', category_id = category_id)
				if(created_all):
					print(metrics, metrics_slab, str_date, week_no, language_id, category_id)
					save_obj_all.count = 1
					save_obj_all.save()
				else:
					print(metrics, metrics_slab, str_date, week_no, language_id, category_id)
					save_obj_all.count = F('count') + 1
					save_obj_all.save()


def put_install_signup_conversion():

	today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
	start_date = today + timedelta(days = -2)
	end_date = today
	for dt in rrule.rrule(rrule.DAILY, dtstart = start_date, until = today):
		curr_day = dt.day 
		curr_month = dt.month
		curr_year = dt.year
		install_data = ReferralCodeUsed.objects.filter(by_user__isnull=False, created_at__day=curr_day, created_at__month = curr_month, created_at__year=curr_year).values_list('android_id', flat=True)
		signup_data = ReferralCodeUsed.objects.filter(by_user__isnull = False, created_at__day=curr_day, created_at__month = curr_month, created_at__year=curr_year).values_list('android_id', flat=True)
		install_signup = list(set(install_data) & set(signup_data))
		tot_count = len(install_signup)
		metrics = '10'
		metrics_slab = ''
		str_date = str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day)
		datetime_key = parser.parse(str_date)
		week_no = datetime_key.isocalendar()[1]
		curr_year_dt = datetime_key.year 
		if(curr_year_dt == 2020):
			week_no+=52
		if(curr_year_dt == 2019 and week_no == 1):
			week_no = 52

		#print(metrics, metrics_slab, str_date, week_no, tot_count)	
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_date, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, week_no, tot_count)
			save_obj.count = tot_count
			save_obj.save()
		else:
			print(metrics, metrics_slab, week_no, tot_count)
			save_obj.count = tot_count
			save_obj.save()

# this method is also not being used anywhere, do not call
def put_ratio_sessions_users():

	metrics = '11'
	metrics_slab = ''

	today = datetime.now()
	start_date = today + timedelta(days = -180)
	end_date = today 
	for dt in rrule.rrule(rrule.DAILY, dtstart = start_date, until = today):
		curr_day = dt.day 
		curr_month = dt.month
		curr_year = dt.year
		tot_session_records = 0
		tot_user_list = []
		str_date = str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day)
		datetime_key = parser.parse(str_date)
		week_no = datetime_key.isocalendar()[1]
		curr_year_dt = datetime_key.year 
		if(curr_year_dt == 2020):
			week_no+=52
		if(curr_year_dt == 2019 and week_no == 1):
			week_no = 52

		all_traction_data = UserJarvisDump.objects.filter(sync_time__day = curr_day, sync_time__month = curr_month, sync_time__year = curr_year, dump_type = 1)
		for user_jarvis in all_traction_data:
			user_data_string = user_jarvis.dump
			user_data_dump = ast.literal_eval(user_data_string)
			if('user_id' in user_data_dump):
				userid = user_data_dump['user_id']
				tot_user_list.append(userid)

			if('session_start_time' in user_data_dump):
				tot_session_records+=1
			
		tot_user_set = set(tot_user_list)
		tot_user_set_count = float(len(tot_user_set))
		if(tot_user_set_count>0):
			session_user_ratio = float(float(tot_session_records)/float(tot_user_set_count))
			#print(dt, session_user_ratio)
			save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_date, week_no = week_no)
			if(created):
				print(metrics, metrics_slab, week_no, session_user_ratio)
				save_obj.count = session_user_ratio
				save_obj.save()
			else:
				print(metrics, metrics_slab, week_no, session_user_ratio)
				save_obj.count = F('count') + session_user_ratio
				save_obj.save()
					


def put_uninstall_data():

	metrics = '11'
	metrics_slab = ''

	dt = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=-2)
	start_dt = dt.replace(hour=0, minute=0, second=0)
	end_dt = dt.replace(hour=23, minute=59, second=59)

	tot_records = FCMDevice.objects.filter(device_type='1', is_uninstalled=True, uninstalled_date__gte=start_dt, uninstalled_date__lte = end_dt)\
		.annotate(at_hour=TruncHour('uninstalled_date'))\
		.values('at_hour')\
		.order_by('at_hour')\
		.annotate(total=Count('id'))

	week_no = dt.isocalendar()[1]
	if(dt.year == 2020):
		week_no+=52
	if(dt.year == 2019 and week_no == 1):
		week_no = 52

	for each_hour in tot_records:
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = each_hour['at_hour'], week_no = week_no)
		save_obj.count = each_hour['total']
		save_obj.save()
		print(metrics, each_hour['at_hour'], each_hour['total'])


def put_views_data():
	to_date = datetime.today()
	from_date = to_date.replace(hour=0, minute=0, second=0)+timedelta(days=-1)
	for start_of_day in rrule.rrule(rrule.DAILY, dtstart= from_date, until= to_date):
		end_of_day = start_of_day.replace(hour=23, minute=59, second=59)
		total_views_data = VideoPlaytime.objects.filter(timestamp__gte=start_of_day, timestamp__lte=end_of_day)

		#Calculating both unique and non-unique video views
		all_counts = total_views_data.values('video__id', 'video__m2mcategory', 'video__language_id')\
			.annotate(unique_count=Count('user', distinct=True), non_unique_count=Count('user'))

		count_dict={}

		for each_vid in all_counts:
			lang_id = each_vid['video__language_id']
			categ_id = each_vid['video__m2mcategory']

			if categ_id not in count_dict:
				count_dict[categ_id] = {}
			if lang_id not in count_dict[categ_id]:
				count_dict[categ_id][lang_id]  = {'non_unique_count':0, 'unique_count':0}

			count_dict[categ_id][lang_id]['non_unique_count'] += each_vid['non_unique_count']
			count_dict[categ_id][lang_id]['unique_count'] += each_vid['unique_count']

		week_no = start_of_day.isocalendar()[1]
		curr_year = start_of_day.year 
		str_date = str(start_of_day.year) + "-" + str(start_of_day.month) + "-" + str(start_of_day.day)
		if(curr_year == 2020):
			week_no+=52
		if(curr_year == 2019 and week_no == 1):
			week_no = 52

		for each_categ in count_dict:
			for each_lang in count_dict[each_categ]:
				unique_count = count_dict[each_categ][each_lang]['unique_count']
				non_unique_count = count_dict[each_categ][each_lang]['non_unique_count']

				categ_id = ''
				if each_categ:
					categ_id = (int)(each_categ)

				#Save unique count
				save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = '7', metrics_slab = '', date = str_date, week_no = week_no, metrics_language_options=each_lang, category_id=each_categ)
				save_obj.count=unique_count
				save_obj.save()

				#Save non-unique count
				save_obj_1, created_1 = DashboardMetricsJarvis.objects.get_or_create(metrics = '1', metrics_slab = '', date = str_date, week_no = week_no, metrics_language_options=each_lang, category_id=each_categ)
				save_obj_1.count=non_unique_count
				save_obj_1.save()

				print(vars(save_obj))
				print(vars(save_obj_1))

def main():

	put_share_data()
	put_installs_data()
	put_dau_data()
	put_mau_data()
	put_video_views_analytics()
	put_videos_created()
	put_uniq_views_analytics()
	put_total_video_creators()
	put_video_creators_analytics_lang()
	put_install_signup_conversion()
	put_uninstall_data()
	put_views_data()
	

def run():
	main()	
	
