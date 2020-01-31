
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
import django
from datetime import timedelta
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )

# record the time taken for the videos to run
def record_duration_play(log_text_dump, userid):

	unique_video_play= []		# dict recording the freq of the videos played

	# try:
	# 	for i in range(0, len(log_text_dump)):
	# 		record_i = log_text_dump[i]
	# 		curr_stamp = float(record_i['miliseconds'])
	# 		curr_state = record_i.get('state')
	# 		curr_videoid = int(record_i.get('video_byte_id'))

	# 		# this will be used for reference time calculation
	# 		if(curr_state == 'ClickOnPlay'):
	# 			reference_time = datetime.utcfromtimestamp((curr_stamp)/ 1000).replace(tzinfo=pytz.utc)
	# 			#print(reference_time)


	# 		if(curr_videoid in unique_video_play and (curr_state == 'StartPlaying' or curr_state == 'ClickOnPause')):
	# 			unique_video_play[curr_videoid][curr_state].append(curr_stamp)
	# 		else:
	# 			video_tuple = {}
	# 			video_tuple['StartPlaying'] = []
	# 			video_tuple['ClickOnPause'] = []
	# 			if(curr_state == 'StartPlaying' or curr_state == 'ClickOnPause'):
	# 				video_tuple[curr_state].append(curr_stamp)
	# 				unique_video_play[curr_videoid] = video_tuple

	
	# 	for key, val in unique_video_play.items():
	# 		v_id = key
	# 		v_tuple = val 
	# 		if(len(v_tuple['StartPlaying']) > 0 and len(v_tuple['ClickOnPause'])> 0):

	# 			start_play_sorted = sorted(v_tuple['StartPlaying'])
	# 			pause_play_sorted = sorted(v_tuple['ClickOnPause'])
	# 			time_video_played = (pause_play_sorted[len(pause_play_sorted) - 1] - start_play_sorted[0]) / 1000
	# 			if(time_video_played<0):
	# 				time_video_played = 0
	# 			if(reference_time):				# duration of the video play
	# 				user_data_obj = VideoPlaytime(user = userid, videoid = v_id, playtime = time_video_played, timestamp = reference_time)
	# 				user_data_obj.save()

	# except Exception as e:
	# 	print('Exception 2' + str(e))	

	try:
		for i in range(0, len(log_text_dump)):
			record_i = log_text_dump[i]
			#curr_stamp = float(record_i['miliseconds'])
			curr_stamp = record_i['miliseconds']
			processed_stamp = parse_colon(curr_stamp)
			curr_state = record_i.get('state')
			curr_videoid = int(record_i.get('video_byte_id'))
			#print(curr_videoid, curr_state, processed_stamp)
			if(curr_state == 'StartPlayingcdn'):
				(vid, timestamp) = (curr_videoid, processed_stamp)
				unique_video_play.append((vid, timestamp))

				
		calc_playtime(unique_video_play, userid)		
		#print(unique_video_play)		


	except Exception as e:
		print('Exception 2' + str(e))		


# this method estimates the video play time for the records which do not have 'click on pause' time
# please note that this is just an estimate
# in some cases values may need to be mannually inspected
# def record_duration_play_estimate(log_text_dump, uniq_userid):
# 	#print(uniq_userid)
# 	try:
# 		for i in range(0, len(log_text_dump)):
# 			record_i = log_text_dump[i]
# 			curr_stamp = float(record_i['miliseconds'])
# 			curr_state = record_i.get('state')
# 			curr_videoid = int(record_i.get('video_byte_id'))
# 			#print(curr_state)
# 			if(curr_state == 'ClickOnPlay'):
# 				# reference time 
# 				ref_timestamp = datetime.utcfromtimestamp((curr_stamp)/ 1000).replace()
# 				#print(ref_timestamp)
# 				results = VideoDetails.objects.filter(userid = uniq_userid, timestamp__gt = ref_timestamp).order_by('timestamp')
# 				results_count = results.count()
# 				#print(results_count)
# 				if(results_count > 0):
# 					results_sorted = results[0]
# 					print(results_sorted.timestamp, ref_timestamp)
# 					upper_cap_timestamp = results_sorted.timestamp
# 					#print(upper_cap_timestamp)
# 					time_diff = upper_cap_timestamp - ref_timestamp
# 					#print(time_diff)
# 					print(time_diff.total_seconds())
# 					time_diff_hrs = (time_diff.total_seconds() / 3600)
# 					print(time_diff_hrs)
# 	except Exception as e:	
# 		print('Exception 3' + str(e)) 


