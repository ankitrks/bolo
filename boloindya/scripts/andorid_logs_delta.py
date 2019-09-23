# script for evaluating the time difference between time to player ready, time to video play

from __future__ import division
from forum.user.models import AndroidLogs
#from forum.user.models import DeltaAndroidLogs
from forum.user.models import UserProfile
from forum.topic.models import Topic
import time
import datetime
import pytz
from datetime import datetime
import ast
import csv
import os
local_tz = pytz.timezone("Asia/Kolkata")
from django.http import JsonResponse
from datetime import timedelta  


import smtplib
import mimetypes
from email.mime.multipart import MIMEMultipart
from email import encoders
from email.message import Message
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from django.utils import timezone

# global list recording the data accessed from the logs
complete_data = []


# func for extracting time the video takes to run(currently not used)
def extract_time_delta(log_text_dump, userid):
	#print("check_1")
	uniq_video_records = dict()		# dict recording id --> [click, ready, start]

	for i in range(0, len(log_text_dump)):
		record_i = log_text_dump[i]
		#print(record_i.keys())
		curr_stamp = int(record_i['miliseconds'])
		tstamp_a = curr_stamp
		curr_state = record_i.get('state')
		net_details = record_i.get('net_speed')
		curr_videoid = int(record_i.get('video_byte_id'))
		

		if(curr_videoid in uniq_video_records):
			if(len(uniq_video_records[curr_videoid]) == 1):
				if(curr_state == 'PlayerReady'):
					uniq_video_records[curr_videoid].append(tstamp_a)
			if(len(uniq_video_records[curr_videoid]) == 2):
				if(curr_state == 'StartPlaying'):
					uniq_video_records[curr_videoid].append(tstamp_a)
					uniq_video_records[curr_videoid].append(net_details)			
		else:
			if(curr_state == 'ClickOnPlay'):
				uniq_video_records[curr_videoid] = []
				uniq_video_records[curr_videoid].append(tstamp_a)
				#uniq_video_records['video_byte_id'] = []
				#uniq_video_records['video_byte_id'].append(tstamp_a)
			
	complete_data = []			
	#print(len(uniq_video_records))				
	for v_id, v_timeseries in uniq_video_records.items():
		if(len(v_timeseries) == 4):			# consider only videos where triplet occurs
			#print("here")
			delta1 = (v_timeseries[1] - v_timeseries[0]) / 1000
			delta2 = (v_timeseries[2] - v_timeseries[0]) / 1000
			#round_delta1 = "%.1f" % delta1
			#round_delta2 = "%.1f" % delta2
			round_delta1 = round(delta1, 1)
			round_delta2 = round(delta2, 1)
			#print(delta1, delta2, type(delta1), type(delta2))
			#print(userid, v_id, round_delta1, round_delta2)
			net_info = v_timeseries[3]
			
			user_details = UserProfile.objects.get(user = userid)
			if(user_details.name):
				str_username = user_details.name
			else:
				str_username = user_details.user.username 	
				
			video_details = Topic.objects.get(pk = v_id)
			str_videotitle = video_details.title
			#print(str_username, str_videotitle)
			data_iter = []
			data_iter.append(str_username)
			data_iter.append(str_videotitle)
			data_iter.append(round_delta1)
			data_iter.append(round_delta2)
			data_iter.append(net_info)
			#print(data_iter)	
			print(','.join(map(str,data_iter)))
			complete_data.append(data_iter)
			"""
			try:
				delta_obj = DeltaAndroidLogs(user = userid, videoid = v_id, timeplayerready = delta1, timeplay = delta2)
				delta_obj.save()
				print(delta_obj)
			except Exception as e:
				print(str(e))
			"""

