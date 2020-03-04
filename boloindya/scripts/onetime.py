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

def put_hau_data():

	today = datetime.now()
	start_date = today + timedelta(days=-180)
	end_date = today
	for dt in rrule(rrule.DAILY, dtstart= start_date, until= today):
		curr_day = dt.day 
		curr_month = dt.month 
		curr_year = dt.year 
		str_curr_date = str(curr_year) + "-" + str(curr_month) + "-" + str(curr_day)






