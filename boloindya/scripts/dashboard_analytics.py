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

	today = datetime.now()
	start_date = today + timedelta(days = -1)

	day_month_year_dict = dict()
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

		metrics = '3'
		metrics_slab = ''
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = key, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()
		else:
			print(metrics, metrics_slab, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()	


def  put_installs_data():

	today = datetime.now()
	start_date = today + timedelta(days = -1)

	user_install_dict = dict()
	all_data = ReferralCodeUsed.objects.filter(by_user__isnull = True, created_at__gt = start_date)
	for item in all_data:
		curr_userid = str(item.android_id)
		curr_month = item.created_at.month 
		curr_year = item.created_at.year
		curr_day = item.created_at.day 
		curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day)
		#print(curr_date, curr_userid)

		if((curr_date in user_install_dict)):
			user_install_dict[curr_date].append(curr_userid)
		else:
			user_install_dict[curr_date] = []
			user_install_dict[curr_date].append(curr_userid)		 
	

	#print(user_install_dict, len(user_install_dict))
	for key, val in user_install_dict.items():
		datetime_key = parser.parse(key)
		week_no = datetime_key.isocalendar()[1]
		curr_year = datetime_key.year 
		if(curr_year == 2020):
			week_no+=52
		if(curr_year == 2019 and week_no == 1):
			week_no = 52

		metrics = '5'
		metrics_slab = '6'
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = key, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, key, week_no)
			save_obj.count = len(val)
			save_obj.save()
		else:
			print(metrics, metrics_slab, key, week_no)
			save_obj.count = len(val)
			save_obj.save()	
	

def put_video_views_data():

	today = datetime.now()
	start_date = today + timedelta(days = -1)

	day_month_year_dict = dict()
	all_data = VideoPlaytime.objects.filter(timestamp__gt = start_date)
	for item in all_data:
		curr_videoid = item.videoid
		curr_month = item.timestamp.month 
		curr_year = item.timestamp.year
		curr_day = item.timestamp.day 
		curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day)

		if((curr_date in day_month_year_dict)):
			day_month_year_dict[curr_date].append(curr_videoid)
		else:
			day_month_year_dict[curr_date] = []

	print(len(day_month_year_dict))
	for key, val in day_month_year_dict.items():
		datetime_key = parser.parse(key)
		week_no = datetime_key.isocalendar()[1]
		curr_year = datetime_key.year
		if(curr_year == 2020):
			week_no+=52
		if(curr_year == 2019 and week_no == 1):
			week_no = 52

		metrics = '1'
		metrics_slab = ''
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = key, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()

		metrics_uniq = '7'
		metrics_slab_uniq = ''	
		save_obj_uniq, created_uniq = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics_uniq, metrics_slab = metrics_slab_uniq, date = key, week_no= week_no)
		if(created_uniq):
			print(metrics_uniq, metrics_slab_uniq, key, week_no, len(set(val)))
			save_obj_uniq.count = len(set(val))
			save_obj_uniq.save()

def put_video_views_analytics():

	today = datetime.now()
	start_date = today + timedelta(days = -1)	
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

		metrics = '7'
		metrics_slab = ''
		
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_date, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, str_date, week_no, len(set(user_view_dict)))
			save_obj.count = len(set(user_view_dict))
			save_obj.save()
		else:
			print(metrics, metrics_slab, str_date, week_no, len(set(user_view_dict)))	
			save_obj.count = len(set(user_view_dict))
			save_obj.save()





def put_videos_created():

	today = datetime.now()
	start_date = today + timedelta(days = -1)

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

		# save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = key, week_no = week_no)
		# if(created):
		# 	print(metrics, metrics_slab, key, week_no, len(val))
		# 	save_obj.count = len(val)
		# 	save_obj.save()


