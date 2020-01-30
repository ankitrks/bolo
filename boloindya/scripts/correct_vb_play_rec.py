from forum.user.models import AndroidLogs, VideoPlaytime, VideoCompleteRate, UserAppTimeSpend
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
import dateutil.parser 
local_tz = pytz.timezone("Asia/Kolkata")
import sys
import django
from datetime import timedelta
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )
from jarvis.models import DashboardMetrics


def parse_duration(time):

	string_dist = time.split(":")
	mins = int(string_dist[0])
	seconds = int(string_dist[1])
	time = mins*60 + seconds
	return int(time)


def main():
	all_data = VideoPlaytime.objects.all()
	for item in all_data:
		curr_userid = item.user 
		curr_videoid = item.videoid
		curr_playtime = item.playtime
		media_details = Topic.objects.all().filter(id=curr_videoid)
		tot_playtime = media_details[0].media_duration 
		tot_playtime_sec = parse_duration(tot_playtime)
		if(curr_playtime>tot_playtime_sec):
			print(tot_playtime_sec, curr_userid, curr_videoid)
			VideoPlaytime.objects.filter(user = curr_userid, videoid=curr_videoid).update(playtime = tot_playtime_sec)
		else:
			print("no")	

def run():
	main()