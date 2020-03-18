# -*- coding: utf-8 -*-

# this is a one-time script for recording and updating the fields and values in DashBoardMetricsJarvis table
# Not intended to be run as a cron script at all.

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

def put_hau_data():

	today = datetime.now()
	start_date = today + timedelta(days=-150)
	end_date = today
	for dt in rrule.rrule(rrule.DAILY, dtstart= start_date, until= end_date):
		curr_day = dt.day 
		curr_month = dt.month 
		curr_year = dt.year 
		str_curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day)
		for curr_hour in range(0, 23):
			null_data = ReferralCodeUsed.objects.filter((Q(android_id=None) | Q(android_id = '')) &  Q(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year, created_at__hour = curr_hour))
			all_data = ReferralCodeUsed.objects.filter(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year, created_at__hour = curr_hour)
			user_null_data = all_data.exclude(Q(android_id=None) | Q(android_id = '')).values_list('android_id', flat=True)
			id_list_2 = AndroidLogs.objects.filter(created_at__day = curr_day, created_at__month = curr_month, created_at__year = curr_year, created_at__hour = curr_hour).values_list('user__pk', flat=True)
			id_list_3 = FCMDevice.objects.filter(user__pk__in = id_list_2).values_list('dev_id', flat = True)
			clist = set(list(id_list_3) + list(user_null_data))
			hau_count = len(clist) + null_data.count()
			print(dt, curr_hour, hau_count)


def main():
	put_hau_data()

def run():
	main()