def calc_playtime(unique_video_play, userid):

	try:
		for i in range(0, len(unique_video_play)-1):
			curr_vid = unique_video_play[i][0]
			next_vid = unique_video_play[i+1][0]
			if(curr_vid!=next_vid):
				ref_timestamp = datetime.utcfromtimestamp((float(unique_video_play[i][1]))/ 1000).replace()
				print(ref_timestamp)
				time_diff = float(unique_video_play[i+1][1]) - float(unique_video_play[i][1])
				#print(time_diff)
				time_diff  = (float(time_diff) / 1000)
				time_video_played = time_diff
				#print(time_video_played)
				#time_video_played = float(float(unique_video_play[i+1][1]) - float(unique_video_play[i][1])) /1000
				if(time_video_played<0):
					time_video_played = 0
				#print(curr_vid, time_video_played)
				user_data_obj = VideoPlaytime(user = userid, videoid = curr_vid, playtime = time_video_played, timestamp = ref_timestamp)
				user_data_obj.save()

	except Exception as e:
		print('Exception playtime' + str(e))


# method for parsing time when it has colon
def parse_colon(time):
 	dist_time = time.split(":")
 	if(len(dist_time)>1):
 		return dist_time[0] + "" + dist_time[1]
 	else:
 		return dist_time[0]	

# parse string duration of the video and return the time in second
def parse_duration(time):

	string_dist = time.split(":")
	mins = int(string_dist[0])
	seconds = int(string_dist[1])
	time = mins*60 + seconds
	return int(time)


# func responsible for finding the completetion rate of videos
def calculate_completetion_rate():

	today = datetime.now()
	# if(today.month>1):
	# 	last_month = today.month - 1
	# else:
	# 	last_month = 12 	

	# if(today.month > last_month):	
	# 	last_year = today.year
	# else:
	# 	last_year = today.year - 1	
	long_ago = today + timedelta(days = -90)
	video_records = VideoPlaytime.objects.filter(timestamp__gte = long_ago)  # fetch records of the last two months only
	for each_record in video_records:
		user_id = each_record.user
		video_id = each_record.videoid
		reference_time = each_record.timestamp  
		video_media_info = Topic.objects.get(is_vb = True, id = video_id)
		playtime_duration = each_record.playtime
		total_duration = parse_duration(video_media_info.media_duration)
		per_viewed = float(float(playtime_duration)/ float(total_duration)) * 100
		#print(playtime_duration, total_duration, per_viewed)
		#print(total_duration)
		if(per_viewed>=40.0):
			scaled_per_viewed = 100.0
		else:
			scaled_per_viewed = per_viewed
		#print(playtime_duration, total_duration, per_viewed, scaled_per_viewed)
		user_data_obj = VideoCompleteRate(user = user_id, videoid = video_id, duration = total_duration, playtime = playtime_duration, percentage_viewed= scaled_per_viewed, timestamp = reference_time)
		user_data_obj.save()		


# func responsible for finding the time spend by the user across various activities
def app_activity_time_spend():

	user_records = ActivityTimeSpend.objects.all()
	for each_record in user_records:
		user_id = each_record.user 
		fragment_id = each_record.fragmentid 
		user_activity_records = ActivityTimeSpend.objects.filter(user = user_id)
		tot_time = 0
		for each_activity_record in user_activity_records:
			tot_time+= each_activity_record.time_spent 

		#tot_time = ((float(tot_time) / 1000))
		tot_time = float(tot_time)
		print(tot_time)	
		existing_records = UserAppTimeSpend.objects.filter(user = user_id, total_time = tot_time).count()
		if(existing_records!=0):
			UserAppTimeSpend.objects.filter(user = user_id).update(total_time = tot_time)
		else:		
			user_data_obj = UserAppTimeSpend(user = user_id, total_time = tot_time)
			user_data_obj.save()


def main():
	android_logs = AndroidLogs.objects.filter(log_type = 'click2play')
	for each_log in android_logs:
		try:
			each_android_log_dump = ast.literal_eval(each_log.logs)
			#each_android_log_dump_id = each_log.user     # username
			each_android_userid = each_log.user_id       # user id corrosponding to the log
			#print(each_android_userid)
			#print(each_android_log_dump, each_android_log_dump_id) 
			record_duration_play(each_android_log_dump, each_android_userid)
			#record_duration_play_estimate(each_android_log_dump, each_android_userid)


		except Exception as e:
			print('Exception: 1' + str(e))


	#calculate_completetion_rate()
	#app_activity_time_spend()				#commented as of now, we will look into this later

def run():
	main()

