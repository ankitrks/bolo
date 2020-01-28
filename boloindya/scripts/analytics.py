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
	language_map.append(str(b))


def convert_data_csv(month_year_dict, filename):

	print(month_year_dict)
	#display_dict = dict()		# month-year --> [eng, hindi, bengali ....]
	f = open(filename, 'w')
	month_name = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
	w = csv.writer(f)
	#w.writerow(['Month-Year', language_map])
	w.writerow(['Month-Year', 'Language', 'Count'])
	#month_year_lang_dict = dict()
	month_year_list = []
	for key, val in month_year_dict.items():
		month_year_list.append((key[0], key[1]))

	# month_year_list = list(set(month_year_list))
	# #print(language_map)

	# for (a,b) in month_year_list:
	# 	display_freq = [0] * len(language_map)
	# 	for key, val in month_year_dict.items():
	# 		if(a==key[0] and b==key[1]):
	# 			#print(str(key[2]))
	# 			index = language_map.index(str(key[2]))
	# 			#print(index)
	# 			display_freq[index] = val

	# 	#print((a,b), display_freq)
	# 	writer = csv.writer(f)		
	# 	curr_name = month_name[int(a-1)] + "" + str(b) 
	# 	writer.writerow([curr_name, display_freq[0], display_freq[1], display_freq[2], display_freq[3], display_freq[4], display_freq[5], display_freq[6], display_freq[7], display_freq[8]])

	for key, val in month_year_dict.items():
		writer = csv.writer(f)
		curr_name = month_name[int(key[0])-1]
		writer.writerow([curr_name + str(key[1]), str(key[2]), val])

	f.close()	

def convert_data_csv_lang_categ(month_year_dict, filename):

	print(month_year_dict)
	f = open(filename, 'w')
	month_name = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
	w = csv.writer(f)
	w.writerow(['Month-Year', 'Language', 'Category', 'Count'])
	for key, val in month_year_dict.items():
		writer = csv.writer(f)
		curr_name = month_name[int(key[0])-1]
		writer.writerow([curr_name + str(key[1]), str(key[2]), str(key[3]), val])

	f.close()	


def like_count():
	all_data = UserVideoTypeDetails.objects.all()
	month_year_dict = dict()
	month_year_dict_uniq = dict()
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
				curr_like_count = val.likes_count

			language_str = language_map[int(lang_id)-1]	
			if((curr_month, curr_year, language_str) not in month_year_dict):
				month_year_dict[(curr_month, curr_year, language_str)] = []
			else:
				month_year_dict[(curr_month, curr_year, language_str)].append(curr_videoid)

	
	print(month_year_dict)
	for key, val in month_year_dict.items():
		month_year_dict_uniq[key] = len(set(val))

	convert_data_csv(month_year_dict_uniq, 'data_like.csv')

def share_count():
	all_data = UserVideoTypeDetails.objects.all()
	month_year_dict = dict()
	month_year_dict_uniq = dict()
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
				month_year_dict[(curr_month, curr_year, language_str)] = []
			else:
				month_year_dict[(curr_month, curr_year, language_str)].append(curr_videoid)

	
	#print(month_year_dict)
	for key, val in month_year_dict.items():
		month_year_dict_uniq[key] = len(set(val))

		
	convert_data_csv(month_year_dict_uniq, 'data_shared.csv')


def view_count():
	all_data = VideoPlaytime.objects.all()
	month_year_dict = dict()
	month_year_dict_uniq = dict()
	for item in all_data:
		curr_videoid = item.videoid
		curr_date = item.timestamp
		curr_month = curr_date.month
		curr_year = curr_date.year 
		lang_details = Topic.objects.all().filter(id=curr_videoid)
		for val in lang_details:
			lang_id = str(val.language_id)

		if(language_id.isdigit()):
			language_str = language_map[int(lang_id)-1]
		else:
			language_str = lang_id	
	
		if((curr_month, curr_year, language_str) not in month_year_dict):
			month_year_dict[(curr_month, curr_year, language_str)] = []
		else:
			month_year_dict[(curr_month, curr_year, language_str)].append(curr_videoid)

	for key, val in month_year_dict.items():
		month_year_dict_uniq[key] = len(set(val))

	print(month_year_dict_uniq)	
	


def comment_count():
	all_data = UserVideoTypeDetails.objects.all()
	month_year_dict = dict()
	month_year_dict_uniq = dict()
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
				curr_comment_count = val.comment_count

			language_str = language_map[int(lang_id)-1]	
			if((curr_month, curr_year, language_str) not in month_year_dict):
				month_year_dict[(curr_month, curr_year, language_str)] = []
			else:
				month_year_dict[(curr_month, curr_year, language_str)].append(curr_videoid)

	for key, val in month_year_dict.items():
		month_year_dict_uniq[key] = len(set(val))

	print(month_year_dict_uniq)	
	#print(month_year_dict)				
	convert_data_csv(month_year_dict_uniq, 'data_commented.csv')


# category name with total video count, language wise 
def lang_category_count():

	all_data = UserVideoTypeDetails.objects.all()
	month_year_dict = dict()
	month_year_dict_uniq = dict()
	for item in all_data:
		curr_videoid = item.videoid
		print(curr_videoid)
		curr_date = item.timestamp
		curr_month = curr_date.month
		curr_year = curr_date.year 
		lang_details = Topic.objects.all().filter(id = curr_videoid)
		for val in lang_details:
			lang_id = val.language_id
			curr_category = str(val.category)

		language_str = language_map[int(lang_id)-1]
		if((curr_month, curr_year, language_str, curr_category) not in month_year_dict):
			month_year_dict[(curr_month, curr_year, language_str, curr_category)] = []
		else:
			month_year_dict[(curr_month, curr_year, language_str, curr_category)].append(curr_videoid)

	for key, val in month_year_dict.items():
		month_year_dict_uniq[key] = len(set(val))

		
	convert_data_csv_lang_categ(month_year_dict_uniq, 'data_lang_category.csv')			 		

# videos created each month lang wise
def lang_video_count():

	all_data = UserVideoTypeDetails.objects.all()
	month_year_dict = dict()
	month_year_dict_uniq = dict()
	for item in all_data:
		curr_videoid = item.videoid
		curr_date = item.timestamp
		curr_month = curr_date.month
		curr_year = curr_date.year 
		lang_details = Topic.objects.all().filter(id = curr_videoid)
		for val in lang_details:
			lang_id = val.language_id

		language_str = language_map[int(lang_id)-1]
		if((curr_month, curr_year, language_str) not in month_year_dict):
			month_year_dict[(curr_month, curr_year, language_str)] = []
		else:
			month_year_dict[(curr_month, curr_year, language_str)].append(curr_videoid)

	
	for key, val in month_year_dict.items():
		month_year_dict_uniq[key] = len(set(val))

	print(month_year_dict_uniq)	
	convert_data_csv(month_year_dict_uniq, 'data_video_lang.csv')				


def main():
	# like_count()
	# share_count()
	# comment_count()
	# lang_category_count()
	# lang_video_count()
	view_count()


def run():
	main()
