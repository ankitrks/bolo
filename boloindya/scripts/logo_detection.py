
# -*- coding: utf-8 -*-

from forum.topic.models import Topic
from google.cloud import vision
import io
import boto3
import time
import random
import os
import os, io
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from datetime import datetime,timedelta,date
from ffmpy import FFmpeg
from datetime import timedelta
from google.cloud import vision

from django.conf import settings
import operator
from ffmpy import FFmpeg
from forum.topic.models import Topic
from forum.user.models import UserProfile
from forum.topic.models import Notification
client = vision.ImageAnnotatorClient()
from ffmpy import FFmpeg
import sys
import urllib
import os
from shutil import copyfile

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

PROJECT_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# method for converting string to time
def timetostring(t):
	minute = 0
	seconds = 0
	if(t<10):
		minute = 0
		seconds = t 
		return '00'+':'+'0'+ str(seconds)
	elif(t>=60):
		minute = '01'
		seconds = t%60
		if(seconds < 10):
			seconds = '0' + str(seconds)
		else:
			seconds = str(seconds)
		return minute + ':' + seconds	
	else:
		return '00:' + str(t)			


def remove_redundant_files():
	os.remove(settings.BASE_DIR + '/temp/local_video.mp4')
	os.remove(settings.BASE_DIR + '/temp/output1.png')


# method to identify plagarised logos in videos uploaded
def identify_logo():
	
	plag_source = []
	plag_text_options = Topic.plag_text_options
	for (a,b) in plag_text_options:
		plag_source.append(str(b))

	f_name = settings.BASE_DIR + '/temp/plag_vid_details.txt'
	f = io.open(f_name, "w", encoding="UTF-8")
	today = datetime.today()
	try:
		#long_ago = today + timedelta(hours = -6)
		#topic_objects = Topic.objects.exclude(is_removed = True).filter(is_vb = True, date__gte = long_ago)
		topic_objects = Topic.objects.filter(is_removed=False, id__gt = 19417)
		global_counter = 1
		for item in topic_objects:
			iter_id = item.id
			data = Topic.objects.filter(id = iter_id)
			url = data[0].backup_url
			video_title = data[0].title
			url_str = url.encode('utf-8')
			test = urllib.FancyURLopener()
			test.retrieve(url_str, 'local_video.mp4')
			duration = data[0].media_duration 
			time = duration.split(":")
			minute = int(time[0]) * 60
			second = int(time[1])
			total_second = minute + second
			t1 = int(total_second / 5)
			t2 = t1 + t1
			t3 = t1 + t2
			#t4 = t1 + t3
			#t5 = t1 + t4
			t1 = '00:' + timetostring(t1)
			t2 = '00:' + timetostring(t2)
			t3 = '00:' + timetostring(t3)
			#t4 = '00:' + timetostring(t4)
			#t5 = '00:' + timetostring(t5)
			intervals = []
			intervals.append(t1)
			intervals.append(t2)
			intervals.append(t3)
			#intervals.append(t4)
			#intervals.append(t5)
			count = 1
			global_counter+=1

			for interval in intervals:
				ff = FFmpeg(inputs = {settings.BASE_DIR + '/temp/local_video.mp4': None}, outputs = {settings.BASE_DIR + "/temp/output{}.png".format(count): ['-y', '-ss', interval, '-vframes', '1']})
				ff.run()
				file_name = settings.BASE_DIR + '/temp/output{}.png'.format(count)
				with io.open(file_name, 'rb') as image_file:
					content = image_file.read()
					image = vision.types.Image(content = content)
					response = client.text_detection(image = image)
					texts = response.text_annotations
					for text in texts:
						modified_text = text.description
						if(modified_text in plag_source):
							f.write(iter_id + " " + video_title + " " + url_str + " " + (modified_text) + "\n")
							# Topic.objects.filter(id = iter_id).update(plag_text = str(plag_source.index(modified_text)))
							# Topic.objects.filter(id = iter_id).update(time_deleted = datetime.now())
							# data[0].delete()

	except Exception as e:
		print('' + str(e))
		pass 
		#print('' + str(e))  				
	f.close()
					

def main():
	identify_logo()
	#remove_redundant_files()


def run():
	main()

