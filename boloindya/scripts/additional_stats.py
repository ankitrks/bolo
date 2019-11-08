from forum.user.models import AndroidLogs, VideoPlaytime, VideoCompleteRate, UserAppTimeSpend
from drf_spirit.models import UserJarvisDump, UserLogStatistics, ActivityTimeSpend, VideoDetails,UserTimeRecord
from forum.topic.models import Topic
import time
import ast 
from django.http import JsonResponse
import re
import datetime
from datetime import datetime
import os 
import pytz 
import dateutil.parser 
local_tz = pytz.timezone("Asia/Kolkata")
import sys
import ast
import csv
import os


import django
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )


complete_data = []
lang_categ_videofreq = {}


def report_stats():

	month_name = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	lang_categ_dict = {}			# dict recrording the unqiue language category pair

	try:
		all_video_playtime = VideoPlaytime.objects.all()
		for each_video in all_video_playtime:
			videoid = each_video.videoid
			video_details = Topic.objects.get(pk=videoid)
			video_strname = video_details.title
			userid = each_video.user 
			playtime = each_video.playtime 
			topic_based_data = Topic.objects.filter(id = videoid, is_vb = True)
			for each_topic_data in topic_based_data:
				categ_name = str(each_topic_data.category)
				lang_id = str(each_topic_data.language_id)

				if(each_topic_data.language_id == '1'):
					language_type = 'English'
				if(each_topic_data.language_id == '2'):
					language_type = 'Hindi'
				if(each_topic_data.language_id == '3'):
					language_type = 'Tamil'
				if(each_topic_data.language_id == '4'):
					language_type = 'Telgu'
				if(each_topic_data.language_id == '5'):
					language_type = 'Bengali'
				if(each_topic_data.language_id == '6'):
					language_type = 'Kannada'		

			playtime_count_details = VideoPlaytime.objects.filter(videoid = videoid)
			freq_playtime_count = len(playtime_count_details)
			user_count_details = VideoDetails.objects.filter(videoid = videoid)
			user_count = len(user_count_details)
			impression_details = VideoDetails.objects.filter(videoid = videoid)
			impression_count = len(impression_details)

			stats_list = []
			stats_list.append(freq_playtime_count)
			stats_list.append(user_count)
			stats_list.append(impression_count)

			if((categ_name, language_type) in lang_categ_dict):
				curr_data = lang_categ_dict[(categ_name, language_type)]
				curr_data[0]+= stats_list[0]
				curr_data[1]+= stats_list[1]
				curr_data[2]+= stats_list[2]
				lang_categ_dict[(categ_name, language_type)] = curr_data
			else:
				lang_categ_dict[(categ_name, language_type)] = stats_list

			
			if((categ_name, language_type) in lang_categ_videofreq):
				lang_categ_videofreq[(categ_name, language_type)]+=1
			else:
				lang_categ_videofreq[(categ_name, language_type)] = 1

								
	except Exception as e:
			print('except' + str(e))

			
	return lang_categ_dict			



def report_additional_stats():

	month_name = ['Jan', 'Feb', 'March', 'April', 'May', 'June', 'July', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
	try:
		all_video_playtime = VideoPlaytime.objects.all()
		for each_video in all_video_playtime:
			videoid = each_video.videoid 
			video_details = Topic.objects.get(pk = videoid)
			video_strname = video_details.title
			video_strname = video_strname.replace(',', '')


			userid = each_video.user 
			playtime = each_video.playtime 
			ref_timestamp = each_video.timestamp
			str_date = ref_timestamp.strftime("%m/%d/%Y, %H:%M:%S") 
			#print(ref_timestamp)
			#print(ref_timestamp.month)
			#print(month_name[int(ref_timestamp.month) - 1])
			topic_based_data = Topic.objects.filter(id = videoid, is_vb = True)
			#print(len(topic_based_data))
			for each_topic_data in topic_based_data:
				#print(each_topic_data.category)
				#print(each_topic_data.language_id)
				language_type =''
				if(each_topic_data.language_id == '1'):
					language_type = 'English'
				if(each_topic_data.language_id == '2'):
					language_type = 'Hindi'
				if(each_topic_data.language_id == '3'):
					language_type = 'Tamil'
				if(each_topic_data.language_id == '4'):
					language_type = 'Telgu'
				if(each_topic_data.language_id == '5'):
					language_type = 'Bengali'
				if(each_topic_data.language_id == '6'):
					language_type = 'Kannada'		

					
				#print(language_type)		
				#print(each_topic_data.m2mcategory)
				list_to_display = []
				#print("here")
				list_to_display.append(str(userid))
				#print("c1")
				list_to_display.append(video_strname)
				list_to_display.append(str(playtime))
				list_to_display.append(str(language_type))
				list_to_display.append(str(each_topic_data.category))
				list_to_display.append(str(month_name[int(ref_timestamp.month) - 1]))

				complete_data.append(list_to_display)

				#list_to_display.append(str(month_name[int(ref_timestamp.month) - 1]))
				#print(list_to_display[0], list_to_display[1], list_to_display[2], list_to_display[3], list_to_display[4])
				#print(len(list_to_display))
				#print(','.join(map(str, list_to_display)))
				#print(userid, videoid, playtime, language_type, str(each_topic_data.category), str_date], str(month_name[int(ref_timestamp.month) - 1])

			
	except Exception as e:
		#print('some exception' + str(e))	
		count = 0	

# not being used
def write_csv():
	print(len(complete_data))
	#headers = ['USERNAME', 'VIDEOTITLE', 'PLAYER READY(MIN)', 'PLAYER READY(MAX)', 'PLAYER READY(DELTA)', 'START PLAY(MIN)', 'START PLAY(MAX)', 'START PLAY(DELTA)', 'NETWORK']
	#headers = ['User', 'Video title', 'Player Ready', 'Play Time', 'Network']
	headers = ['Userid', 'VideoTitle', 'Playtime', 'Language', 'Video category', 'Month']
        f_name = 'add_records.csv'
	with open(f_name, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(headers)
		for each_data in complete_data:
			writer.writerow([x.encode('utf-8') for x in each_data])

def dump_csv(sample_dict):

	headers = ['Category', 'Language', 'Play Count', 'Contributers', 'Impression Count', 'Number of Videos']
	f_name = 'add_records.csv'

	for(a,b), val in sample_dict.items():
		list_print = []
		list_print.append(a)
		list_print.append(b)
		list_print.append(val[0])
		list_print.append(val[1])
		list_print.append(val[2])
		list_print.append(val[3])

		if(list_print[3] == 0):
			list_print[3] = list_print[5]
		if(list_print[4] == 0):
			list_print[4] = list_print[2]	

		print(','.join(map(str, list_print)))



def main():
	#report_additional_stats()
	dict_ret = report_stats()
	#print(dict_ret)
	#print(lang_categ_videofreq)
	for (a, b), val in dict_ret.items():
		stats_list = val 
		#print((a,b))
		uniq_video_count = lang_categ_videofreq[(a,b)]
		stats_list.append(uniq_video_count)

	dump_csv(dict_ret)	
	#print(dict_ret)		
	#write_csv()


def run():
	main()