# func for extractning the time the video takes to run(this one is used)
def extract_minmax_delta(log_text_dump, userid):

	uniq_video_records = {}
	for i in range(0, len(log_text_dump)):
		record_i = log_text_dump[i]
		#print(record_i)
		curr_stamp = int(record_i['miliseconds'])
		curr_state = record_i.get('state')
		net_details = record_i.get('net_speed')
		curr_videoid = int(record_i.get('video_byte_id'))

		if(curr_videoid in uniq_video_records):
			uniq_video_records[curr_videoid][curr_state].append(curr_stamp)
		else:
			video_triple = {}
			video_triple['ClickOnPlay'] = []
			video_triple['PlayerReady'] = []
			video_triple['StartPlaying'] = []
			video_triple[curr_state].append(curr_stamp)
			uniq_video_records[curr_videoid] = video_triple

	#print(uniq_video_records)
	for key, val in uniq_video_records.items():
		v_id = key
		v_triplet = val 
		if(len(v_triplet['ClickOnPlay'])>0 and len(v_triplet['PlayerReady'])>0 and len(v_triplet['StartPlaying'])> 0):

			#print(v_triplet['ClickOnPlay'], v_triplet['PlayerReady'], v_triplet['StartPlaying'], type(v_triplet['ClickOnPlay'][0]))
			click_list_sorted = sorted(v_triplet['ClickOnPlay'])
			player_list_sorted = sorted(v_triplet['PlayerReady'])
			start_list_sorted = sorted(v_triplet['StartPlaying'])

			#print(click_list_sorted, player_list_sorted, start_list_sorted, type(click_list_sorted))
			mintime_player_ready  = (player_list_sorted[0] - click_list_sorted[0]) / 1000
			maxtime_player_ready = (player_list_sorted[len(player_list_sorted)-1] - click_list_sorted[0]) / 1000
			mintime_start = (start_list_sorted[0] - click_list_sorted[0]) / 1000
			maxtime_start = (start_list_sorted[len(start_list_sorted)-1] - click_list_sorted[0]) / 1000
			delta_player_ready = maxtime_player_ready - mintime_player_ready
			delta_start = maxtime_start - mintime_start

			#print(mintime_player_ready, maxtime_player_ready, mintime_start, maxtime_start)
			user_details = UserProfile.objects.get(user = userid)
			if(user_details.name):
				str_username = user_details.name
			else:
				str_username = user_details.user.username 	
				
			video_details = Topic.objects.get(pk = v_id)
			str_videotitle = video_details.title
			str_videotitle = str_videotitle.replace(',', '')

			data_iter = []
			data_iter.append(str_username)
			data_iter.append(str_videotitle)
			data_iter.append(mintime_player_ready)
			#data_iter.append(maxtime_player_ready)
			#data_iter.append(delta_player_ready)
			data_iter.append(mintime_start)
			#data_iter.append(maxtime_start)
			#data_iter.append(delta_start)
			data_iter.append(net_details)
			data_iter = [str(i) for i in data_iter]
			#print(','.join(map(str,data_iter)))
			#print(data_iter)
			if(len(data_iter)>0):
				complete_data.append(data_iter)
		
# func for writing data into csv
def write_csv():
	print(len(complete_data))
	#headers = ['USERNAME', 'VIDEOTITLE', 'PLAYER READY(MIN)', 'PLAYER READY(MAX)', 'PLAYER READY(DELTA)', 'START PLAY(MIN)', 'START PLAY(MAX)', 'START PLAY(DELTA)', 'NETWORK']
	headers = ['User', 'Video title', 'Player Ready', 'Play Time', 'Network']
        f_name = 'deltarecords.csv'
	with open(f_name, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(headers)
		for each_data in complete_data:
			writer.writerow([x.encode('utf-8') for x in each_data])

# func for sending the csv created to the mail
def send_file_mail():
	emailfrom = "support@careeranna.com"
	emailto = "ankit@careeranna.com"
	filetosend = os.getcwd() + "/deltarecords.csv"
	username = "support@careeranna.com"
	password = "Support@3011"				# please do not use this()

	msg = MIMEMultipart()
	msg["From"] = emailfrom
	msg["To"] = emailto
	msg["Subject"] = "CSV file recording the time taken to run the videos on boloindya(last Mon to current Mon)"
	msg.preamble = ""

	ctype, encoding = mimetypes.guess_type(filetosend)
	if(ctype is None or encoding is not None):
		ctype = "application/octet-stream"

	maintype, subtype = ctype.split("/", 1)
	fp = open(filetosend, "rb")
	attachment = MIMEBase(maintype, subtype)
	attachment.set_payload(fp.read())
	fp.close()
	encoders.encode_base64(attachment)
	attachment.add_header("Content-Disposition", "attachment", filename = 'buffering-report-boloindya-' + str(datetime.now().date()))
	msg.attach(attachment)

	server = smtplib.SMTP("smtp.gmail.com:587")
	server.starttls()
	server.login(username, password)
	server.sendmail(emailfrom, [emailto, 'akash@careeranna.com'], msg.as_string())
	server.quit()


def main():

	written_records= []
	curr_dttime = datetime.now()
	some_day_last_week = timezone.now().date() - timedelta(days=7)
	monday_of_last_week = some_day_last_week - timedelta(days = (some_day_last_week.isocalendar()[2] - 1))
	monday_of_this_week = monday_of_last_week + timedelta(days = 7)

	# fetch recrods bw last monday and monday of this week
	android_logs = AndroidLogs.objects.filter(created_at__gte = monday_of_last_week, created_at__lte = monday_of_this_week)
	for each_android in android_logs:
		try:
			each_android_dump = ast.literal_eval(each_android.logs)
			#each_android_dump = each_android.logs
			#print(each_android_dump, type(each_android_dump))
			userid = each_android.user_id
			if(type(each_android_dump).__name__ == 'list'):
				# it is a nromal log
				#extract_time_delta(each_android_dump, userid)
				extract_minmax_delta(each_android_dump, userid)
		except Exception as e:
			count=0

	write_csv()
	send_file_mail()



def run():
	main()

