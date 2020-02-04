# -*- coding: utf-8 -*-

from forum.user.models import AndroidLogs, VideoPlaytime, VideoCompleteRate, UserAppTimeSpend, ReferralCodeUsed, UserProfile
from drf_spirit.models import UserJarvisDump, UserLogStatistics, ActivityTimeSpend, VideoDetails,UserTimeRecord, UserVideoTypeDetails
from forum.topic.models import Topic
import time
import ast 
from django.http import JsonResponse
from drf_spirit.utils import language_options
from dateutil import parser
import re
import datetime
from datetime import datetime
import os 
import csv
import pytz 
import pandas as pd 
import dateutil.parser 
local_tz = pytz.timezone("Asia/Kolkata")
import sys
import django
import random
from datetime import datetime
from calendar import monthrange
from jarvis.models import DashboardMetrics
from datetime import timedelta
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )
from jarvis.models import DashboardMetrics, DashboardMetricsJarvis

language_string = list(language_options)
language_map = []
for (a,b) in language_string:
	language_map.append(str(b))


def put_share_data():

	day_month_year_dict = dict()
	all_data = UserVideoTypeDetails.objects.all()
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
			else:
				day_month_year_dict[curr_date].append(curr_videoid)	

	print(day_month_year_dict)						
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
		#print(metrics, metrics_slab, key, week_no, len(val))
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = key, week_no = week_no)
		if(created):
			print(metrics, metrics_slab, key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()


def put_installs_data():

	user_install_dict = dict()
	all_data = ReferralCodeUsed.objects.filter(by_user__isnull = True)
	for item in all_data:
		curr_userid = str(item.android_id)
		curr_month = item.created_at.month 
		curr_year = item.created_at.year
		curr_day = item.created_at.day 
		curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day)
		#print(curr_date, curr_userid)

		if((curr_date in user_install_dict)):
			if(curr_userid!='' and curr_userid!='None'):
				user_install_dict[curr_date].append(curr_userid)
		else:
			user_install_dict[curr_date] = []		 
	

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
		save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = key, week_no= week_no)
		if(created):
			print(metrics, metrics_slab, key, week_no, len(val))
			save_obj.count = len(val)
			save_obj.save()
	

def put_video_views_data():

	day_month_year_dict = dict()
	all_data = VideoPlaytime.objects.all()
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

		#metrics = '1'
		#metrics_slab = ''
		#print(metrics, metrics_slab, key, week_no, len(val))
		# save_obj, created = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics, metrics_slab = metrics_slab, date = key, week_no = week_no)
		# if(created):
		# 	print(metrics, metrics_slab, key, week_no, len(val))
		# 	save_obj.count = len(val)
		# 	save_obj.save()

		metrics_uniq = '7'
		metrics_slab_uniq = ''	
		save_obj_uniq, created_uniq = DashboardMetricsJarvis.objects.get_or_create(metrics = metrics_uniq, metrics_slab = metrics_slab_uniq, date = key, week_no= week_no)
		if(created_uniq):
			print(metrics_uniq, metrics_slab_uniq, key, week_no, len(set(val)))
			save_obj_uniq.count = len(set(val))
			save_obj_uniq.save()



def put_videos_created():

	day_month_year_dict = dict()
	all_data = Topic.objects.all()
	for item in all_data:
		curr_month = item.date.month 
		curr_year = item.date.year
		curr_day = item.date.day 
		curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day)
		curr_videoid = item.id

		if(curr_date in day_month_year_dict):
			day_month_year_dict[curr_date].append(curr_videoid)
		else:
			day_month_year_dict[curr_date] = []

	
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


# number of video creators split according to date of signup and distributed into various slabs
def put_video_creators():

	user_signup_dict = dict()
	signup_data = ReferralCodeUsed.objects.filter(by_user__isnull = False)
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

	print(slab_1_dict)
	print("\n\n")
	print(slab_2_dict)
	print("\n\n")
	print(slab_3_dict)				
					
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
		print(metrics, metrics_slab, datetime_key, week_no, len(val))

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
		print(metrics, metrics_slab, datetime_key, week_no, len(val))

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
		print(metrics, metrics_slab, datetime_key, week_no, len(val))						

	

def main():

	#put_share_data()
	#put_installs_data()
	#put_videos_created()
	#put_video_views_data()
	put_video_creators()

def run():
	main()	