# number of video creators split according to date of signup and distributed into various slabs
def put_video_creators():

	today = datetime.now()
	start_date = today + timedelta(days = -1)

	user_signup_dict = dict()
	signup_data = ReferralCodeUsed.objects.filter(by_user__isnull = False, created_at__gt = start_date)
	for item in signup_data:
		curr_userid = item.by_user.id 
		user_signup_dict[curr_userid] = item.created_at 

	print(len(user_signup_dict))
	slab_1_dict = dict()
	slab_2_dict = dict()
	slab_3_dict = dict()

	for key, val in user_signup_dict.items():
		curr_userid = key
		all_data = Topic.objects.all().filter(user = curr_userid)

		user_lang_dict = dict()
		for lang in language_map:
			user_lang_dict[lang] = 0

		if(len(all_data)>0):
			for val_iter in all_data:
				if(val_iter.language_id.isdigit()):
					user_lang_dict[language_map[int(val_iter.language_id)-1]]+=1
				else:
					user_lang_dict[str(val_iter.language_id)]+=1	

			str_date = str(user_signup_dict[curr_userid].year) + "-" + str(user_signup_dict[curr_userid].month) + "-" + str(user_signup_dict[curr_userid].day)
			#print(str_date)

			tot_video_upload_count = 0
			for key_lang, val_lang in user_lang_dict.items():
				tot_video_upload_count+=int(val_lang)
			

			# distribute into slabs
			print(tot_video_upload_count)
			if(tot_video_upload_count>=60):
				if(str_date in slab_3_dict):
					slab_3_dict[str_date].append(curr_userid)
				else:
					slab_3_dict[str_date] = []
					slab_3_dict[str_date].append(curr_userid)

			if(tot_video_upload_count>=25 and tot_video_upload_count<60):
				if(str_date in slab_2_dict):
					slab_2_dict[str_date].append(curr_userid)
				else:
					slab_2_dict[str_date] = []
					slab_2_dict[str_date].append(curr_userid)

			if(tot_video_upload_count>=5 and tot_video_upload_count<25):
				if(str_date in slab_1_dict):
					slab_1_dict[str_date].append(curr_userid)
				else:
					slab_1_dict[str_date] = []
					slab_1_dict[str_date].append(curr_userid)
					
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
						

