from forum.user.models import AndroidLogs, VideoPlaytime, VideoCompleteRate, UserAppTimeSpend, ReferralCodeUsed, UserProfile
from drf_spirit.models import UserJarvisDump, UserLogStatistics, ActivityTimeSpend, VideoDetails,UserTimeRecord, UserVideoTypeDetails
from forum.topic.models import Topic, BoloActionHistory
from jarvis.models import FCMDevice
from django.db.models import Count, Sum
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
from django.db.models.functions import TruncDate
import json
import phonenumbers
import csv
from phonenumbers import carrier
from phonenumbers import geocoder


from datetime import timedelta
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]))

def run():
    all_data = UserProfile.objects.filter((~Q(mobile_no=None) & ~Q(mobile_no='')))
    for each_obj in all_data:
        try:
            ph = phonenumbers.parse(each_obj.mobile_no, "IN")
            isValidNum = phonenumbers.is_valid_number(ph)
            if isValidNum:
                each_obj.mobile_no = str(ph.national_number)
                each_obj.country_code = str(ph.country_code)
                print(each_obj.mobile_no, each_obj.country_code)
                # each_obj.save()

        except Exception as e:
            print(e)

run()
