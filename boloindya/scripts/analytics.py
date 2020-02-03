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


def convert_data_csv_view_count(month_year_dict, filename):

	print(month_year_dict)
	f = open(filename, 'w')
	month_name = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sept', 'Oct', 'Nov', 'Dec']
	w = csv.writer(f)
	w.writerow(['Month-Year', 'Language', 'Category', 'Duration(sec)'])
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
	month_year_dict_view = dict()
	for item in all_data:
		curr_videoid = item.videoid
		print(curr_videoid)
		curr_date = item.timestamp
		curr_month = curr_date.month
		curr_year = curr_date.year 
		lang_details = Topic.objects.get(id=curr_videoid)
		lang_id = str(lang_details.language_id)
		curr_category = lang_details.category

		# for val in lang_details:
		# 	lang_id = str(val.language_id)
		# 	curr_category = val.category

		print(lang_id)	
		if(lang_id.isdigit()):
			language_str = language_map[int(lang_id)-1]
		else:
			language_str = lang_id	
	
		if((curr_month, curr_year, language_str, curr_category) not in month_year_dict):
			month_year_dict[(curr_month, curr_year, language_str, curr_category)] = []
		else:
			month_year_dict[(curr_month, curr_year, language_str, curr_category)].append(curr_videoid)
		
	print(month_year_dict)		
	for key, val in month_year_dict.items():
		print("here")
		month_year_dict_uniq[key] = len(set(val))
		month_year_dict_view [key] = len(val)
	
	#print(month_year_dict_view)	
	#print(month_year_dict_uniq)
	#convert_data_csv(month_year_dict_view, 'data_views_total.csv')
	#convert_data_csv(month_year_dict_uniq, 'data_views_uniq.csv')
	convert_data_csv_lang_categ(month_year_dict_view, 'data_views_total.csv')


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
			lang_details = Topic.objects.all().filter(id = curr_videoid, is_vb = True)
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

	#print(month_year_dict_uniq)	
	convert_data_csv(month_year_dict_uniq, 'data_video_lang.csv')				

# total duration of views month wise, lang wise, cateog wise
def total_view_lang_categ():
	all_data = VideoPlaytime.objects.all()
	month_year_dict = dict()
	for item in all_data:
		curr_videoid = item.videoid
		print(curr_videoid)
		curr_date = item.timestamp
		curr_month = curr_date.month
		curr_year = curr_date.year
		lang_details = Topic.objects.all().filter(id = curr_videoid, is_vb = True)
		for val in lang_details:
			lang_id = val.language_id
			curr_category = str(val.category)

		playtime = item.playtime
		if(lang_id.isdigit()):
			language_str = 	language_map[int(lang_id)-1]
		else:
			language_str = lang_id

		if((curr_month, curr_year, language_str, curr_category) not in month_year_dict):
			month_year_dict[(curr_month, curr_year, language_str, curr_category)] = 0
		else:
			month_year_dict[(curr_month, curr_year, language_str, curr_category)]+=playtime

	#print(month_year_dict)
	convert_data_csv_view_count(month_year_dict, 'data_view_duration.csv')

			

def signup_login():

	header = ['UserID', 'UserName', 'Signup-Date'] + list(language_map)
	#print(header)
	df = pd.DataFrame()
	user_signup_dict = dict()
	signup_data = ReferralCodeUsed.objects.filter(by_user__isnull = False)
	for item in signup_data:
		curr_userid = item.by_user.id
		user_signup_dict[curr_userid] = item.created_at

	print(len(user_signup_dict))

	count = 0
	for key, val in user_signup_dict.items():
		curr_userid = key 
		all_data = Topic.objects.all().filter(user = curr_userid)
		user_lang_dict = dict()
		for lang in language_map:
			user_lang_dict[lang] = 0
	
		if(len(all_data)>0):
			count+=1	
			for item in all_data:
				if(item.language_id.isdigit()):
					user_lang_dict[language_map[int(item.language_id)-1]]+=1
				else:
					user_lang_dict[str(item.language_id)]+=1

			#print(user_lang_dict)
			user_details = UserProfile.objects.get(user = curr_userid)	
			if(user_details.name):
				curr_username = user_details.name
			else:
				curr_username = user_details.user.username

			#print(curr_userid, curr_username, user_signup_dict[curr_userid], user_lang_dict)
			str_date = str(user_signup_dict[curr_userid].day) + "-" + str(user_signup_dict[curr_userid].month) + "-" + str(user_signup_dict[curr_userid].year)
			#print(str_date) 
			row_data = {'UserID':curr_userid, 'UserName':curr_username, 'Signup-Date': str_date}
			row_data.update(user_lang_dict)	
			#row_data = [curr_userid, str(curr_username), str_date] + list(user_lang_dict.values())
			print(len(row_data), row_data)
			#print(row_data)
			df = df.append(row_data, ignore_index = True)

	df['Signup-Date'] = pd.to_datetime(df['Signup-Date'])		
	df = df.sort_values(by = 'Signup-Date', ascending = False)
	print(df.columns.values.tolist())
	print(df.head(100))
	df.to_csv('signup_data_creator.csv', encoding = 'utf-8', index = False)
	print(count)
		
		

def main():
	# like_count()
	# share_count()
	#comment_count()
	# lang_category_count()
	# lang_video_count()
	#view_count()
	total_view_lang_categ()
	signup_login()


def run():
	main()