# put new video creators with lang filter
def put_video_creators_analytics_lang():

	uset = []

	today = datetime.now()
	metrics = '4'
	start_date = today + timedelta(days = -150)
	end_date = today
	for dt in rrule.rrule(rrule.DAILY, dtstart = start_date, until = end_date):
		curr_day = dt.day 
		curr_month = dt.month
		curr_year = dt.year
		all_data = Topic.objects.filter(is_vb=True, date__day = curr_day, date__month = curr_month, date__year = curr_year).values('user', 'language_id').annotate(vb_count=Count('pk', 'language_id')).order_by('-vb_count', 'language_id')
		#print(len(all_data))

		for item in all_data:
			userid = str(item['user'])
			language_id = str(item['language_id'])
			if(language_id in language_map):
				language_id = str(language_map.index(language_id))

			user_details = UserProfile.objects.get(user = userid)
			date_joined = user_details.user.date_joined
			tot_vb_count = int(item['vb_count'])
			#print(tot_vb_count)
			#print(date_joined)
			str_date = str(date_joined.year) + "-" + str(date_joined.month) + "-" + str(date_joined.day)
			datetime_key = parser.parse(str_date)
			week_no = datetime_key.isocalendar()[1]
			curr_year_dt = datetime_key.year 
			if(curr_year_dt == 2020):
				week_no+=52
			if(curr_year_dt == 2019 and week_no == 1):
				week_no = 52

			uset.append(str_date)

			if(tot_vb_count>=60):
				metrics_slab = '2'
				save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = language_id)
				if(created):
					print(metrics, metrics_slab, datetime_key, week_no, 1)
					save_obj.count = 1
					save_obj.save()
				else:
					print(metrics, metrics_slab, datetime_key, week_no, 1)
					save_obj.count = F('count') + 1
					save_obj.save()

				save_obj_all, created_all = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = '0')
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
				save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = language_id)
				if(created):
					print(metrics, metrics_slab, datetime_key, week_no, 1)
					save_obj.count = 1
					save_obj.save()
				else:
					print(metrics, metrics_slab, datetime_key, week_no, 1)
					save_obj.count = F('count') + 1
					save_obj.save()

				save_obj_all, created_all = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = '0')
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
				save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = language_id)
				if(created):
					print(metrics, metrics_slab, datetime_key, week_no, 1)
					save_obj.count = 1
					save_obj.save()
				else:
					print(metrics, metrics_slab, datetime_key, week_no, 1)
					save_obj.count = F('count') + 1
					save_obj.save()

				save_obj_all, created_all = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = '0')
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
				save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = language_id)
				if(created):
					print(metrics, metrics_slab, datetime_key, week_no, 1)
					save_obj.count = 1
					save_obj.save()
				else:
					print(metrics, metrics_slab, datetime_key, week_no, 1)
					save_obj.count = F('count') + 1
					save_obj.save()

				save_obj_all, created_all = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = datetime_key, week_no = week_no, metrics_language_options = '0')
				if(created_all):
					print(metrics, metrics_slab, datetime_key, week_no, 1)
					save_obj_all.count = 1
					save_obj_all.save()
				else:
					print(metrics, metrics_slab, datetime_key, week_no, 1)
					save_obj_all.count = F('count') + 1
					save_obj_all.save()			



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

	today = datetime.today()
	start_date = today + timedelta(days = -1)	
	end_date = today
	for dt in rrule.rrule(rrule.DAILY, dtstart= start_date, until= today):
		#print(dt)
		curr_day = dt.day 
		curr_month = dt.month 
		curr_year = dt.year 
		str_curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day)

		null_data = ReferralCodeUsed.objects.filter((Q(android_id=None) | Q(android_id = '')) &  Q(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year))
		all_data = ReferralCodeUsed.objects.filter(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year)
		user_null_data = all_data.exclude(Q(android_id=None) | Q(android_id = '')).values_list('android_id', flat=True)
		# not_null_data = all_data.exclude((Q(android_id=None) | Q(android_id = '')) & Q(android_id__in=user_null_data))
		# id_list_1 = not_null_data.values_list('by_user', flat = True)
		id_list_2 = AndroidLogs.objects.filter(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year).values_list('user__pk', flat=True)
		id_list_3 = FCMDevice.objects.filter(user__pk__in = id_list_2).values_list('dev_id', flat = True)
		clist = set(list(id_list_3) + list(user_null_data))
		dau_count = len(clist) + null_data.count()
		print(dau_count)


		#print(id_list_1.count(), id_list_2.count())
		#id_list_concat = list(id_list_1) + list(id_list_2)

		#print(dt, len(set(id_list_concat)) + null_data.count())

		# tot_data = ReferralCodeUsed.objects.filter(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year, by_user__isnull = True)
		# install_data = ReferralCodeUsed.objects.filter(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year, by_user__isnull = False)
		# #tot_data = ReferralCodeUsed.objects.filter(created_at__contains = str_curr_date, by_user__isnull = True)
		# #install_data = ReferralCodeUsed.objects.filter(created_at__contains = str_curr_date, by_user__isnull = False)
		# excluded_data = tot_data.exclude(android_id__in = install_data.values_list('android_id', flat = True))
		# #print(len(excluded_data))
		# excluded_data_list = excluded_data.values_list('by_user', flat = True)
		# android_data = AndroidLogs.objects.filter(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year)

		# temp_data = android_data.exclude(user__in = install_data.values_list('by_user', flat = True))
		# dau_count = temp_data.distinct('user').count() + tot_data.count()
		# print("date, count", dt, dau_count)


		week_no = dt.isocalendar()[1]
		if(curr_year == 2020):
			week_no+=52
		if(curr_year == 2019 and week_no == 1):
			week_no = 52

		metrics = '6'
		metrics_slab = ''
		print(metrics, metrics_slab, str_curr_date, week_no, dau_count)

		# t1 = ReferralCodeUsed.objects.filter(created_at__day= curr_day, created_at__month= curr_month, created_at__year= curr_year, by_user__isnull = True).count()
		# t2 = AndroidLogs.objects.filter(created_at__day= curr_day, created_at__month= curr_month, created_at__year= curr_year).distinct('user').count()
		# tot_count = t1 + t2
		
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_curr_date, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, str_curr_date, week_no, dau_count)
			save_obj.count = dau_count
			save_obj.save()
		else:
			print(metrics, metrics_slab, str_curr_date, week_no, dau_count)
			save_obj.count = dau_count
			save_obj.save()	           


