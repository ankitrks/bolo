# script for evaluating the time difference between time to player ready, time to video play

from __future__ import division
from forum.user.models import AndroidLogs
# from forum.user.models import DeltaAndroidLogs
from forum.user.models import UserProfile
from forum.topic.models import Topic
import time
import datetime
import pytz
from datetime import datetime
from datetime import date 
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
import math


# global list recording the data accessed from the logs
complete_data = []
NUMBER_OF_DAYS=1


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
			print(data_iter)	
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
	import datetime
	uniq_video_records = {}
	net_details=[]
	countLogLenghth=len(log_text_dump)
	for j in range(countLogLenghth):
		record_j = log_text_dump[j]
		curr_stamp = record_j['miliseconds']
		curr_state = record_j['state']
		net_details = record_j['net_speed']
		curr_videoid = record_j['video_byte_id']
		device_model = record_j['device_model']
		manufacturer = record_j['manufacturer']

		video_triple = {}

		video_triple['ClickOnPlay'] = []
		video_triple['PlayerReady'] = []
		video_triple['StartPlayingcache'] = []
		video_triple['StartPlaying'] = []
		video_triple['StartPlayingcdn'] = []
		video_triple[curr_state]=curr_stamp
		video_triple['video_byte_id']=curr_videoid
		uniq_video_records[j] = video_triple 
	for key,val in uniq_video_records.items():
		v_id = val['video_byte_id']
		v_triplet = val
		if(len(val)>0):
			total_time_played=0
			player_list_sorted=0
			StartPlayingcache=0
			StartPlayingCDN=0
			start_list_sorted=0
			click_list_sorted=0
			if 'ClickOnPlay' in v_triplet:
				if(len(v_triplet['ClickOnPlay'])>0):
					clickOnTime=v_triplet['ClickOnPlay']
					milliseconds = int(clickOnTime)/1000.0
					click_list_sorted = datetime.datetime.fromtimestamp(milliseconds).strftime('%Y-%m-%d %H:%M:%S')

			if 'TimePlayed' in v_triplet:
				if(len(v_triplet['TimePlayed'])>0):
					total_time_played = v_triplet['TimePlayed']
			if 'PlayerReady' in v_triplet:
				if(len(v_triplet['PlayerReady'])>0):
					player_list_sorted = v_triplet['PlayerReady']
			if 'StartPlayingcdn' in v_triplet:
				if(len(v_triplet['StartPlayingcdn'])>0):
					StartPlayingCDN = v_triplet['StartPlayingcdn']
			if 'StartPlayingcache' in v_triplet:
				if(len(v_triplet['StartPlayingcache'])>0):
					StartPlayingcache = v_triplet['StartPlayingcache']
			if 'StartPlaying' in v_triplet:
				if(len(v_triplet['StartPlaying'])>0):
					start_list_sorted = v_triplet['StartPlaying']
			user_details = UserProfile.objects.get(user = userid)
			if(user_details.name):
				str_username = user_details.name
			else:
				str_username = user_details.user.username 	
			str_videotitle=""
			try:	
				video_details = Topic.objects.get(pk = v_id)
				str_videotitle = video_details.title
				str_videotitle = str_videotitle.replace(',', '')
			except Exception as e1:
				video_details=[]

			
			data_iter = []
			data_iter.append(str_username)
			data_iter.append(str_videotitle)
			data_iter.append(player_list_sorted)
			data_iter.append(total_time_played)
			data_iter.append(StartPlayingCDN)
			data_iter.append(StartPlayingcache)
			data_iter.append(start_list_sorted)
			data_iter.append(net_details)
			data_iter.append(device_model)
			data_iter.append(manufacturer)
			data_iter.append(click_list_sorted)
			data_iter = [str(i) for i in data_iter]
			if(len(data_iter)>0):
				complete_data.append(data_iter)
	
# func for writing data into csv
def write_csv():
	headers = ['User', 'Video title', 'Player Ready', 'Time Played','StartPlayingcdn','StartPlayingcache','StartPlaying', 'Network','Device Model','Manufacturer','Play Date Time']
        f_name = 'deltarecords.csv'
	with open(f_name, 'w') as f:
		writer = csv.writer(f)
		writer.writerow(headers)
		for each_data in complete_data:
			writer.writerow([x.encode('utf-8') for x in each_data])



# func for sending the csv created to the mail
def send_file_mail():
	emailfrom = "support@careeranna.com"
	emailto = "sarfaraz@careeranna.com"
	filetosend = os.getcwd() + "/deltarecords.csv"
	username = "support@careeranna.com"
	password = "$upp0rt@30!1"				# please do not use this()

	msg = MIMEMultipart()
	msg["From"] = emailfrom
	msg["To"] = emailto
	msg["Subject"] = "Bolo Indya: Weekly users buffering report date: " + str(datetime.now().date())
	msg.preamble = ""	
	attachment = open(filetosend, "rb") 
	file_stream = MIMEBase('application', 'octet-stream') 
	body = 'PFA the file'
	msg.attach(MIMEText(body, 'plain')) 
	file_stream.set_payload((attachment).read()) 
	encoders.encode_base64(file_stream) 
	file_stream.add_header('Content-Disposition', "attachment; filename= %s" % filetosend) 
	msg.attach(file_stream)
	server = smtplib.SMTP("smtp.gmail.com:587")
	server.starttls()
	server.login(username, password)
	server.sendmail(emailfrom, [emailto, 'ankit@careeranna.com', 'varun@careeranna.com', 'gitesh@careeranna.com' , 'maaz@careeranna.com',  'gaurang.s@boloindya.com', 'akash.u@boloindya.com'], msg.as_string())	
	server.quit()

def main():

	written_records= []
	curr_dttime = datetime.now()

	if NUMBER_OF_DAYS <7:
		curr_time = date.today() 
		yesterday = curr_time - timedelta(days = 1) 
		print(curr_time, yesterday, 'current and yesterday')
		# curr_time = '2020-06-20'
		# yesterday = '2020-06-19'

	android_logs = AndroidLogs.objects.filter(created_at__gte = yesterday, created_at__lte = curr_time)

	for each_android in android_logs:
		try:
			each_android_dump = ast.literal_eval(each_android.logs)
			#each_android_dump = each_android.logs
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