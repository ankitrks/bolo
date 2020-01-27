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

language_string = list(language_options)
language_map = []
for (a,b) in language_string:
	language_map.append(b)


def convert_data_csv(month_year_dict, filename):

	print(month_year_dict)

	f = open(filename, 'w')
	month_name = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
	w = csv.writer(f)
	w.writerow(['Month-Year', 'Language', 'Count'])
	for key, val in month_year_dict.items():
		writer = csv.writer(f)
		curr_name = month_name[int(key[0])-1]
		writer.writerow([curr_name + str(key[1]), str(key[2]), val])

	f.close()	



def like_count():
	all_data = UserVideoTypeDetails.objects.all()
	month_year_dict = dict()
	for item in all_data:
		if(str(item.video_type) == 'liked'):
			#print(item)
			curr_videoid = item.videoid 
			curr_date = item.timestamp
			curr_month = curr_date.month 
			curr_year = curr_date.year 
			lang_details = Topic.objects.all().filter(id = curr_videoid)
			for val in lang_details:
				lang_id = val.language_id 

			language_str = language_map[int(lang_id)-1]	
			if((curr_month, curr_year, language_str) not in month_year_dict):
				month_year_dict[(curr_month, curr_year, language_str)] = 1
			else:
				month_year_dict[(curr_month, curr_year, language_str)]+=1

	
	#print(month_year_dict)				
	convert_data_csv(month_year_dict, 'data_like.csv')

def share_count():
	all_data = UserVideoTypeDetails.objects.all()
	month_year_dict = dict()
	for item in all_data:
		if(str(item.video_type) == 'shared'):
			#print(item)
			curr_videoid = item.videoid 
			curr_date = item.timestamp
			curr_month = curr_date.month 
			curr_year = curr_date.year 
			lang_details = Topic.objects.all().filter(id = curr_videoid)
			for val in lang_details:
				lang_id = val.language_id 

			language_str = language_map[int(lang_id)-1]	
			if((curr_month, curr_year, language_str) not in month_year_dict):
				month_year_dict[(curr_month, curr_year, language_str)] = 1
			else:
				month_year_dict[(curr_month, curr_year, language_str)]+=1

	
	#print(month_year_dict)				
	convert_data_csv(month_year_dict, 'data_shared.csv')

def comment_count():
	all_data = UserVideoTypeDetails.objects.all()
	month_year_dict = dict()
	for item in all_data:
		if(str(item.video_type) == 'commented'):
			#print(item)
			curr_videoid = item.videoid 
			curr_date = item.timestamp
			curr_month = curr_date.month 
			curr_year = curr_date.year 
			lang_details = Topic.objects.all().filter(id = curr_videoid)
			for val in lang_details:
				lang_id = val.language_id 

			language_str = language_map[int(lang_id)-1]	
			if((curr_month, curr_year, language_str) not in month_year_dict):
				month_year_dict[(curr_month, curr_year, language_str)] = 1
			else:
				month_year_dict[(curr_month, curr_year, language_str)]+=1

	
	#print(month_year_dict)				
	convert_data_csv(month_year_dict, 'data_commented.csv')

def main():
	like_count()
	share_count()
	comment_count()


def run():
	main()
