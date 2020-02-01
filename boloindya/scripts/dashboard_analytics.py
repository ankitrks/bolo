# -*- coding: utf-8 -*-

from forum.user.models import AndroidLogs, VideoPlaytime, VideoCompleteRate, UserAppTimeSpend, ReferralCodeUsed, UserProfile
from drf_spirit.models import UserJarvisDump, UserLogStatistics, ActivityTimeSpend, VideoDetails,UserTimeRecord, UserVideoTypeDetails
from forum.topic.models import Topic
import time
import ast 
from django.http import JsonResponse
from drf_spirit.utils import language_options
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
from jarvis.models import DashboardMetrics

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
			curr_date = item.timestamp 
			curr_month = curr_date.month 
			curr_year = curr_date.year 
			curr_day = curr_date.day

			if(curr_date not in day_month_year_dict):
				day_month_year_dict[curr_date] = []
			else:
				day_month_year_dict[curr_date].append(curr_videoid)	

	
	print(day_month_year_dict)			
				
	"""				
	for key, val in day_month_year_dict.items():


	week_no = curr_date.isocalendar()[1]
	if(curr_year == 2020):
		week_no+=52
	else:
		week_no = 52

				
	metrics = '3'
	metrics_slab = '5'
	save_obj, created = DashboardMetrics.objects.get_or_create(metrics = metrics, metrics_slab = slab, date = month_date, week_no = week_no)
	"""	




def main():

	put_share_data()


def run():
	main()	