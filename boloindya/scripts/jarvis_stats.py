
from forum.user.models import AndroidLogs, VideoPlaytime, VideoCompleteRate
from drf_spirit.models import UserJarvisDump, UserLogStatistics
from forum.topic.models import Topic
import time
import ast 
from django.http import JsonResponse
import re
import datetime
import os 
import pytz 
import dateutil.parser 


local_tz = pytz.timezone("Asia/Kolkata")
import sys
import django
os.environ["DJANGO_SETTINGS_MODULE"] = "settings"
sys.path.append( '/'.join(os.path.realpath(__file__).split('/')[:5]) )


# record the time taken for the videos to run
def record_duration_play(log_text_dump, userid):

	unique_video_play= {}		# dict recording the freq of the videos played

	try:
		for i in range(0, len(log_text_dump)):
			record_i = log_text_dump[i]
			curr_stamp = int(record_i['miliseconds'])
			curr_state = record_i.get('state')
			curr_videoid = int(record_i.get('video_byte_id'))

			if(curr_videoid in unique_video_play and (curr_state == 'StartPlaying' or curr_state == 'ClickOnPause')):
				unique_video_play[curr_videoid][curr_state].append(curr_stamp)
			else:
				video_tuple = {}
				video_tuple['StartPlaying'] = []
				video_tuple['ClickOnPause'] = []
				if(curr_state == 'StartPlaying' or curr_state == 'ClickOnPause'):
					video_tuple[curr_state].append(curr_stamp)
					unique_video_play[curr_videoid] = video_tuple

	
		for key, val in unique_video_play.items():
			v_id = key
			v_tuple = val 
			if(len(v_tuple['StartPlaying']) > 0 and len(v_tuple['ClickOnPause'])> 0):

				start_play_sorted = sorted(v_tuple['StartPlaying'])
				pause_play_sorted = sorted(v_tuple['ClickOnPause'])
				time_video_played = (pause_play_sorted[len(pause_play_sorted) - 1] - start_play_sorted[0]) / 1000			# duration of the video play
				user_data_obj = VideoPlaytime(user = userid, videoid = v_id, playtime = time_video_played)
				user_data_obj.save()

	except Exception as e:
		print('Exception 2' + str(e))			

# parse string duration of the video and return the time in second
def parse_duration(time):

	string_dist = time.split(":")
	mins = int(string_dist[0])
	seconds = int(string_dist[1])
	time = mins*60 + seconds
	return int(time)



# model responsible for finding the completetion rate of videos
def calculate_completetion_rate():

	video_records = VideoPlaytime.objects.all()
	for each_record in video_records:
		user_id = each_record.user
		video_id = each_record.videoid 
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
		user_data_obj = VideoCompleteRate(user = user_id, videoid = video_id, duration = total_duration, playtime = playtime_duration, percentage_viewed= scaled_per_viewed)
		user_data_obj.save()		



def main():
	
	android_logs = AndroidLogs.objects.filter(log_type = 'click2play')
	for each_log in android_logs:
		try:
			each_android_log_dump = ast.literal_eval(each_log.logs)
			each_android_log_dump_id = each_log.user
			#print(each_android_log_dump, each_android_log_dump_id) 
			record_duration_play(each_android_log_dump, each_android_log_dump_id)

		except Exception as e:
			print('Exception: 1' + str(e))

	calculate_completetion_rate()			


def run():
	main()