def put_mau_data():

	today = datetime.today()
	start_date = today + timedelta(days = -2)	
	end_date = today
	for dt in rrule.rrule(rrule.DAILY, dtstart= start_date, until= today):
		curr_month = dt.month
		curr_year = dt.year
		curr_day = dt.day 
		str_curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(01)
		null_data = ReferralCodeUsed.objects.filter((Q(android_id=None) | Q(android_id = '')) &  Q(created_at__month = curr_month, created_at__year = curr_year))
		all_data = ReferralCodeUsed.objects.filter(created_at__month = curr_month, created_at__year = curr_year)
		user_null_data = all_data.exclude(Q(android_id=None) | Q(android_id = '')).values_list('android_id', flat=True)
		# not_null_data = all_data.exclude((Q(android_id=None) | Q(android_id = '')) & Q(android_id__in=user_null_data))
		# id_list_1 = not_null_data.values_list('by_user', flat = True)
		id_list_2 = AndroidLogs.objects.filter(created_at__month = curr_month, created_at__year = curr_year).values_list('user__pk', flat=True)
		id_list_3 = FCMDevice.objects.filter(user__pk__in = id_list_2).values_list('dev_id', flat = True)
		clist = set(list(id_list_3) + list(user_null_data))
		mau_count = len(clist) + null_data.count()
		#print(str_curr_date, mau_count)

		metrics = '8'
		metrics_slab = ''
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_curr_date)
		if(created):
			print(metrics, metrics_slab, str_curr_date, mau_count)
			save_obj.count = mau_count
			save_obj.save()
		else:
			print(metrics, metrics_slab, str_curr_date, mau_count)
			save_obj.count = mau_count
			save_obj.save()	   



# put daily combo view of (user, vid) to be put in daily records
def put_uniq_views_analytics():

	today = datetime.now()
	start_date = today + timedelta(days = -1)	
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


	today = datetime.now()
	start_date = today + timedelta(days = -150)
	end_date = today
	for dt in rrule.rrule(rrule.DAILY, dtstart = start_date, until = today):
		language_dict = dict()
		for item in language_options:
			language_dict[item[0]] = 0

		curr_day = dt.day 
		curr_month = dt.month 
		curr_year = dt.year
		str_date = str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day)
		all_data = Topic.objects.filter(is_vb = True, date__day = curr_day, date__month = curr_month, date__year = curr_year).values('user', 'pk', 'language_id').order_by('user') 
		#print(len(all_data))
		for item in all_data:
			video_id = str(item['pk'])
			language_id = str(item['language_id'])
			userid = str(item['user'])
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
		curr_year = datetime_key.year 
		if(curr_year == 2020):
			week_no+=52
		if(curr_year == 2019 and week_no == 1):
			week_no = 52

		metrics = '9'
		metrics_slab = ''

		for each in language_dict.items():
			save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = str_date, week_no = week_no, metrics_language_options = str(each[0]))
			if(created):
				print(metrics, metrics_slab, str_date, week_no, str(each[0]), each[1])
				save_obj.count = each[1]
				save_obj.save()	
			else:
				print(metrics, metrics_slab, datetime_key, week_no, str(each[0]), each[1])
				save_obj.count = each[1]
				save_obj.save()	


			#print(metrics, metrics_slab, str_date, week_no, each[0],each[1])



		
def main():

	# put_share_data()
	# put_installs_data()
	# put_dau_data()
	# put_mau_data()
	#put_video_creators_analytics()
	# put_video_views_analytics()
	# put_videos_created()
	# put_uniq_views_analytics()
	#put_total_video_creators()
	put_video_creators_analytics_lang()

	

def run():
	main()	
	
